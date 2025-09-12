"""
DuckDuckGo Search Tool for South Park Script Generator

This module provides web search capabilities using DuckDuckGo's search API
through the ddgs library. It offers both news and general web search functionality
to help AI personas gather current information during brainstorming sessions.
"""

import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass

from ddgs import DDGS
from langchain_core.tools import tool


@dataclass
class SearchConfig:
    """Configuration for DuckDuckGo search operations."""
    region: str = "us-en"
    safesearch: str = "moderate"  # 'strict', 'moderate', 'off'
    max_results: int = 10
    timelimit: Optional[str] = None  # 'd' (day), 'w' (week), 'm' (month), 'y' (year)


class DuckDuckGoSearch:
    """
    DuckDuckGo search client for web and news searches.
    
    This class provides a convenient interface to DuckDuckGo's search API
    with proper error handling and result formatting.
    """
    
    def __init__(self, config: SearchConfig = None):
        self.config = config or SearchConfig()
        self.ddgs = DDGS()
    
    def search_web(
        self, 
        query: str, 
        max_results: int = None,
        region: str = None,
        safesearch: str = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a general web search using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            region: Search region (e.g., 'us-en', 'uk-en')
            safesearch: Safety filter ('strict', 'moderate', 'off')
            
        Returns:
            List of search results with title, snippet, url
        """
        try:
            search_params = {
                'region': region or self.config.region,
                'safesearch': safesearch or self.config.safesearch,
                'max_results': max_results or self.config.max_results
            }
            
            print(f"🔍 Searching web for: '{query}'")
            results = []
            
            for result in self.ddgs.text(query=query, **search_params):
                formatted_result = {
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', ''),
                    'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    'source': self._extract_domain(result.get('href', ''))
                }
                results.append(formatted_result)
            
            print(f"✅ Found {len(results)} web search results")
            return results
            
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            return []
    
    def search_news(
        self,
        query: str,
        max_results: int = None,
        region: str = None,
        safesearch: str = None,
        timelimit: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for recent news using DuckDuckGo News.
        
        Args:
            query: News search query
            max_results: Maximum number of results to return
            region: Search region (e.g., 'us-en', 'uk-en')
            safesearch: Safety filter ('strict', 'moderate', 'off')
            timelimit: Time limit ('d', 'w', 'm', 'y')
            
        Returns:
            List of news results with title, snippet, url, date, source
        """
        try:
            search_params = {
                'region': region or self.config.region,
                'safesearch': safesearch or self.config.safesearch,
                'max_results': max_results or self.config.max_results
            }
            
            if timelimit or self.config.timelimit:
                search_params['timelimit'] = timelimit or self.config.timelimit
            
            print(f"📰 Searching news for: '{query}'")
            results = []
            
            for result in self.ddgs.news(query=query, **search_params):
                formatted_result = {
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('url', ''),
                    'date': result.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d')),
                    'source': result.get('source', '')
                }
                results.append(formatted_result)
            
            print(f"✅ Found {len(results)} news results")
            return results
            
        except Exception as e:
            print(f"❌ News search failed: {e}")
            return []
    
    def search_images(
        self,
        query: str,
        max_results: int = None,
        region: str = None,
        safesearch: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for images using DuckDuckGo Images.
        
        Args:
            query: Image search query
            max_results: Maximum number of results to return
            region: Search region
            safesearch: Safety filter
            
        Returns:
            List of image results with title, url, thumbnail, source
        """
        try:
            search_params = {
                'region': region or self.config.region,
                'safesearch': safesearch or self.config.safesearch,
                'max_results': max_results or self.config.max_results
            }
            
            print(f"🖼️ Searching images for: '{query}'")
            results = []
            
            for result in self.ddgs.images(query=query, **search_params):
                formatted_result = {
                    'title': result.get('title', ''),
                    'url': result.get('image', ''),
                    'thumbnail': result.get('thumbnail', ''),
                    'source': result.get('source', ''),
                    'width': result.get('width', 0),
                    'height': result.get('height', 0)
                }
                results.append(formatted_result)
            
            print(f"✅ Found {len(results)} image results")
            return results
            
        except Exception as e:
            print(f"❌ Image search failed: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return 'Unknown'


# Global search instance for reuse
_search_instance = None


def get_ddg_search() -> DuckDuckGoSearch:
    """Get or create the global DuckDuckGo search instance."""
    global _search_instance
    
    if _search_instance is None:
        _search_instance = DuckDuckGoSearch()
    
    return _search_instance


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo for general information.
    
    Use this tool to find current information, facts, or context about any topic.
    Great for research during brainstorming sessions to get up-to-date information
    about current events, cultural phenomena, or background on topics.
    
    Args:
        query: What you want to search for (be specific for better results)
        max_results: Number of results to return (default: 5, max: 10)
        
    Returns:
        str: Formatted search results with titles, snippets, and URLs
    """
    try:
        search_client = get_ddg_search()
        
        # Limit max_results to reasonable bounds
        max_results = min(max(1, max_results), 10)
        
        results = search_client.search_web(query, max_results=max_results)
        
        if not results:
            return f"No web search results found for: {query}"
        
        # Format results for easy reading
        formatted_results = []
        for i, result in enumerate(results, 1):
            snippet = result['snippet'][:200] + "..." if len(result['snippet']) > 200 else result['snippet']
            
            formatted_results.append(
                f"**Result {i}: {result['title']}**\n"
                f"Source: {result['source']}\n"
                f"Summary: {snippet}\n"
                f"URL: {result['url']}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Web search error: {e}"


@tool
def search_news(query: str, max_results: int = 5, timeframe: str = "week") -> str:
    """
    Search for recent news using DuckDuckGo News.
    
    Use this tool to find current news articles and recent developments about topics.
    Perfect for getting up-to-date information about current events, trending topics,
    or recent developments that could inspire episode ideas.
    
    Args:
        query: News topic to search for
        max_results: Number of news articles to return (default: 5, max: 10)
        timeframe: How recent ('day', 'week', 'month', 'year')
        
    Returns:
        str: Formatted news results with headlines, summaries, dates, and sources
    """
    try:
        search_client = get_ddg_search()
        
        # Limit max_results to reasonable bounds
        max_results = min(max(1, max_results), 10)
        
        # Map timeframe to ddgs format
        timelimit_map = {
            'day': 'd',
            'week': 'w', 
            'month': 'm',
            'year': 'y'
        }
        timelimit = timelimit_map.get(timeframe.lower(), 'w')
        
        results = search_client.search_news(query, max_results=max_results, timelimit=timelimit)
        
        if not results:
            return f"No recent news found for: {query}"
        
        # Format results for easy reading
        formatted_results = []
        for i, result in enumerate(results, 1):
            snippet = result['snippet'][:250] + "..." if len(result['snippet']) > 250 else result['snippet']
            
            formatted_results.append(
                f"**News {i}: {result['title']}**\n"
                f"Source: {result['source']} | Date: {result['date']}\n"
                f"Summary: {snippet}\n"
                f"URL: {result['url']}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"News search error: {e}"


@tool 
def search_images(query: str, max_results: int = 3) -> str:
    """
    Search for images using DuckDuckGo Images.
    
    Use this tool to find visual references, inspiration, or examples related to topics.
    Can be helpful for understanding visual trends, getting inspiration for scenes,
    or finding reference material for cultural phenomena.
    
    Args:
        query: What images to search for
        max_results: Number of image results to return (default: 3, max: 5)
        
    Returns:
        str: Formatted image results with titles, dimensions, and URLs
    """
    try:
        search_client = get_ddg_search()
        
        # Limit max_results to reasonable bounds for images
        max_results = min(max(1, max_results), 5)
        
        results = search_client.search_images(query, max_results=max_results)
        
        if not results:
            return f"No images found for: {query}"
        
        # Format results for easy reading
        formatted_results = []
        for i, result in enumerate(results, 1):
            dimensions = ""
            if result['width'] and result['height']:
                dimensions = f" ({result['width']}x{result['height']})"
            
            formatted_results.append(
                f"**Image {i}: {result['title']}**{dimensions}\n"
                f"Source: {result['source']}\n"
                f"URL: {result['url']}\n"
                f"Thumbnail: {result['thumbnail']}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Image search error: {e}"


@tool
def search_trending_topics(region: str = "us-en") -> str:
    """
    Search for currently trending topics and breaking news.
    
    Use this tool to discover what's currently happening in the world,
    trending topics, or breaking news that could provide inspiration for episodes.
    
    Args:
        region: Region for trending topics (us-en, uk-en, etc.)
        
    Returns:
        str: Current trending topics and breaking news
    """
    try:
        search_client = get_ddg_search()
        
        # Search for trending/breaking news
        trending_queries = [
            "trending news today",
            "breaking news",
            "viral news today"
        ]
        
        all_results = []
        for trending_query in trending_queries:
            results = search_client.search_news(
                trending_query, 
                max_results=3, 
                timelimit='d',  # Today only
                region=region
            )
            all_results.extend(results)
        
        if not all_results:
            return "No trending topics found at this time."
        
        # Remove duplicates and format
        seen_titles = set()
        unique_results = []
        for result in all_results:
            if result['title'] not in seen_titles:
                seen_titles.add(result['title'])
                unique_results.append(result)
        
        # Format trending topics
        formatted_results = ["🔥 **TRENDING TOPICS TODAY:**\n"]
        for i, result in enumerate(unique_results[:8], 1):  # Top 8 trending
            snippet = result['snippet'][:150] + "..." if len(result['snippet']) > 150 else result['snippet']
            
            formatted_results.append(
                f"**{i}. {result['title']}**\n"
                f"Source: {result['source']}\n"
                f"Summary: {snippet}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Trending topics search error: {e}"


# Export all tools and classes
__all__ = [
    'DuckDuckGoSearch',
    'SearchConfig',
    'get_ddg_search',
    'search_web',
    'search_news', 
    'search_images',
    'search_trending_topics'
]
