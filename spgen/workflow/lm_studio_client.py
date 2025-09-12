"""LM Studio client for tool calling using native LM Studio SDK."""

import os
import json
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

try:
    import lmstudio as lms
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    print("⚠️  LM Studio SDK not available - falling back to OpenAI-compatible mode")


# ---------- Tool-call logging utilities (shared with llm_client.py) ----------

def log_tool_call(
    tool_name: str, tool_args: Dict[str, Any], tool_result: str, log_dir: Optional[str] = None
) -> None:
    """Log tool calls and responses to tool_calls.txt file."""
    if log_dir is None:
        log_dir = os.getcwd()

    tool_log_file = os.path.join(log_dir, "tool_calls.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
===============================================
TOOL CALL: {timestamp}
===============================================
Tool: {tool_name}
Args: {json.dumps(tool_args, indent=2, ensure_ascii=False)}
Result Length: {len(str(tool_result))} characters
Result Preview: {str(tool_result)[:200]}{"..." if len(str(tool_result)) > 200 else ""}

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
    if log_dir is None:
        log_dir = os.getcwd()

    analysis_log_file = os.path.join(log_dir, "llm_analysis.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format the analysis for better readability
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


def set_tool_log_dir(log_dir: str) -> None:
    """Set the global log directory for tool call logging."""
    global _current_log_dir
    _current_log_dir = log_dir


def get_tool_log_dir() -> str:
    """Get the current log directory for tool call logging."""
    return _current_log_dir or os.getcwd()

_last_tool_result: Optional[str] = None

def get_last_tool_result() -> Optional[str]:
    """Get the result of the last tool call."""
    return _last_tool_result

def set_last_tool_result(result: str) -> None:
    """Set the result of the last tool call."""
    global _last_tool_result
    _last_tool_result = result


_current_log_dir: Optional[str] = None


def _extract_usage_strings(result: Any) -> str:
    """Extract usage information from LM Studio result, similar to llm_client.py format."""
    usage_info = ""
    try:
        # LM Studio ActResult may have usage information in different places
        if hasattr(result, 'usage') and result.usage:
            u = result.usage
            if isinstance(u, dict):
                input_tokens = u.get('prompt_tokens', 0) or u.get('input_tokens', 0)
                output_tokens = u.get('completion_tokens', 0) or u.get('output_tokens', 0)
                total_tokens = u.get('total_tokens', 0) or (input_tokens + output_tokens)
                usage_info = f", Usage: input={input_tokens}, output={output_tokens}, total={total_tokens}"
                
                # Check for reasoning/thinking tokens
                thinking_tokens = (u.get('reasoning_tokens', 0) or 
                                 u.get('thinking_tokens', 0) or 
                                 u.get('total_reasoning_tokens', 0) or 0)
                if thinking_tokens > 0:
                    usage_info += f", thinking={thinking_tokens}"
        
        # Try to extract from metadata if available
        elif hasattr(result, 'metadata') and result.metadata:
            meta = result.metadata
            if isinstance(meta, dict) and 'usage' in meta:
                u = meta['usage']
                if isinstance(u, dict):
                    input_tokens = u.get('prompt_tokens', 0) or u.get('input_tokens', 0)
                    output_tokens = u.get('completion_tokens', 0) or u.get('output_tokens', 0)
                    total_tokens = u.get('total_tokens', 0) or (input_tokens + output_tokens)
                    usage_info = f", Usage: input={input_tokens}, output={output_tokens}, total={total_tokens}"
                    
                    thinking_tokens = (u.get('reasoning_tokens', 0) or 
                                     u.get('thinking_tokens', 0) or 
                                     u.get('total_reasoning_tokens', 0) or 0)
                    if thinking_tokens > 0:
                        usage_info += f", thinking={thinking_tokens}"
        
        # For simple response objects, check if they have content and estimate tokens
        elif hasattr(result, 'content') and result.content:
            # Rough token estimation (1 token ≈ 4 characters for English text)
            content_length = len(str(result.content))
            estimated_tokens = content_length // 4
            usage_info = f", Usage: estimated_total≈{estimated_tokens}"
            
    except Exception:
        pass
    
    return usage_info


def _extract_model_name_from_lmstudio(result: Any, default_model: str) -> str:
    """Extract model name from LM Studio result."""
    try:
        if hasattr(result, 'model') and result.model:
            return result.model
        elif hasattr(result, 'metadata') and result.metadata:
            meta = result.metadata
            if isinstance(meta, dict):
                return meta.get('model_name') or meta.get('model') or default_model
    except Exception:
        pass
    return default_model


def _extract_final_content(content: str, prompt: str = "") -> str:
    """
    Extract the final content from LM Studio response, handling reasoning channels.
    
    Some LM Studio models use reasoning channels like:
    <|channel|>analysis<|message|>thinking process<|end|><|start|>assistant<|channel|>final<|message|>actual answer
    
    Args:
        content: Raw response content
        prompt: Original prompt (for logging)
        
    Returns:
        Cleaned final content
    """
    if not content:
        return content
        
    analysis_content = ""
    final_content = content
    
    # Extract and log analysis content if present
    if '<|channel|>analysis<|message|>' in content:
        analysis_parts = content.split('<|channel|>analysis<|message|>')
        if len(analysis_parts) > 1:
            analysis_content = analysis_parts[1].split('<|end|>')[0].strip()
            if analysis_content:
                print("🧠 LLM Analysis/Reasoning:")
                print("-" * 50)
                # Format the analysis for better readability
                formatted_analysis = analysis_content.replace('. ', '.\n• ').replace('? ', '?\n• ')
                print(f"• {formatted_analysis}")
                print("-" * 50)
        
    # Handle reasoning channels - extract content after final channel marker
    if '<|channel|>final<|message|>' in content:
        parts = content.split('<|channel|>final<|message|>')
        if len(parts) > 1:
            final_content = parts[-1].strip()
    
    # Remove any remaining channel markers
    import re
    final_content = re.sub(r'<\|[^|]*\|>[^<]*', '', final_content).strip()
    
    # Log the analysis if we found any
    if analysis_content and prompt:
        log_llm_analysis(prompt, analysis_content, final_content, get_tool_log_dir())
    
    return final_content


def _convert_langchain_tool_to_lmstudio(tool: Any) -> Callable:
    """Convert a LangChain tool to LM Studio tool format (actual function)."""
    if not hasattr(tool, 'name') or not hasattr(tool, 'description'):
        raise ValueError(f"Tool {tool} is not a valid LangChain tool")

    # Get tool schema
    if hasattr(tool, 'args_schema') and tool.args_schema:
        schema = tool.args_schema.model_json_schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])
    else:
        # Fallback for tools without schema
        properties = {}
        required = []

    # Create a function with the EXACT signature that LM Studio expects
    param_names = list(properties.keys())
    
    # Generic function for other tools
    def generic_tool(**kwargs):
        """Generic tool function for LM Studio."""
        try:
            result = tool.invoke(kwargs)

            # Store the result for later retrieval
            set_last_tool_result(str(result))

            # Log the tool call
            log_tool_call(tool.name, kwargs, str(result), get_tool_log_dir())

            return str(result)
        except Exception as e:
            error_msg = f"Error: {e}"
            log_tool_call(tool.name, kwargs, error_msg, get_tool_log_dir())
            return error_msg

    # Set the function name to match the tool name
    generic_tool.__name__ = tool.name
    return generic_tool


def _execute_tool_call(tool_name: str, tool_args: Dict[str, Any], available_tools: List[Any]) -> str:
    """Execute a tool call and return the result."""
    for tool in available_tools:
        if getattr(tool, 'name', None) == tool_name:
            try:
                result = tool.invoke(tool_args)
                log_tool_call(tool_name, tool_args, str(result), get_tool_log_dir())
                return str(result)
            except Exception as e:
                err = f"Error: {e}"
                log_tool_call(tool_name, tool_args, err, get_tool_log_dir())
                return err

    return f"Error: Tool '{tool_name}' not found"


def llm_call_with_lmstudio(
    template: str,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    model_name: str = "default",
    **kwargs
) -> tuple[str, str]:
    """
    Call LLM using LM Studio SDK with tool calling support.

    Args:
        template: The prompt template
        temperature: Temperature for generation
        tools: List of LangChain tools to make available
        model_name: Name of the model to use (or "default")
        **kwargs: Additional arguments for template formatting

    Returns:
        tuple[str, str]: (content, model_name)
    """
    if not LMSTUDIO_AVAILABLE:
        raise RuntimeError("LM Studio SDK not available")

    # Format the template
    prompt = template.format(**kwargs)

    # Get the model
    if model_name == "default":
        # Try to get the first available model
        models = lms.list_loaded_models()
        if not models:
            raise RuntimeError("No models loaded in LM Studio. Please load a model first.")
        model = lms.llm(models[0].identifier)
        actual_model_name = models[0].identifier
    else:
        model = lms.llm(model_name)
        actual_model_name = model_name

    # Create config for temperature
    config = {"temperature": temperature} if temperature != 0.7 else None

    # If no tools, just do a simple chat
    if not tools:
        result = model.respond(prompt, config=config)
        content = str(result.content)
        # Parse response to extract final content from reasoning channels
        content = _extract_final_content(content, prompt)
        
        # Log usage information like llm_client.py
        usage_info = _extract_usage_strings(result)
        extracted_model_name = _extract_model_name_from_lmstudio(result, actual_model_name)
        print(f"📊 Model: {extracted_model_name}, Tool calls: 0{usage_info}")
        
        return content, extracted_model_name

    # Pass tools directly to LM Studio (assume they are already functions, not LangChain tools)
    lmstudio_tools = []
    for tool in tools:
        if callable(tool):
            # It's a direct function, use it as-is
            lmstudio_tools.append(tool)
        else:
            # It's a LangChain tool, convert it
            try:
                lmstudio_tools.append(_convert_langchain_tool_to_lmstudio(tool))
            except Exception as e:
                # Skip tools that can't be converted
                continue

    if not lmstudio_tools:
        # No valid tools found, fall back to simple chat
        result = model.respond(prompt, config=config)
        content = str(result.content)
        # Parse response to extract final content from reasoning channels
        content = _extract_final_content(content, prompt)
        
        # Log usage information like llm_client.py
        usage_info = _extract_usage_strings(result)
        extracted_model_name = _extract_model_name_from_lmstudio(result, actual_model_name)
        print(f"📊 Model: {extracted_model_name}, Tool calls: 0{usage_info}")
        
        return content, extracted_model_name

    try:
        # Use act method for tool execution
        result = model.act(
            chat=prompt,
            tools=lmstudio_tools,
            config=config
        )
        
        # Return a simple success message
        content = f"Tool executed successfully in {result.rounds} rounds."
        
        # Log usage information like llm_client.py
        usage_info = _extract_usage_strings(result)
        extracted_model_name = _extract_model_name_from_lmstudio(result, actual_model_name)
        tool_calls_count = max(0, result.rounds - 1) if hasattr(result, 'rounds') else 0
        print(f"📊 Model: {extracted_model_name}, Tool calls: {tool_calls_count}{usage_info}")
        
        return content.strip(), extracted_model_name
        
    except Exception as e:
        # Fallback to simple chat
        result = model.respond(prompt, config=config)
        content = str(result.content)
        
        # Parse response to extract final content from reasoning channels
        content = _extract_final_content(content, prompt)
        
        # Log usage information like llm_client.py
        usage_info = _extract_usage_strings(result)
        extracted_model_name = _extract_model_name_from_lmstudio(result, actual_model_name)
        print(f"📊 Model: {extracted_model_name}, Tool calls: 0{usage_info}")
        
        return content, extracted_model_name


def check_lmstudio_availability() -> bool:
    """Check if LM Studio is available and has loaded models."""
    if not LMSTUDIO_AVAILABLE:
        return False

    try:
        models = lms.list_loaded_models()
        return len(models) > 0
    except Exception:
        return False


def get_available_models() -> List[str]:
    """Get list of available models in LM Studio."""
    if not LMSTUDIO_AVAILABLE:
        return []

    try:
        models = lms.list_loaded_models()
        return [model.identifier for model in models]
    except Exception:
        return []
