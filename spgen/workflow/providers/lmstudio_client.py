import re
import codecs
from typing import Any, Callable, List, Optional, Tuple

import lmstudio as lms

from spgen.workflow.logging_utils import log_llm_analysis, log_tool_call, log_chat_message, get_tool_log_dir


class LMStudioWrapper:
    """Wrapper class for LMStudio SDK operations with logging and content processing."""
    
    def __init__(self):
        self.tool_calls_count = 0
        self.assistant_messages: List[str] = []
    
    def _extract_final_content_from_lmstudio(self, content: str, prompt: str) -> str:
        """
        Extract and clean final content from LMStudio response.
        
        Supports both gpt-oss-20b format (channel markers) and seed-oss-36b format (seed:think tags).
        
        Note: When using structured output (response_format), the 'parsed' attribute 
        contains structured data. For unstructured responses, 'parsed' is identical to 'content'.
        """
        analysis_content = ""
        final_content = content
        
        # Handle seed-oss-36b thinking tokens format
        if '<seed:think>' in content and '</seed:think>' in content:
            thinking_match = re.search(r'<seed:think>(.*?)</seed:think>', content, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1).strip()
                # Clean up budget reflection tokens
                thinking_content = re.sub(r'<seed:cot_budget_reflect>.*?</seed:cot_budget_reflect>', '', thinking_content, flags=re.DOTALL)
                thinking_content = thinking_content.strip()
                
                if thinking_content:
                    print("🧠 LLM Analysis/Reasoning (from Seed-OSS-36B):")
                    print("-" * 50)
                    print(f"• {thinking_content.replace('. ', '.\n• ')}")
                    print("-" * 50)
                    analysis_content = thinking_content
            
            # Extract final content after thinking tokens
            final_content = content.split('</seed:think>')[-1].strip()
            
        # Handle gpt-oss-20b channel format
        elif '<|channel|>analysis<|message|>' in content:
            parts = content.split('<|channel|>analysis<|message|>', 1)
            if len(parts) > 1:
                analysis_content = parts[1].split('<|end|>')[0].strip()
                if analysis_content:
                    print("🧠 LLM Analysis/Reasoning (from LM Studio):")
                    print("-" * 50)
                    print(f"• {analysis_content.replace('. ', '.\n• ')}")
                    print("-" * 50)
        
        # Extract final content if present (gpt-oss-20b format)
        if '<|channel|>final<|message|>' in content:
            final_content = content.split('<|channel|>final<|message|>')[-1].strip()
        
        # Clean up special tokens
        final_content = re.sub(r'<\|[^|]*\|>[^<]*', '', final_content).strip()
        
        # Clean up seed-oss-36b tokens
        final_content = re.sub(r'<seed:[^>]*>', '', final_content).strip()
        
        # Handle escape sequences
        final_content = self._unescape_content(final_content)
        
        # Log analysis if present
        if analysis_content:
            log_llm_analysis(prompt, analysis_content, final_content, get_tool_log_dir())
        
        return final_content
    
    def _extract_content_from_result(self, result) -> str:
        """
        Extract content from LMStudio result object, handling both structured and unstructured responses.
        
        For structured output (response_format), returns the structured data.
        For unstructured output, returns the parsed text content.
        """
        if hasattr(result, 'structured') and result.structured and hasattr(result, 'parsed'):
            # Structured output - parsed contains the structured data
            return str(result.parsed)
        elif hasattr(result, 'parsed'):
            # Unstructured output - parsed contains the raw text (same as content)
            return str(result.parsed)
        elif hasattr(result, 'content'):
            # Fallback to content
            return str(result.content)
        else:
            # For ActResult or other types without content/parsed
            return ""
    
    def _unescape_content(self, content: str) -> str:
        """Handle escape sequences in content."""
        # Handle common escape sequences manually to avoid encoding issues
        if "\\n" in content:
            content = content.replace("\\n", "\n")
        if "\\t" in content:
            content = content.replace("\\t", "\t")
        
        # Handle Unicode escape sequences like \u202f
        def replace_unicode_escape(match):
            try:
                return chr(int(match.group(1), 16))
            except (ValueError, OverflowError):
                return match.group(0)  # Return original if can't decode
        
        content = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode_escape, content)
        return content
    
    def _convert_langchain_tool_to_lmstudio(self, tool: Any) -> Callable:
        """Wrap a LangChain tool into an LM Studio SDK compatible function."""
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
    
    def _prepare_tools(self, tools: Optional[List[Any]]) -> List[Callable]:
        """Prepare tools for LMStudio SDK."""
        if not tools:
            return []
        
        lm_tools: List[Callable] = []
        for t in tools:
            if hasattr(t, 'invoke'):
                lm_tools.append(self._convert_langchain_tool_to_lmstudio(t))
            elif callable(t):
                # Ensure callable has a docstring
                if not getattr(t, '__doc__', None):
                    t.__doc__ = f"Tool {getattr(t, '__name__', 'tool')}"
                lm_tools.append(t)
        return lm_tools
    
    def _on_message(self, fragment, round_index=0):
        """Handle message fragments from LMStudio."""
        role = getattr(fragment, 'role', None)
        content = getattr(fragment, 'content', '') or ''
        log_chat_message(role or 'unknown', content, round_index, fragment, get_tool_log_dir())
        
        if role == 'assistant' and content:
            self.assistant_messages.append(str(content))
        elif role == 'tool':
            self.tool_calls_count += 1
    
    def _extract_usage_info(self, result) -> dict:
        """Extract usage information from LMStudio result object."""
        usage = {}
        
        # Debug: check what type of result we have
        result_type = type(result).__name__
        
        # Try different ways to get usage info
        if hasattr(result, 'usage') and result.usage:
            usage = result.usage
        elif hasattr(result, 'usage_metadata') and result.usage_metadata:
            usage = result.usage_metadata
        elif hasattr(result, 'response_metadata') and result.response_metadata:
            metadata = result.response_metadata
            if isinstance(metadata, dict):
                usage = metadata.get('token_usage', {}) or metadata.get('usage', {})
        elif hasattr(result, 'stats') and result.stats:
            # LMStudio stores usage in stats object (for PredictionResult)
            stats = result.stats
            usage = {
                'prompt_tokens': getattr(stats, 'prompt_tokens_count', 0),
                'completion_tokens': getattr(stats, 'predicted_tokens_count', 0),
                'total_tokens': getattr(stats, 'total_tokens_count', 0),
                'num_gpu_layers': getattr(stats, 'num_gpu_layers', -1),
                'time_to_first_token': getattr(stats, 'time_to_first_token_sec', 0),
                'tokens_per_second': getattr(stats, 'tokens_per_second', 0),
                'stop_reason': getattr(stats, 'stop_reason', 'unknown'),
                'accepted_draft_tokens': getattr(stats, 'accepted_draft_tokens_count', 0),
                'ignored_draft_tokens': getattr(stats, 'ignored_draft_tokens_count', 0),
                'rejected_draft_tokens': getattr(stats, 'rejected_draft_tokens_count', 0),
                'total_draft_tokens': getattr(stats, 'total_draft_tokens_count', 0)
            }
        
        # For ActResult, we don't have detailed usage stats, but we can estimate
        if not usage and hasattr(result, 'total_time_seconds'):
            print(f"🔍 Debug - {result_type} result: no detailed usage stats available")
            # ActResult typically doesn't provide detailed token usage
            # We could potentially estimate based on assistant_messages content
            if hasattr(self, 'assistant_messages') and self.assistant_messages:
                # Rough estimation based on message content length
                total_content = ''.join(str(msg) for msg in self.assistant_messages)
                estimated_tokens = len(total_content.split()) * 1.3  # rough token estimation
                usage = {
                    'prompt_tokens': 0,  # Unknown
                    'completion_tokens': int(estimated_tokens),
                    'total_tokens': int(estimated_tokens),
                    'total_time_seconds': getattr(result, 'total_time_seconds', 0)
                }
        
        return usage
    
    def _format_usage_info(self, usage: dict, model_name: str, tool_calls: int) -> str:
        """Format usage information for display."""
        if usage:
            # Basic token usage
            input_tokens = usage.get('prompt_tokens', usage.get('input_tokens', usage.get('input', 0)))
            output_tokens = usage.get('completion_tokens', usage.get('output_tokens', usage.get('output', 0)))
            total_tokens = usage.get('total_tokens', usage.get('total', input_tokens + output_tokens))
            
            # Performance metrics
            time_to_first_token = usage.get('time_to_first_token', 0)
            tokens_per_second = usage.get('tokens_per_second', 0)
            stop_reason = usage.get('stop_reason', 'unknown')
            total_time = usage.get('total_time_seconds', 0)
            
            # Draft token metrics (for speculative decoding)
            accepted_draft = usage.get('accepted_draft_tokens', 0) or 0
            ignored_draft = usage.get('ignored_draft_tokens', 0) or 0
            rejected_draft = usage.get('rejected_draft_tokens', 0) or 0
            total_draft = usage.get('total_draft_tokens', 0) or 0
            
            # Build usage string with core metrics
            usage_str = f", Usage: input={input_tokens}, output={output_tokens}, total={total_tokens}"
            
            # Add performance metrics if available
            if time_to_first_token and time_to_first_token > 0:
                usage_str += f", first_token={time_to_first_token:.3f}s"
            if tokens_per_second and tokens_per_second > 0:
                usage_str += f", speed={tokens_per_second:.1f} tok/s"
            elif total_time and total_time > 0 and output_tokens > 0:
                # Estimate speed for ActResult
                estimated_speed = output_tokens / total_time
                usage_str += f", speed≈{estimated_speed:.1f} tok/s (estimated)"
            if stop_reason and stop_reason != 'unknown':
                usage_str += f", stopped={stop_reason}"
            if total_time and total_time > 0:
                usage_str += f", total_time={total_time:.2f}s"
            
            # Add draft token info if available (speculative decoding)
            if total_draft and total_draft > 0:
                usage_str += f", draft_tokens={accepted_draft}/{total_draft} accepted"
        else:
            usage_str = ", Usage: not available"
        
        return f"📊 Model: {model_name}, Tool calls: {tool_calls}{usage_str}"
    
    def respond(self, prompt: str, model_name: str, temperature: float, thinking_budget: Optional[int] = None) -> Tuple[str, str]:
        """Make a simple response call to LMStudio."""
        model = lms.llm(model_name)
        
        # Reset state
        self.tool_calls_count = 0
        self.assistant_messages = []
        
        # Prepare config
        config = {"temperature": temperature}
        
        # Add thinking budget for seed-oss-36b models
        if thinking_budget is not None and "seed-oss" in model_name.lower():
            config["thinking_budget"] = thinking_budget
            print(f"🧮 Using thinking budget: {thinking_budget} tokens")
        
        result = model.respond(
            prompt,
            config=config,
            on_message=self._on_message,
            on_prompt_processing_progress=lambda progress: print(f"{progress * 100}% complete")
        )

        content = self._extract_final_content_from_lmstudio(self._extract_content_from_result(result), prompt)
        usage = self._extract_usage_info(result)
        print(self._format_usage_info(usage, model_name, 0))
        
        return content, model_name
    
    def act(self, prompt: str, model_name: str, temperature: float, tools: Optional[List[Any]], thinking_budget: Optional[int] = None) -> Tuple[str, str]:
        """Make an action call with tools to LMStudio."""
        model = lms.llm(model_name)
        lm_tools = self._prepare_tools(tools)

        # Reset state
        self.assistant_messages = []
        self.tool_calls_count = 0

        # Prepare config
        config = {"temperature": temperature}
        
        # Add thinking budget for seed-oss-36b models
        if thinking_budget is not None and "seed-oss" in model_name.lower():
            config["thinking_budget"] = thinking_budget
            print(f"🧮 Using thinking budget: {thinking_budget} tokens")

        chat = lms.Chat()
        chat.add_user_message(prompt)
        result = model.act(chat, lm_tools, on_message=self._on_message, config=config)

        final_raw = self.assistant_messages[-1] if self.assistant_messages else ''
        content = self._extract_final_content_from_lmstudio(final_raw, prompt) if final_raw else ''
        
        # Sanitize occasional trailing artifacts
        if content:
            content = re.sub(r"[\]\)\'\"]+$", "", content).strip()
        
        usage = self._extract_usage_info(result)
        tool_calls_count = self.tool_calls_count if self.tool_calls_count > 0 else max(0, getattr(result, 'rounds', 1) - 1)
        print(self._format_usage_info(usage, model_name, tool_calls_count))
        
        return content, model_name



def respond(prompt: str, model_name: str, temperature: float, thinking_budget: Optional[int] = None) -> Tuple[str, str]:
    """Backward compatibility function for simple responses."""
    return LMStudioWrapper().respond(prompt, model_name, temperature, thinking_budget)

def act(prompt: str, model_name: str, temperature: float, tools: Optional[List[Any]], thinking_budget: Optional[int] = None) -> Tuple[str, str]:
    """Backward compatibility function for tool-enabled responses."""
    return LMStudioWrapper().act(prompt, model_name, temperature, tools, thinking_budget)