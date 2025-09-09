# South Park Episode Generator - Test Suite

This directory contains comprehensive tests for the news research functionality and other components of the South Park episode generator.

## Test Structure

### News Research Tests (`test_news_research.py`)

**NewsResearchAgent Tests:**
- `test_news_agent_initialization` - Verifies agent initialization
- `test_search_news_success` - Tests successful news search with mocked DDGS
- `test_search_news_failure` - Tests error handling during news search
- `test_analyze_news_for_south_park_success` - Tests news analysis for South Park context
- `test_analyze_news_for_south_park_no_results` - Tests handling of empty news results
- `test_analyze_news_for_south_park_llm_failure` - Tests LLM failure handling
- `test_create_matt_stone_analysis` - Tests Matt Stone perspective generation
- `test_create_trey_parker_analysis` - Tests Trey Parker perspective generation
- `test_create_news_context_files` - Tests file creation and content
- `test_create_news_context_files_no_results` - Tests handling when no news found
- `test_generate_episode_prompt_from_news` - Tests dynamic prompt generation
- `test_generate_episode_prompt_no_trending_news` - Tests handling of no trending news

**News Research Node Tests:**
- `test_research_current_events_success` - Tests workflow node execution
- `test_research_current_events_state_modification` - Tests state updates

**Integration Tests:**
- `test_duplicate_removal_in_news_search` - Tests deduplication logic
- `test_error_handling_in_analysis_methods` - Tests error handling across all methods

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test File
```bash
python run_tests.py test_news_research
```

### Run Tests with Coverage
```bash
pytest --cov=workflow tests/
```

### Run Tests Matching Pattern
```bash
python run_tests.py -k "news"
```

### Run Only Unit Tests
```bash
python run_tests.py -m unit
```

## Test Features

### Mocking Strategy
- **DDGS Search**: Mocked to avoid real network calls during testing
- **LLM Calls**: Mocked to provide predictable responses and test error handling
- **File System**: Uses temporary directories for file creation tests

### Fixtures
- `news_agent`: Creates NewsResearchAgent instance
- `mock_news_results`: Provides sample news data
- `temp_log_dir`: Creates temporary directory for file operations
- `mock_episode_state`: Provides test episode state

### Error Testing
- Network failures during news search
- LLM timeout and error responses  
- File system permission issues
- Missing or invalid news results

### Integration Testing
- End-to-end workflow testing
- State modification verification
- File creation and content validation
- Duplicate removal logic

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (slower, may use real services)
- `@pytest.mark.slow` - Tests that take significant time
- `@pytest.mark.network` - Tests requiring network access

## Adding New Tests

When adding functionality to the news research system:

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test component interactions
3. **Error Cases**: Test failure scenarios and edge cases  
4. **Mock External Services**: Avoid real API calls in tests
5. **Use Fixtures**: Reuse common test data and setup
6. **Document Test Purpose**: Clear docstrings explaining what each test validates

## Performance Testing

For performance-critical operations:
```bash
pytest --durations=10 tests/  # Show 10 slowest tests
```

## Continuous Integration

These tests are designed to run in CI environments without external dependencies:
- All network calls are mocked
- File operations use temporary directories
- No API keys or credentials required