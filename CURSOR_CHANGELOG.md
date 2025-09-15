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
- **FIXED ANALYSIS/THINKING LOGGING REGRESSION**: Updated `spgen/workflow/llm_provider.py` to robustly parse and log analysis channels and thinking/reasoning token counts from both `usage_metadata` and `response_metadata.{token_usage|usage}` across non-tools and tools paths. Removed noisy debug prints and ensured final content strips LM Studio channel markers while logging analysis to `llm_analysis.txt`.
- **FIXED OVERRIDE LOGIC**: Corrected `llm_client.py` logic so that `override_use_lmstudio_sdk=False` properly forces OpenAI usage instead of falling through to other conditions.

### 2025-01-15

#### LMStudio Client Refactoring and Usage Information Enhancement
- **REFACTORED LMSTUDIO CLIENT**: Completely restructured `spgen/workflow/providers/lmstudio_client.py` from standalone functions to a clean `LMStudioWrapper` class with proper state management and method organization.
- **ENHANCED USAGE INFORMATION**: Fixed usage statistics extraction from LMStudio result objects. Now properly extracts comprehensive metrics including:
  - Basic token usage: `input=219, output=75, total=294`
  - Performance metrics: `first_token=0.531s, speed=41.4 tok/s`
  - Stop reason: `stopped=eosFound`
  - Draft token metrics for speculative decoding (when available)
- **IMPROVED CODE ORGANIZATION**: All functionality now contained within `LMStudioWrapper` class with methods:
  - `_extract_final_content_from_lmstudio()` - Content extraction and analysis
  - `_unescape_content()` - Escape sequence handling
  - `_extract_usage_info()` - Comprehensive usage data extraction
  - `_format_usage_info()` - Rich usage display formatting
  - `respond()` and `act()` - Main public methods
- **MAINTAINED BACKWARD COMPATIBILITY**: Exported `respond()` and `act()` functions that delegate to the wrapper class, ensuring existing code continues to work without changes.
- **FIXED UNICODE ESCAPE SEQUENCES**: Resolved logging issues with special characters (`\n`, `\u202f`) by implementing targeted escape sequence handling that avoids encoding problems.
- **ENHANCED CHAT MESSAGE LOGGING**: Added `log_chat_message()` function in `logging_utils.py` for consistent chat message logging with clean text extraction from `TextData` objects.
- **IMPROVED CONTENT EXTRACTION**: Added `_extract_content_from_result()` method to properly handle both structured and unstructured LMStudio responses. The `parsed` attribute contains structured data when using `response_format` with JSON schema, otherwise contains raw text identical to `content`. This prepares the client for future structured output usage while maintaining backward compatibility.
- **SEED-OSS-36B SUPPORT**: Added comprehensive support for seed-oss-36b model's thinking token format:
  - Handles `<seed:think>` and `</seed:think>` tags for reasoning content
  - Strips `<seed:cot_budget_reflect>` budget reflection tokens from analysis output
  - Supports `thinking_budget` parameter (multiples of 512 tokens) for controlling reasoning depth
  - Maintains backward compatibility with gpt-oss-20b channel marker format
  - Automatically detects model type and applies appropriate parsing logic
- **UPDATED TESTS**: Added thinking budget support to all test methods in `tests/test_lmstudio_client.py`. Tests now automatically use 512 token thinking budget for seed-oss models while maintaining backward compatibility with other models.


