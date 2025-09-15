from typing import Any, List, Optional, Tuple
import json

from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langchain_core.language_models import BaseChatModel

from spgen.workflow.logging_utils import log_tool_call, log_llm_analysis, get_tool_log_dir

def _extract_usage_strings(msg: Optional[BaseMessage]) -> str:
    if not msg:
        return ""
    usage_info = ""
    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
        u = msg.usage_metadata
        usage_info = f", Usage: input={u.get('input_tokens', 0)}, output={u.get('output_tokens', 0)}, total={u.get('total_tokens', 0)}"
        thinking = int((u.get('reasoning_tokens') or u.get('thinking_tokens') or 0) or 0)
        thinking = max(thinking, int(u.get('reasoning_input_tokens', 0) or 0) + int(u.get('reasoning_output_tokens', 0) or 0))
        if thinking > 0:
            usage_info += f", thinking={thinking}"
    elif hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
        rm = msg.response_metadata
        tu = rm.get('token_usage') or rm.get('usage') or {}
        usage_info = f", Usage: input={tu.get('prompt_tokens', 0)}, output={tu.get('completion_tokens', 0)}, total={tu.get('total_tokens', 0)}"
        thinking = int((tu.get('reasoning_tokens') or tu.get('thinking_tokens') or tu.get('total_reasoning_tokens') or 0) or 0)
        thinking = max(thinking, int(tu.get('reasoning_input_tokens', 0) or 0) + int(tu.get('reasoning_output_tokens', 0) or 0))
        if thinking > 0:
            usage_info += f", thinking={thinking}"
    return usage_info

def _extract_model_name(msg: Optional[BaseMessage], default_model: str) -> str:
    if msg and hasattr(msg, 'response_metadata') and isinstance(msg.response_metadata, dict):
        meta = msg.response_metadata
        return meta.get('model_name') or meta.get('model') or default_model
    return default_model

def respond(prompt: str, llm: BaseChatModel, model_name: str) -> Tuple[str, str]:
    response = llm.invoke([HumanMessage(content=prompt)])
    content = (response.content or '').strip()
    usage_info = _extract_usage_strings(response)
    actual_model_name = _extract_model_name(response, model_name)
    print(f"📊 Model: {actual_model_name}, Tool calls: 0{usage_info}")
    return content, actual_model_name

def act(prompt: str, llm: BaseChatModel, model_name: str, tools: List[Any]) -> Tuple[str, str]:
    llm_with_tools = llm.bind_tools(tools)
    messages: List[BaseMessage] = [HumanMessage(content=prompt)]
    while True:
        response = llm_with_tools.invoke(messages)
        tool_calls = getattr(response, 'tool_calls', [])
        if not tool_calls:
            content = (response.content or '').strip()
            if len(messages) > 1:
                # No provider analysis; log tool calls as the reasoning fallback
                all_tool_calls = []
                for m in messages:
                    if hasattr(m, 'tool_calls'):
                        all_tool_calls.extend(m.tool_calls)
                analysis = json.dumps(all_tool_calls, indent=2)
                log_llm_analysis(prompt, analysis, content, get_tool_log_dir())
            usage_info = _extract_usage_strings(response)
            actual_model_name = _extract_model_name(response, model_name)
            total_tool_calls = sum(len(getattr(m, 'tool_calls', [])) for m in messages)
            print(f"📊 Model: {actual_model_name}, Tool calls: {total_tool_calls}{usage_info}")
            return content, actual_model_name
        print(f"🔧 Model made {len(tool_calls)} tool call(s)")
        messages.append(response)
        for tc in tool_calls:
            tool_name = tc.get('name')
            tool_args = tc.get('args', {})
            tool_to_call = next((t for t in tools if getattr(t, 'name', '') == tool_name), None)
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
            messages.append(ToolMessage(content=str(result), tool_call_id=tc.get('id')))


