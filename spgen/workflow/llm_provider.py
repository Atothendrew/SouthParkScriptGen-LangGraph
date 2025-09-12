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

# --- Logging Utilities ---

_current_log_dir: Optional[str] = None

def set_tool_log_dir(log_dir: str) -> None:
    """Set the global log directory for tool call logging."""
    global _current_log_dir
    _current_log_dir = log_dir
    os.makedirs(log_dir, exist_ok=True)

def get_tool_log_dir() -> str:
    """Get the current log directory for tool call logging."""
    return _current_log_dir or os.getcwd()

def log_tool_call(
    tool_name: str, tool_args: Dict[str, Any], tool_result: str, log_dir: Optional[str] = None
) -> None:
    """Log tool calls and responses to tool_calls.txt file."""
    log_dir = log_dir or get_tool_log_dir()
    tool_log_file = os.path.join(log_dir, "tool_calls.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
===============================================
TOOL CALL: {timestamp}
===============================================
Tool: {tool_name}
Args: {json.dumps(tool_args, indent=2, ensure_ascii=False)}
Result Length: {len(str(tool_result))} characters
Result Preview: {str(tool_result)[:200]}{'...' if len(str(tool_result)) > 200 else ''}

Full Result:
{tool_result}
"""
    try:
        with open(tool_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"⚠️ Could not write to tool log file {tool_log_file}: {e}")

def log_llm_analysis(
    prompt: str, analysis: str, final_response: str, log_dir: Optional[str] = None
) -> None:
    """Log LLM analysis/reasoning to llm_analysis.txt file."""
    log_dir = log_dir or get_tool_log_dir()
    analysis_log_file = os.path.join(log_dir, "llm_analysis.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_analysis = analysis.replace('. ', '.\n\n').replace('? ', '?\n\n').replace(': ', ':\n  ')
    
    log_entry = f"""
===============================================
LLM ANALYSIS: {timestamp}
===============================================
PROMPT:
{'-' * 60}
{prompt}
{'-' * 60}
REASONING/ANALYSIS:
{'-' * 60}
{formatted_analysis}
{'-' * 60}
FINAL RESPONSE:
{'-' * 60}
{final_response}
{'-' * 60}
Analysis Length: {len(analysis)} characters
Response Length: {len(final_response)} characters
"""
    try:
        with open(analysis_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"📝 LLM analysis logged to: {analysis_log_file}")
    except Exception as e:
        print(f"⚠️ Could not write to analysis log file {analysis_log_file}: {e}")

# --- Optional Tools (RAG + DDG) ---

try:
    from spgen.tools.episode_rag import search_south_park_episodes
    episode_rag_available = True
except ImportError:
    episode_rag_available = False
    print("⚠️  Episode RAG system not available - continuing with basic tools")

try:
    from spgen.tools.duckduckgo_search import search_web, search_news, search_trending_topics
    ddg_tools_available = True
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
    if os.getenv("ANTHROPIC_API_KEY") and ANTHROPIC_AVAILABLE:
        return "anthropic", os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    if os.getenv("GOOGLE_API_KEY") and GOOGLE_AVAILABLE:
        return "google", os.getenv("GOOGLE_MODEL", "gemini-1.5-pro-latest")
    if os.getenv("OPENAI_API_KEY"):
        return "openai", os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    if LMSTUDIO_SDK_AVAILABLE:
        try:
            if lms.list_loaded_models():
                model_id = lms.list_loaded_models()[0].identifier
                return "lmstudio_sdk", model_id
        except Exception:
            pass  # Server might not be running
            
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
    """Extract token usage info from a LangChain message."""
    if not msg or not hasattr(msg, "usage_metadata") or not msg.usage_metadata:
        return ""
    
    u = msg.usage_metadata
    print(f"Usage metadata: {msg}")
    usage_info = f", Usage: input={u.get('input_tokens', 0)}, output={u.get('output_tokens', 0)}, total={u.get('total_tokens', 0)}"
    
    # Add reasoning/thinking tokens if available
    thinking_tokens = int(u.get("reasoning_tokens", 0) or u.get("thinking_tokens", 0) or 0)
    if thinking_tokens > 0:
        usage_info += f", thinking={thinking_tokens}"
        
    return usage_info

def _extract_model_name(msg: Optional[BaseMessage], default_model: str) -> str:
    """Extract model name from a LangChain message."""
    if msg and hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
        meta = msg.response_metadata
        return meta.get("model_name") or meta.get("model") or default_model
    return default_model

# --- LM Studio SDK Specific Logic ---

def _convert_langchain_tool_to_lmstudio(tool: Any) -> Callable:
    """Convert a LangChain tool to a function for the LM Studio SDK."""
    def sdk_tool(**kwargs):
        try:
            result = tool.invoke(kwargs)
            log_tool_call(tool.name, kwargs, str(result), get_tool_log_dir())
            return str(result)
        except Exception as e:
            error_msg = f"Error: {e}"
            log_tool_call(tool.name, kwargs, error_msg, get_tool_log_dir())
            return error_msg
    sdk_tool.__name__ = tool.name
    return sdk_tool

def _extract_final_content_from_lmstudio(content: str, prompt: str) -> str:
    """Extract final response from LM Studio's reasoning channel format."""
    analysis_content = ""
    final_content = content
    
    if '<|channel|>analysis<|message|>' in content:
        parts = content.split('<|channel|>analysis<|message|>', 1)
        if len(parts) > 1:
            analysis_content = parts[1].split('<|end|>')[0].strip()
            if analysis_content:
                print("🧠 LLM Analysis/Reasoning (from LM Studio):")
                print("-" * 50)
                print(f"• {analysis_content.replace('. ', '.\n• ')}")
                print("-" * 50)

    if '<|channel|>final<|message|>' in content:
        final_content = content.split('<|channel|>final<|message|>')[-1].strip()
    
    final_content = re.sub(r'<\|[^|]*\|>[^<]*', '', final_content).strip()
    
    if analysis_content:
        log_llm_analysis(prompt, analysis_content, final_content, get_tool_log_dir())
    
    return final_content

def _llm_call_with_lmstudio_sdk(
    prompt: str, temperature: float, tools: Optional[List[Any]], model_name: str, response_format: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """Handle LLM call using the native LM Studio SDK."""
    if not LMSTUDIO_SDK_AVAILABLE:
        raise RuntimeError("LM Studio SDK not available.")

    try:
        model = lms.llm(model_name)
    except Exception:
        models = lms.list_loaded_models()
        if not models:
            raise RuntimeError("No models loaded in LM Studio. Please load a model first.")
        model = lms.llm(models[0].identifier)
        model_name = models[0].identifier

    config = {"temperature": temperature}
    
    # Add response format if specified
    if response_format:
        config["response_format"] = response_format
    
    if not tools:
        result = model.respond(prompt, config=config)
        content = _extract_final_content_from_lmstudio(str(result.content), prompt)
        usage = getattr(result, 'usage', {})
        usage_str = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"
        print(f"📊 Model: {model_name}, Tool calls: 0{usage_str}")
        return content, model_name

    lmstudio_tools = []
    if tools:
        for tool in tools:
            if hasattr(tool, 'invoke') and callable(tool.invoke): # LangChain tool
                lmstudio_tools.append(_convert_langchain_tool_to_lmstudio(tool))
            elif callable(tool): # Regular function
                lmstudio_tools.append(tool)
    
    if not lmstudio_tools:
        return _llm_call_with_lmstudio_sdk(prompt, temperature, None, model_name)

    result = model.act(chat=prompt, tools=lmstudio_tools, config=config)
    content = f"Tool execution completed in {result.rounds} rounds."
    usage = getattr(result, 'usage', {})
    usage_str = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"
    tool_calls_count = max(0, result.rounds - 1)
    print(f"📊 Model: {model_name}, Tool calls: {tool_calls_count}{usage_str}")
    return content, model_name

# --- Main LLM Call Function ---

def llm_call(
    template: str,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    provider: Optional[LLMProvider] = "openai_compatible",
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

    # 2. Handle LM Studio SDK as a special case
    if provider == "lmstudio_sdk":
        try:
            return _llm_call_with_lmstudio_sdk(prompt, temperature, tools, model_name, response_format)
        except Exception as e:
            print(f"❌ LM Studio SDK call failed: {e}. Falling back to OpenAI-compatible mode.")
            provider = "openai_compatible"
            model_name = model or os.getenv("OPENAI_MODEL", "local-model")

    # 3. Standard LangChain provider logic
    try:
        llm = _build_llm_client(provider, model_name, temperature)
    except (ImportError, ValueError) as e:
        print(f"❌ Failed to build LLM client for {provider}: {e}")
        return f"Error: Could not initialize LLM provider '{provider}'.", "error-model"

    messages: List[BaseMessage] = [HumanMessage(content=prompt)]
    
    if not tools:
        response = llm.invoke(messages)
        content = (response.content or "").strip()
        usage_info = _extract_usage_strings(response)
        actual_model_name = _extract_model_name(response, model_name)
        print(f"📊 Model: {actual_model_name}, Tool calls: 0{usage_info}")
        return content, actual_model_name

    # 4. Tool-calling loop
    llm_with_tools = llm.bind_tools(tools)
    
    while True:
        response = llm_with_tools.invoke(messages)
        
        tool_calls = getattr(response, "tool_calls", [])
        if not tool_calls:
            # No more tool calls, we're done
            content = (response.content or "").strip()
            # Log analysis if there were any tool calls in previous steps
            if len(messages) > 1: # More than just the initial human message
                # Extract all reasoning content from the message history for the analysis log
                all_reasoning = "\n\n".join([
                    m.content for m in messages 
                    if hasattr(m, 'tool_calls') and m.content and isinstance(m.content, str)
                ])
                # If there was no reasoning content, fall back to logging the tool calls
                if not all_reasoning:
                    all_tool_calls = []
                    for m in messages:
                        if hasattr(m, 'tool_calls'):
                            all_tool_calls.extend(m.tool_calls)
                    analysis = json.dumps(all_tool_calls, indent=2)
                else:
                    analysis = all_reasoning
                log_llm_analysis(prompt, analysis, content, get_tool_log_dir())
            break

        print(f"🔧 Model made {len(tool_calls)} tool call(s)")
        messages.append(response)
        
        for tc in tool_calls:
            tool_name = tc.get("name")
            tool_args = tc.get("args", {})
            tool_to_call = next((t for t in tools if getattr(t, "name", "") == tool_name), None)
            
            if not tool_to_call:
                result = f"Error: Tool '{tool_name}' not found."
            else:
                try:
                    if hasattr(tool_to_call, 'invoke'):
                        result = tool_to_call.invoke(tool_args)
                    else:
                        result = tool_to_call(**tool_args)
                    preview = str(result)[:100] + ('...' if len(str(result)) > 100 else '')
                    print(f"✅ Executed {tool_name}: {preview}")
                except Exception as e:
                    result = f"Error executing tool {tool_name}: {e}"
                    print(f"❌ {result}")
            
            log_tool_call(tool_name, tool_args, str(result), get_tool_log_dir())
            messages.append(ToolMessage(content=str(result), tool_call_id=tc.get("id")))

    # After the loop, content is set from the last response without tool calls.
    usage_info = _extract_usage_strings(response)
    actual_model_name = _extract_model_name(response, model_name)
    total_tool_calls = sum(len(getattr(m, 'tool_calls', [])) for m in messages)
    print(f"📊 Model: {actual_model_name}, Tool calls: {total_tool_calls}{usage_info}")

    return content, actual_model_name

__all__ = [
    "llm_call",
    "get_available_tools",
    "log_tool_call",
    "set_tool_log_dir",
    "get_tool_log_dir",
    "get_default_llm_provider",
]
