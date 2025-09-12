"""
South Park Episode RAG (Retrieval Augmented Generation) Tool

Based on the LangGraph agentic RAG tutorial, this module provides semantic search
capabilities over South Park episode summaries to help personas reference 
historical content when brainstorming new episodes.

Reference: https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/
"""

import os
import glob
import yaml
from typing import List, Dict, Any, Literal, Optional
from pathlib import Path
from dataclasses import dataclass
from pydantic import BaseModel, Field

from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model


class EpisodeGrade(BaseModel):
    """Grade episodes using a binary score for relevance check."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )
    reasoning: str = Field(
        description="Brief explanation of why the episode is or isn't relevant"
    )


@dataclass 
class EpisodeRAGConfig:
    """Configuration for Episode RAG system."""
    episode_summaries_dir: str = "episode_summaries"
    chunk_size: int = 500
    chunk_overlap: int = 100
    embedding_model: str = "text-embedding-3-small"  # OpenAI embedding model
    retrieval_k: int = 5  # Number of documents to retrieve
    temperature: float = 0.0  # Temperature for grading model


class EpisodeRAG:
    """
    RAG system for South Park episodes using LangGraph agentic patterns.
    
    This class implements the core RAG functionality:
    1. Document preprocessing from YAML episode summaries
    2. Vector storage and semantic search
    3. Document relevance grading
    4. Retriever tool creation
    """
    
    def __init__(self, config: EpisodeRAGConfig = None):
        self.config = config or EpisodeRAGConfig()
        self.vectorstore = None
        self.retriever = None
        self.retriever_tool = None
        self.grader_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the embedding and grading models."""
        # Initialize grading model for document relevance assessment
        self.grader_model = init_chat_model("gpt-4o-mini", temperature=self.config.temperature)
        
    def preprocess_episodes(self) -> List[Document]:
        """
        Preprocess South Park episode YAML files into searchable documents.
        
        Converts structured YAML episode data into text chunks suitable for
        vector embedding and semantic search.
        
        Returns:
            List[Document]: Processed documents ready for embedding
        """
        documents = []
        
        # Get all episode YAML files
        episode_files = glob.glob(
            os.path.join(self.config.episode_summaries_dir, "s*.yaml")
        )
        
        for episode_file in episode_files:
            try:
                # Load YAML directly instead of using complex loader
                with open(episode_file, 'r', encoding='utf-8') as f:
                    episode_data = yaml.safe_load(f)
                
                # Convert episode data to searchable text
                episode_text = self._episode_data_to_text(episode_data)
                
                # Extract basic info safely
                basic_info = episode_data.get('basic_info', {})
                season = basic_info.get('season', 0)
                episode_number = basic_info.get('episode_number', 0)
                title = basic_info.get('title', 'Unknown')
                air_date = basic_info.get('original_air_date', 'Unknown')
                episode_type = basic_info.get('episode_type', 'unknown')
                
                # Create document with metadata
                doc = Document(
                    page_content=episode_text,
                    metadata={
                        "episode_id": f"s{season:02d}e{episode_number:02d}",
                        "title": title,
                        "season": season,
                        "episode_number": episode_number,
                        "air_date": str(air_date),
                        "episode_type": episode_type,
                        "source_file": episode_file,
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"Warning: Failed to load episode {episode_file}: {e}")
                continue
        
        # Split documents into chunks for better retrieval
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            length_function=len,
        )
        
        doc_splits = text_splitter.split_documents(documents)
        
        print(f"✅ Preprocessed {len(documents)} episodes into {len(doc_splits)} chunks")
        return doc_splits
    
    def _episode_data_to_text(self, episode_data: Dict[str, Any]) -> str:
        """
        Convert episode YAML data to searchable text.
        
        Args:
            episode_data: Raw episode data from YAML
            
        Returns:
            str: Formatted text representation of the episode
        """
        parts = []
        
        # Basic info
        basic_info = episode_data.get('basic_info', {})
        parts.append(f"Title: {basic_info.get('title', 'Unknown')}")
        parts.append(f"Season {basic_info.get('season', 0)}, Episode {basic_info.get('episode_number', 0)}")
        parts.append(f"Air Date: {basic_info.get('original_air_date', 'Unknown')}")
        parts.append(f"Type: {basic_info.get('episode_type', 'unknown')}")
        
        # Plot
        plot = episode_data.get('plot', {})
        if plot.get('logline'):
            parts.append(f"\nLogline: {plot['logline']}")
        if plot.get('plot_summary'):
            parts.append(f"\nPlot Summary:\n{plot['plot_summary']}")
        
        # Plot threads
        plot_threads = plot.get('plot_threads', [])
        if plot_threads:
            parts.append("\nPlot Threads:")
            for thread in plot_threads:
                parts.append(f"- {thread.get('title', 'Unknown')}: {thread.get('description', '')}")
                characters = thread.get('characters_involved', [])
                if characters:
                    parts.append(f"  Characters: {', '.join(characters)}")
        
        # Characters
        characters = episode_data.get('characters', {})
        main_chars = characters.get('main', [])
        if main_chars:
            char_names = [char.get('name', 'Unknown') for char in main_chars]
            parts.append(f"\nMain Characters: {', '.join(char_names)}")
        
        supporting_chars = characters.get('supporting', [])
        if supporting_chars:
            char_names = [char.get('name', 'Unknown') for char in supporting_chars]
            parts.append(f"Supporting Characters: {', '.join(char_names)}")
        
        # Content elements
        content = episode_data.get('content', {})
        
        # Cultural references
        cultural_refs = content.get('cultural_references', [])
        if cultural_refs:
            parts.append("\nCultural References:")
            for ref in cultural_refs:
                target = ref.get('target', 'Unknown')
                description = ref.get('description', '')
                parts.append(f"- {target}: {description}")
        
        # Running gags
        running_gags = content.get('running_gags', [])
        if running_gags:
            gag_names = [gag.get('name', 'Unknown') for gag in running_gags]
            parts.append(f"\nRunning Gags: {', '.join(gag_names)}")
        
        # Locations
        locations = content.get('locations', [])
        if locations:
            location_names = [loc.get('name', 'Unknown') for loc in locations]
            parts.append(f"Locations: {', '.join(location_names)}")
        
        # Themes
        themes = content.get('themes', [])
        if themes:
            theme_names = [theme.get('theme', 'Unknown') for theme in themes]
            parts.append(f"Themes: {', '.join(theme_names)}")
        
        # Continuity
        continuity = episode_data.get('continuity', {})
        callbacks = continuity.get('callbacks', [])
        if callbacks:
            parts.append(f"\nCallbacks: {', '.join(callbacks)}")
        
        setup_future = continuity.get('setup_for_future', [])
        if setup_future:
            parts.append(f"Setup for Future: {', '.join(setup_future)}")
        
        # Production notes
        production = episode_data.get('production', {})
        if production:
            notable_quotes = production.get('notable_quotes', [])
            if notable_quotes:
                parts.append(f"\nNotable Quotes: {'; '.join(notable_quotes[:3])}")  # Limit to first 3
        
        return "\n".join(parts)
    
    def create_vectorstore(self, documents: List[Document]) -> InMemoryVectorStore:
        """
        Create vector store from processed documents.
        
        Args:
            documents: List of processed documents
            
        Returns:
            InMemoryVectorStore: Vector store for semantic search
        """
        try:
            # Create embeddings
            embeddings = OpenAIEmbeddings(model=self.config.embedding_model)
            
            # Create vector store
            self.vectorstore = InMemoryVectorStore.from_documents(
                documents=documents, 
                embedding=embeddings
            )
            
            # Create retriever
            self.retriever = self.vectorstore.as_retriever(k=self.config.retrieval_k)
            
            print(f"✅ Created vector store with {len(documents)} document chunks")
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Failed to create vector store: {e}")
            raise
    
    def create_retriever_tool(self):
        """
        Create a retriever tool for use in LangGraph workflows.
        
        Returns:
            Tool: LangChain tool for episode retrieval
        """
        if not self.retriever:
            raise ValueError("Must create vectorstore before creating retriever tool")
        
        self.retriever_tool = create_retriever_tool(
            self.retriever,
            "search_south_park_episodes",
            "Search and return information about South Park episodes. "
            "Use this to find episodes with similar themes, characters, plotlines, "
            "or cultural references when brainstorming new episode ideas. "
            "The search understands context about characters, locations, running gags, "
            "and thematic elements across South Park's history."
        )
        
        return self.retriever_tool
    
    def grade_episode_relevance(
        self, 
        question: str, 
        episode_context: str
    ) -> Literal["relevant", "not_relevant"]:
        """
        Grade whether retrieved episode context is relevant to the question.
        
        Based on the LangGraph tutorial's document grading approach.
        
        Args:
            question: The original question/query
            episode_context: Retrieved episode content
            
        Returns:
            str: "relevant" or "not_relevant"
        """
        grade_prompt = f"""
        You are a grader assessing relevance of a South Park episode to a brainstorming question.

        Retrieved Episode Context:
        {episode_context}

        Brainstorming Question: {question}

        If the episode contains themes, characters, plotlines, cultural references, 
        or other elements that could inspire or inform the brainstorming question, 
        grade it as relevant.

        Consider relevance for:
        - Similar character dynamics or relationships
        - Comparable themes or social commentary
        - Related cultural references or parodies
        - Similar plot structures or conflicts
        - Useful character development patterns
        - Relevant running gags or callbacks

        Give a binary score 'yes' or 'no' to indicate whether the episode is relevant.
        """
        
        response = (
            self.grader_model
            .with_structured_output(EpisodeGrade)
            .invoke([{"role": "user", "content": grade_prompt}])
        )
        
        print(f"📊 Episode relevance grade: {response.binary_score} - {response.reasoning}")
        
        return "relevant" if response.binary_score == "yes" else "not_relevant"
    
    def rewrite_query(self, original_query: str) -> str:
        """
        Rewrite the query to improve episode search results.
        
        Args:
            original_query: The original brainstorming question
            
        Returns:
            str: Improved query for episode search
        """
        rewrite_prompt = f"""
        You are improving a search query for South Park episode content.

        Original query: {original_query}

        Rewrite this query to better search for relevant South Park episodes.
        Focus on:
        - Key themes and topics
        - Character names and relationships  
        - Social commentary themes
        - Cultural references or parodies
        - Plot elements or conflicts
        - Specific South Park concepts or running gags

        Make the query more specific and searchable while maintaining the original intent.

        Improved query:
        """
        
        response = self.grader_model.invoke([{"role": "user", "content": rewrite_prompt}])
        improved_query = response.content.strip()
        
        print(f"🔄 Query rewritten: '{original_query}' → '{improved_query}'")
        return improved_query
    
    def search_episodes(
        self, 
        query: str, 
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search episodes with automatic query improvement and relevance grading.
        
        Implements the agentic RAG pattern from the LangGraph tutorial.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: Relevant episode information
        """
        if not self.retriever_tool:
            raise ValueError("Must initialize RAG system before searching")
        
        max_results = max_results or self.config.retrieval_k
        
        # Initial search using the raw retriever (not the tool)
        initial_results = self.retriever.invoke(query)
        
        relevant_episodes = []
        
        # Grade each result for relevance
        for result in initial_results[:max_results]:
            grade = self.grade_episode_relevance(query, result.page_content)
            
            if grade == "relevant":
                relevant_episodes.append({
                    "content": result.page_content,
                    "metadata": result.metadata,
                    "relevance": "high"
                })
        
        # If no relevant results, try rewriting the query
        if not relevant_episodes:
            print("🔄 No relevant results found, rewriting query...")
            improved_query = self.rewrite_query(query)
            
            # Search again with improved query
            improved_results = self.retriever.invoke(improved_query)
            
            for result in improved_results[:max_results]:
                grade = self.grade_episode_relevance(query, result.page_content)
                
                if grade == "relevant":
                    relevant_episodes.append({
                        "content": result.page_content,
                        "metadata": result.metadata,
                        "relevance": "medium"
                    })
        
        print(f"✅ Found {len(relevant_episodes)} relevant episodes for query: '{query}'")
        return relevant_episodes
    
    def initialize(self) -> bool:
        """
        Initialize the complete RAG system.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            print("🚀 Initializing South Park Episode RAG system...")
            
            # 1. Preprocess episodes
            documents = self.preprocess_episodes()
            if not documents:
                print("❌ No episodes found to process")
                return False
            
            # 2. Create vectorstore
            self.create_vectorstore(documents)
            
            # 3. Create retriever tool
            self.create_retriever_tool()
            
            print("✅ Episode RAG system initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Episode RAG system: {e}")
            return False


# Global instance for use across the application
_episode_rag_instance = None


def get_episode_rag() -> EpisodeRAG:
    """Get or create the global Episode RAG instance."""
    global _episode_rag_instance
    
    if _episode_rag_instance is None:
        _episode_rag_instance = EpisodeRAG()
        
        # Try to initialize if not already done
        if not _episode_rag_instance.retriever_tool:
            success = _episode_rag_instance.initialize()
            if not success:
                print("⚠️  Episode RAG initialization failed, some features may be limited")
    
    return _episode_rag_instance


def initialize_episode_rag(config: EpisodeRAGConfig = None) -> bool:
    """
    Initialize the global Episode RAG system.
    
    Args:
        config: Optional configuration for the RAG system
        
    Returns:
        bool: True if initialization successful
    """
    global _episode_rag_instance
    
    _episode_rag_instance = EpisodeRAG(config)
    return _episode_rag_instance.initialize()


@tool
def search_south_park_episodes(query: str) -> str:
    """
    Search South Park episodes for reference material when brainstorming.
    
    This tool helps find relevant episodes based on themes, characters, 
    cultural references, or plot elements. Use it to:
    - Find episodes with similar themes or social commentary
    - Discover character development patterns
    - Reference existing running gags or callbacks
    - Find cultural references or parodies for inspiration
    
    Args:
        query: Description of what you're looking for (themes, characters, 
               cultural references, plot elements, etc.)
    
    Returns:
        str: Relevant episode information formatted for brainstorming context
    """
    try:
        rag_system = get_episode_rag()
        
        if not rag_system.retriever_tool:
            return "Episode RAG system not available. Please initialize first."
        
        results = rag_system.search_episodes(query, max_results=3)
        
        if not results:
            return f"No relevant South Park episodes found for: {query}"
        
        # Format results for brainstorming context
        formatted_results = []
        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            content_preview = result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
            
            formatted_results.append(
                f"**Episode {i}: {metadata.get('title', 'Unknown')}** "
                f"(S{metadata.get('season', '?')}E{metadata.get('episode_number', '?')})\n"
                f"{content_preview}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching episodes: {e}"


# Export main classes and functions
__all__ = [
    'EpisodeRAG',
    'EpisodeRAGConfig', 
    'EpisodeGrade',
    'get_episode_rag',
    'initialize_episode_rag',
    'search_south_park_episodes'
]
