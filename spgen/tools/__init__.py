"""
South Park Script Generator Tools

This module contains utility tools for the South Park Script Generator,
including:
- Episode RAG (Retrieval-Augmented Generation) system for querying episode summaries
- DuckDuckGo search tools for web search, news search, and trending topics
- Utility functions for maintaining episode continuity and research
"""

from .episode_rag import (
    EpisodeRAG,
    EpisodeRAGConfig,
    get_episode_rag,
    initialize_episode_rag,
    search_south_park_episodes,
)
from .duckduckgo_search import (
    DuckDuckGoSearch,
    SearchConfig,
    get_ddg_search,
    search_web,
    search_news,
    search_images,
    search_trending_topics,
)

__all__ = [
    "EpisodeRAG",
    "EpisodeRAGConfig",
    "get_episode_rag",
    "initialize_episode_rag",
    "search_south_park_episodes",
    "DuckDuckGoSearch",
    "SearchConfig",
    "get_ddg_search",
    "search_web",
    "search_news",
    "search_images",
    "search_trending_topics",
]
