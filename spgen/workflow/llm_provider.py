"""
Unified LLM client for South Park episode generation, supporting multiple providers.

This module provides a consolidated interface for making LLM calls, supporting:
- OpenAI
- Anthropic
- Google
- LM Studio (both via SDK and OpenAI-compatible server)

Provider Selection Logic:
1.  An explicit `provider` argument in `llm_call`.
2.  Environment variables, checked in this order:
    - `ANTHROPIC_API_KEY` -> Anthropic
    - `GOOGLE_API_KEY` -> Google
    - `OPENAI_API_KEY` -> OpenAI
3.  LM Studio SDK, if `lmstudio` is installed and a model is loaded.
4.  A fallback to an OpenAI-compatible endpoint (like an LM Studio server)
    at `LMSTUDIO_ENDPOINT`.

"""

import os
import json
import re
from typing import List, Optional, Dict, Any, Literal, Callable, Tuple
from datetime import datetime

from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langchain_core.language_models import BaseChatModel

# --- Provider Imports & Availability ---

# OpenAI
from langchain_openai import ChatOpenAI

# Anthropic
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Google
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# LM Studio SDK
try:
    import lmstudio as lms
    LMSTUDIO_SDK_AVAILABLE = True
except ImportError:
    LMSTUDIO_SDK_AVAILABLE = False

# --- Constants ---

LLMProvider = Literal["openai", "anthropic", "google", "lmstudio_sdk", "openai_compatible"]
LMSTUDIO_ENDPOINT = os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")

from spgen.workflow.logging_utils import (
    set_tool_log_dir,
    get_tool_log_dir,
    log_tool_call,
    log_llm_analysis,
)
from spgen.workflow.providers import lmstudio_client as lmclient
from spgen.workflow.providers import openai_client as oa

# --- Optional Tools (RAG + DDG) ---

try:
    from spgen.tools.episode_rag import search_south_park_episodes
    episode_rag_available = True
except ImportError:
    episode_rag_available = False
    print("⚠️  Episode RAG system not available - continuing with basic tools")

try:
    from spgen.tools.duckduckgo_search import search_web, search_news, search_trending_topics
    ddg_tools_available = False
except ImportError:
    ddg_tools_available = False
    print("⚠️  DuckDuckGo search tools not available - continuing without web search")

def get_available_tools() -> List[Any]:
    """Get list of available tools for LLM calls."""
    tools = []
    if episode_rag_available:
        tools.append(search_south_park_episodes)
    if ddg_tools_available:
        tools.extend([search_web, search_news, search_trending_topics])
    return tools

# --- Provider Detection and Client Building ---

def get_default_llm_provider() -> Tuple[LLMProvider, str]:
    """
    Automatically detect the best available LLM provider.
    Returns a tuple of (provider_name, model_name).
    """
    # Prefer LM Studio SDK if available and a model is loaded
    if LMSTUDIO_SDK_AVAILABLE:
        try:
            if lms.list_loaded_models():
                model_id = lms.list_loaded_models()[0].identifier
                return "lmstudio_sdk", model_id
        except Exception:
            pass  # Server might not be running
    
    # Otherwise, fall back to cloud providers
    if os.getenv("ANTHROPIC_API_KEY") and ANTHROPIC_AVAILABLE:
        return "anthropic", os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    if os.getenv("GOOGLE_API_KEY") and GOOGLE_AVAILABLE:
        return "google", os.getenv("GOOGLE_MODEL", "gemini-1.5-pro-latest")
    if os.getenv("OPENAI_API_KEY"):
        return "openai", os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    return "openai_compatible", os.getenv("OPENAI_MODEL", "local-model")

def _build_llm_client(provider: LLMProvider, model_name: str, temperature: float) -> BaseChatModel:
    """Build a LangChain chat client for the specified provider."""
    if provider == "anthropic":
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic SDK not found. Please run `pip install langchain-anthropic`.")
        return ChatAnthropic(model=model_name, temperature=temperature)
    
    if provider == "google":
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google GenAI SDK not found. Please run `pip install langchain-google-genai`.")
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, convert_system_message_to_human=True)

    if provider == "openai":
        return ChatOpenAI(model=model_name, temperature=temperature, api_key=os.getenv("OPENAI_API_KEY"))

    if provider == "openai_compatible":
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            base_url=LMSTUDIO_ENDPOINT,
            api_key="not-needed",
        )
    
    raise ValueError(f"Unsupported or unavailable LLM provider: {provider}")

# --- Response Parsing and Metrics ---

def _safe_tool_calls_len(msg: Optional[BaseMessage]) -> int:
    if not msg: return 0
    tc = getattr(msg, "tool_calls", [])
    return len(tc) if isinstance(tc, list) else 0

def _extract_usage_strings(msg: Optional[BaseMessage]) -> str:
    """Extract token usage info (including reasoning) from a LangChain message."""
    if not msg:
        return ""

    usage_info = ""

    # Primary: usage_metadata (LangChain standard)
    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
        u = msg.usage_metadata
        usage_info = f", Usage: input={u.get('input_tokens', 0)}, output={u.get('output_tokens', 0)}, total={u.get('total_tokens', 0)}"
        thinking = int(
            (u.get('reasoning_tokens') or u.get('thinking_tokens') or 0)
        )
        # Consider separate input/output reasoning token keys
        reasoning_in = int(u.get('reasoning_input_tokens', 0) or 0)
        reasoning_out = int(u.get('reasoning_output_tokens', 0) or 0)
        thinking = max(thinking, reasoning_in + reasoning_out)
        if thinking > 0:
            usage_info += f", thinking={thinking}"

    # Fallback: response_metadata.token_usage or response_metadata.usage
    elif hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
        rm = msg.response_metadata
        token_maps = []
        if isinstance(rm.get('token_usage'), dict):
            token_maps.append(rm['token_usage'])
        if isinstance(rm.get('usage'), dict):
            token_maps.append(rm['usage'])
        for tu in token_maps:
            if not usage_info:
                usage_info = f", Usage: input={tu.get('prompt_tokens', 0)}, output={tu.get('completion_tokens', 0)}, total={tu.get('total_tokens', 0)}"
            thinking = int(
                (tu.get('reasoning_tokens') or tu.get('thinking_tokens') or tu.get('total_reasoning_tokens') or 0)
            )
            reasoning_in = int(tu.get('reasoning_input_tokens', 0) or 0)
            reasoning_out = int(tu.get('reasoning_output_tokens', 0) or 0)
            thinking = max(thinking, reasoning_in + reasoning_out)
            if thinking > 0 and 'thinking=' not in usage_info:
                usage_info += f", thinking={thinking}"

    return usage_info

def _extract_model_name(msg: Optional[BaseMessage], default_model: str) -> str:
    """Extract model name from a LangChain message."""
    if msg and hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
        meta = msg.response_metadata
        return meta.get("model_name") or meta.get("model") or default_model
    return default_model

def _extract_final_content_from_lmstudio(content: str, prompt: str) -> str:
    return lmclient._extract_final_content_from_lmstudio(content, prompt)

def _llm_call_with_lmstudio_sdk(
    prompt: str, temperature: float, tools: Optional[List[Any]], model_name: str, response_format: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """Handle LLM call using the native LM Studio SDK."""
    if not LMSTUDIO_SDK_AVAILABLE:
        raise RuntimeError("LM Studio SDK not available.")

    # Route to lmstudio client helpers
    if not tools:
        return lmclient.respond(prompt, model_name, temperature)
    return lmclient.act(prompt, model_name, temperature, tools)

# --- Main LLM Call Function ---

def llm_call(
    template: str,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    response_format: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Tuple[str, str]:
    """
    Call an LLM with a unified interface, handling provider selection, tool calls, and logging.

    Args:
        template: The prompt template to format with kwargs.
        temperature: The generation temperature.
        tools: A list of LangChain tools to make available to the model.
        provider: Explicitly specify the provider to use. If None, auto-detects.
        model: Explicitly specify the model name. If None, uses provider's default.
        response_format: Optional structured output format specification.
        **kwargs: Arguments to format into the prompt template.

    Returns:
        A tuple of (final_content, model_name).
    """
    prompt = template.format(**kwargs)
    
    # 1. Determine provider and model
    if provider is None:
        detected_provider, default_model = get_default_llm_provider()
        provider = detected_provider
        model_name = model or default_model
        print(f"🤖 Auto-detected provider: {provider} (model: {model_name})")
    else:
        model_name = model or "default" # Let builder handle default for specified provider

    # 2. Handle LM Studio SDK as a special case (prefer when auto-detected)
    if provider == "lmstudio_sdk":
        try:
            return _llm_call_with_lmstudio_sdk(prompt, temperature, tools, model_name, response_format)
        except Exception as e:
            print(f"❌ LM Studio SDK call failed: {e}. Falling back to OpenAI-compatible mode.")
            provider = "openai_compatible"
            model_name = model or os.getenv("OPENAI_MODEL", "local-model")

    # 3. Standard LangChain provider logic routed to openai_client helpers
    try:
        llm = _build_llm_client(provider, model_name, temperature)
    except (ImportError, ValueError) as e:
        print(f"❌ Failed to build LLM client for {provider}: {e}")
        return f"Error: Could not initialize LLM provider '{provider}'.", "error-model"

    if not tools:
        return oa.respond(prompt, llm, model_name)
    return oa.act(prompt, llm, model_name, tools)

__all__ = [
    "llm_call",
    "get_available_tools",
    "log_tool_call",
    "set_tool_log_dir",
    "get_tool_log_dir",
    "get_default_llm_provider",
]
