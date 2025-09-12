### LLM Client behavior

- File: `spgen/workflow/llm_client.py`
- Primary API: `llm_call(template, temperature=0.7, tools=None, **kwargs) -> tuple[str, str]`
- Return value: `(content, model_name)` where `model_name` is now derived from the provider response metadata (prefers `response.response_metadata['model_name']` or `['model']`). If unavailable, it falls back to `OPENAI_MODEL`.
- Usage logging includes token counts and, when provided, reasoning/thinking tokens. We attempt to read: `usage_metadata.{reasoning_tokens|thinking_tokens|total_reasoning_tokens|reasoning_input_tokens+reasoning_output_tokens}` or `response_metadata.{token_usage|usage}.{...same keys...}`.
- The `model` sent to the provider is still taken from `OPENAI_MODEL` (default `gpt-4o-mini`), but the returned model name reflects the actual model that handled the request.
- When tools are enabled (requires `OPENAI_BASE_URL` and `OPENAI_API_KEY`, not LMStudio), tool calls are executed and logged to `<log_dir>/tool_calls.txt`. Set the directory with `set_tool_log_dir(dir)`.

### Endpoints

- If `OPENAI_BASE_URL` and `OPENAI_API_KEY` are set, calls use those. Otherwise, requests go to `LMSTUDIO_ENDPOINT` (env var, default `http://localhost:1234/v1`) with a dummy API key.

### Notes for contributors

- Prefer reading model name from `response.response_metadata` rather than environment variables when displaying or returning the model.
- `llm_call_with_model(...)` is an alias kept for backward compatibility and simply forwards to `llm_call`.


