import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

_current_log_dir: Optional[str] = None

def set_tool_log_dir(log_dir: str) -> None:
    global _current_log_dir
    _current_log_dir = log_dir
    os.makedirs(log_dir, exist_ok=True)

def get_tool_log_dir() -> str:
    return _current_log_dir or os.getcwd()

def log_tool_call(tool_name: str, tool_args: Dict[str, Any], tool_result: str, log_dir: Optional[str] = None) -> None:
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

def log_llm_analysis(prompt: str, analysis: str, final_response: str, log_dir: Optional[str] = None) -> None:
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


