import re
from typing import Any, Callable, List, Optional, Tuple

import lmstudio as lms

from spgen.workflow.logging_utils import log_llm_analysis, log_tool_call, get_tool_log_dir

def _extract_final_content_from_lmstudio(content: str, prompt: str) -> str:
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
    # Unescape common JSON-style escapes that may appear if message objects were stringified
    if "\\n" in final_content:
        final_content = final_content.replace("\\n", "\n")
    if "\\t" in final_content:
        final_content = final_content.replace("\\t", "\t")
    if analysis_content:
        log_llm_analysis(prompt, analysis_content, final_content, get_tool_log_dir())
    return final_content

def _convert_langchain_tool_to_lmstudio(tool: Any) -> Callable:
    """
    Wrap a LangChain tool into an LM Studio SDK compatible function.

    The returned function includes a docstring derived from the tool's
    name and description to satisfy LM Studio's tool schema extraction.
    """
    name = getattr(tool, 'name', 'tool')
    description = getattr(tool, 'description', None) or getattr(tool, '__doc__', '') or f"Tool {name}"

    def sdk_tool(**kwargs):
        """{description}"""
        try:
            result = tool.invoke(kwargs)
            log_tool_call(name, kwargs, str(result), get_tool_log_dir())
            return str(result)
        except Exception as e:
            error_msg = f"Error: {e}"
            log_tool_call(name, kwargs, error_msg, get_tool_log_dir())
            return error_msg
    sdk_tool.__name__ = name.replace('-', '_')
    return sdk_tool

def _prepare_tools(tools: Optional[List[Any]]) -> List[Callable]:
    if not tools:
        return []
    lm_tools: List[Callable] = []
    for t in tools:
        if hasattr(t, 'invoke'):
            lm_tools.append(_convert_langchain_tool_to_lmstudio(t))
        elif callable(t):
            # Ensure callable has a docstring
            if not getattr(t, '__doc__', None):
                t.__doc__ = f"Tool {getattr(t, '__name__', 'tool')}"
            lm_tools.append(t)
    return lm_tools

def respond(prompt: str, model_name: str, temperature: float) -> Tuple[str, str]:
    model = lms.llm(model_name)
    result = model.respond(prompt, config={"temperature": temperature})
    content = _extract_final_content_from_lmstudio(str(result.content), prompt)
    usage = getattr(result, 'usage', {})
    usage_str = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"
    print(f"📊 Model: {model_name}, Tool calls: 0{usage_str}")
    return content, model_name

def act(prompt: str, model_name: str, temperature: float, tools: Optional[List[Any]]) -> Tuple[str, str]:
    model = lms.llm(model_name)
    lm_tools = _prepare_tools(tools)

    assistant_messages: List[str] = []
    tool_calls_count = 0

    def _on_message(fragment, round_index=0):
        nonlocal tool_calls_count
        role = getattr(fragment, 'role', None)
        content = getattr(fragment, 'content', '') or ''
        if role == 'assistant' and content:
            assistant_messages.append(str(content))
        elif role == 'tool':
            tool_calls_count += 1

    chat = lms.Chat()
    chat.add_user_message(prompt)
    result = model.act(chat, lm_tools, on_message=_on_message, config={"temperature": temperature})

    final_raw = assistant_messages[-1] if assistant_messages else ''
    content = _extract_final_content_from_lmstudio(final_raw, prompt) if final_raw else ''
    # Sanitize occasional trailing artifacts like ")] or ']
    if content:
        content = re.sub(r"[\]\)\'\"]+$", "", content).strip()
    usage = getattr(result, 'usage', {})
    usage_str = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"
    if tool_calls_count == 0:
        tool_calls_count = max(0, getattr(result, 'rounds', 1) - 1)
    print(f"📊 Model: {model_name}, Tool calls: {tool_calls_count}{usage_str}")
    return content, model_name


