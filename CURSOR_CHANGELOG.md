### 2025-09-12

#### Episode Summary Creator Implementation
- **CREATED EPISODE SUMMARY CREATOR**: Built complete LangGraph workflow (`episodesummarycreator/`) for generating comprehensive South Park episode summaries using LLM knowledge instead of web search.
- **RESTRUCTURED WORKFLOW**: Implemented season-by-season approach: 1) Generate episode list per season, 2) Generate comprehensive episode summaries directly from LLM, 3) Save to organized season folders.
- **IMPLEMENTED PYDANTIC SCHEMAS**: Added proper structured output support using Pydantic models with LM Studio SDK's `response_format` parameter and `result.parsed` for guaranteed schema compliance.
- **ENHANCED LLM PROVIDER**: Updated `llm_call()` function in `spgen/workflow/llm_provider.py` to support `response_format` parameter for structured output, passing it through to LM Studio SDK properly.
- **ORGANIZED FILE STRUCTURE**: Episode summaries now saved in season-specific folders (`episode_summaries/1/`, `episode_summaries/2/`, etc.) with filename format `e01_episode_title.yaml`.
- **COMPREHENSIVE EPISODE SCHEMA**: Integrated full `EpisodeSummary` schema from `spgen/schemas/episode_summary.py` including plot analysis, character arcs, cultural references, themes, production details, and continuity tracking.

### 2025-09-12

- Updated `spgen/workflow/llm_client.py` to return the actual provider model name from the response metadata (prefers `model_name` or `model`) instead of echoing the `OPENAI_MODEL` env var. Console logging now also reflects the actual model. Fallback remains the env var when metadata is unavailable.
- Added logging of reasoning/thinking tokens where available by inspecting `usage_metadata` and `response_metadata.token_usage`/`usage` in both tool and non-tool paths.
- Added `--resume-from` to `spgen/cli.py`. Given a path to any file/dir under a previous run's `logs/.../<timestamp>/part_XX/`, the CLI infers the run, reads completion status from `process.txt`, reuses continuity data, and resumes the incomplete part or continues with subsequent parts under the same timestamp dir. It also regenerates the combined script if multipart.
- Added `--next-from` to `spgen/cli.py`. Given a path inside a previous run, it creates `part_{N+1}` under the same timestamp, builds a continuation prompt from continuity (last summary + unresolved plotlines), runs the workflow, updates continuity, and regenerates the combined script.
- **FIXED TOOL CALLING**: Resolved LM Studio SDK tool calling issues where tools were being called with empty arguments `{}`. Root cause was mismatch between LangChain `@tool` decorators and LM Studio expectations. Solution: converted smoke test to use plain Python functions with proper docstrings.
- **CLEANED UP LM STUDIO CLIENT**: Made `spgen/workflow/lm_studio_client.py` completely generic by removing all smoke test specific code, debug logging, and unused functions. Client now handles both direct Python functions and LangChain tools seamlessly.
- **SMOKE TEST SUCCESS**: Tool calling now works correctly - `add_numbers(2,3)=5`, `power_numbers(4,2)=16`, `multiply_numbers(5,16)=80`. Test exits with code 0.
- **ADDED LLM ANALYSIS LOGGING**: Created `log_llm_analysis()` function in LM Studio client to capture and log the model's reasoning process. When models use reasoning channels (`<|channel|>analysis<|message|>`), the analysis is now logged to `llm_analysis.txt` with formatted prompt, reasoning, and final response for easy debugging.
- **CREATED TOOL DECORATORS**: Added `tools/tool_decorators.py` with `@tool_logger` decorator for consistent logging and error handling across all tool functions. Simplifies tool code and ensures consistent output formatting.
- **ADDED TOKEN USAGE LOGGING**: Enhanced LM Studio client with consistent token usage logging matching `llm_client.py` format. Shows input/output/total/thinking tokens when available, with estimates when exact counts unavailable.
- **FIXED OVERRIDE LOGIC**: Corrected `llm_client.py` logic so that `override_use_lmstudio_sdk=False` properly forces OpenAI usage instead of falling through to other conditions.


