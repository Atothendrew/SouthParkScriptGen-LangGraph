# """
# Enhanced South Park Episode RAG (Retrieval-Augmented Generation) Tool
#
# This module provides an advanced question-answering system that uses embeddings
# and LLMs to retrieve and analyze information from the episode summaries database.
# It provides semantic search capabilities and natural language responses.
# """
#
# import os
# import json
# import pickle
# from typing import List, Dict, Any, Optional, Tuple
# from dataclasses import asdict
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# import openai
#
# from spgen.schemas import EpisodeDatabase, EpisodeSummary, EpisodeSummaryLoader
# from spgen.workflow.llm_client import llm_call, LLMClient
#
#
# class EpisodeRAGEnhanced:
#     """
#     Enhanced RAG system for answering questions about South Park episodes.
#
#     Uses embeddings for semantic search and LLMs for natural language responses.
#     """
#
#     def __init__(self,
#                  episodes_dir: str = "episode_summaries",
#                  embedding_model: str = "all-MiniLM-L6-v2",
#                  cache_dir: str = ".rag_cache"):
#         """Initialize the enhanced RAG system."""
#         self.db = EpisodeDatabase()
#         self.episodes_dir = episodes_dir
#         self.cache_dir = cache_dir
#         self.embedding_model_name = embedding_model
#
#         # Initialize components
#         self.embedding_model = None
#         self.llm_client = None
#         self.episode_embeddings = {}
#         self.episode_texts = {}
#
#         # Create cache directory
#         os.makedirs(cache_dir, exist_ok=True)
#
#         # Load episodes and initialize models
#         self._load_episodes()
#         self._initialize_models()
#         self._create_embeddings()
#
#     def _load_episodes(self):
#         """Load all episode YAML files into the database."""
#         if not os.path.exists(self.episodes_dir):
#             print(f"Warning: Episodes directory '{self.episodes_dir}' not found")
#             return
#
#         yaml_files = [f for f in os.listdir(self.episodes_dir) if f.endswith('.yaml')]
#
#         for yaml_file in yaml_files:
#             try:
#                 file_path = os.path.join(self.episodes_dir, yaml_file)
#                 episode = EpisodeSummaryLoader.load_from_yaml(file_path)
#                 self.db.add_episode(episode, save_to_file=False)
#             except Exception as e:
#                 print(f"Warning: Could not load {yaml_file}: {e}")
#
#         print(f"📺 Loaded {len(self.db.get_all_episodes())} episodes into enhanced RAG database")
#
#     def _initialize_models(self):
#         """Initialize embedding model and LLM client."""
#         try:
#             print("🤖 Loading embedding model...")
#             self.embedding_model = SentenceTransformer(self.embedding_model_name)
#             print(f"✅ Loaded embedding model: {self.embedding_model_name}")
#         except Exception as e:
#             print(f"❌ Failed to load embedding model: {e}")
#             print("📦 Installing sentence-transformers...")
#             os.system("uv add sentence-transformers scikit-learn")
#             try:
#                 self.embedding_model = SentenceTransformer(self.embedding_model_name)
#                 print(f"✅ Loaded embedding model: {self.embedding_model_name}")
#             except Exception as e2:
#                 print(f"❌ Still failed to load embedding model: {e2}")
#                 return
#
#         try:
#             print("🧠 Initializing LLM client...")
#             self.llm_client = LLMClient()
#             print("✅ LLM client initialized")
#         except Exception as e:
#             print(f"❌ Failed to initialize LLM client: {e}")
#
#     def _create_embeddings(self):
#         """Create embeddings for all episodes."""
#         if not self.embedding_model:
#             print("❌ Cannot create embeddings without embedding model")
#             return
#
#         embeddings_cache_file = os.path.join(self.cache_dir, "episode_embeddings.pkl")
#         texts_cache_file = os.path.join(self.cache_dir, "episode_texts.json")
#
#         # Check if cached embeddings exist
#         if os.path.exists(embeddings_cache_file) and os.path.exists(texts_cache_file):
#             try:
#                 print("📂 Loading cached embeddings...")
#                 with open(embeddings_cache_file, 'rb') as f:
#                     self.episode_embeddings = pickle.load(f)
#                 with open(texts_cache_file, 'r') as f:
#                     self.episode_texts = json.load(f)
#
#                 # Verify cache is up to date
#                 if len(self.episode_embeddings) == len(self.db.get_all_episodes()):
#                     print(f"✅ Loaded {len(self.episode_embeddings)} cached embeddings")
#                     return
#                 else:
#                     print("🔄 Cache outdated, regenerating embeddings...")
#             except Exception as e:
#                 print(f"❌ Failed to load cached embeddings: {e}")
#
#         print("🔄 Creating embeddings for episodes...")
#
#         for episode in self.db.get_all_episodes():
#             episode_id = f"s{episode.season:02d}e{episode.episode_number:02d}"
#
#             # Create comprehensive text representation of episode
#             episode_text = self._episode_to_text(episode)
#             self.episode_texts[episode_id] = episode_text
#
#             # Create embedding
#             try:
#                 embedding = self.embedding_model.encode(episode_text)
#                 self.episode_embeddings[episode_id] = embedding
#             except Exception as e:
#                 print(f"❌ Failed to create embedding for {episode_id}: {e}")
#
#         # Cache the embeddings
#         try:
#             with open(embeddings_cache_file, 'wb') as f:
#                 pickle.dump(self.episode_embeddings, f)
#             with open(texts_cache_file, 'w') as f:
#                 json.dump(self.episode_texts, f, indent=2)
#             print(f"💾 Cached {len(self.episode_embeddings)} embeddings")
#         except Exception as e:
#             print(f"❌ Failed to cache embeddings: {e}")
#
#         print(f"✅ Created embeddings for {len(self.episode_embeddings)} episodes")
#
#     def _episode_to_text(self, episode: EpisodeSummary) -> str:
#         """Convert episode summary to comprehensive text representation."""
#         text_parts = []
#
#         # Basic info
#         text_parts.append(f"Title: {episode.basic_info.title}")
#         text_parts.append(f"Season {episode.basic_info.season} Episode {episode.basic_info.episode}")
#         text_parts.append(f"Air date: {episode.basic_info.air_date}")
#         text_parts.append(f"Episode type: {episode.basic_info.episode_type.value}")
#
#         # Plot
#         text_parts.append(f"Main storyline: {episode.plot.main_storyline}")
#         if episode.plot.subplot:
#             text_parts.append(f"Subplot: {episode.plot.subplot}")
#         text_parts.append(f"Resolution: {episode.plot.resolution}")
#         text_parts.append(f"Episode arc: {episode.plot.episode_arc}")
#
#         # Characters
#         main_chars = [f"{c.name} ({c.role.value}): {c.description}"
#                      for c in episode.characters.main_characters]
#         text_parts.append(f"Main characters: {'; '.join(main_chars)}")
#
#         supporting_chars = [f"{c.name} ({c.role.value}): {c.description}"
#                            for c in episode.characters.supporting_characters]
#         if supporting_chars:
#             text_parts.append(f"Supporting characters: {'; '.join(supporting_chars)}")
#
#         # Content elements
#         text_parts.append(f"Violence level: {episode.content_elements.violence_level}")
#         text_parts.append(f"Language: {episode.content_elements.language}")
#         text_parts.append(f"Adult themes: {', '.join(episode.content_elements.adult_themes)}")
#
#         # Cultural references
#         refs = [f"{ref.reference}: {ref.context}"
#                 for ref in episode.content_elements.cultural_references]
#         if refs:
#             text_parts.append(f"Cultural references: {'; '.join(refs)}")
#
#         # Themes
#         text_parts.append(f"Primary themes: {', '.join(episode.themes.primary_themes)}")
#         text_parts.append(f"Social commentary: {'; '.join(episode.themes.social_commentary)}")
#
#         # Continuity
#         if episode.continuity.character_introductions:
#             text_parts.append(f"Character introductions: {', '.join(episode.continuity.character_introductions)}")
#
#         running_gags = [f"{gag.gag}: {gag.description}"
#                        for gag in episode.continuity.running_gags]
#         if running_gags:
#             text_parts.append(f"Running gags: {'; '.join(running_gags)}")
#
#         if episode.continuity.plot_connections:
#             text_parts.append(f"Plot connections: {'; '.join(episode.continuity.plot_connections)}")
#
#         # Locations
#         locations = [f"{loc.name}: {loc.description}"
#                     for loc in episode.locations.primary_locations]
#         if locations:
#             text_parts.append(f"Locations: {'; '.join(locations)}")
#
#         # Production notes
#         text_parts.append(f"Writer: {episode.production_notes.writer}")
#         text_parts.append(f"Director: {episode.production_notes.director}")
#         if episode.production_notes.notable_aspects:
#             text_parts.append(f"Notable aspects: {', '.join(episode.production_notes.notable_aspects)}")
#
#         # Cultural impact
#         text_parts.append(f"Significance: {episode.cultural_impact.significance}")
#         if episode.cultural_impact.controversy:
#             text_parts.append(f"Controversy: {episode.cultural_impact.controversy}")
#         text_parts.append(f"Legacy: {episode.cultural_impact.legacy}")
#
#         return " ".join(text_parts)
#
#     def ask(self, question: str, top_k: int = 3) -> str:
#         """
#         Answer a question using semantic search and LLM generation.
#
#         Args:
#             question: Natural language question about episodes
#             top_k: Number of most relevant episodes to retrieve
#
#         Returns:
#             Natural language answer generated by LLM
#         """
#         if not self.embedding_model or not self.llm_client:
#             return "❌ RAG system not properly initialized. Missing embedding model or LLM client."
#
#         if not self.episode_embeddings:
#             return "❌ No episode embeddings available."
#
#         try:
#             # Get relevant episodes using semantic search
#             relevant_episodes = self._semantic_search(question, top_k)
#
#             if not relevant_episodes:
#                 return "❌ No relevant episodes found for your question."
#
#             # Generate response using LLM
#             response = self._generate_response(question, relevant_episodes)
#
#             return response
#
#         except Exception as e:
#             return f"❌ Error processing question: {e}"
#
#     def _semantic_search(self, query: str, top_k: int) -> List[Tuple[EpisodeSummary, float]]:
#         """Perform semantic search to find most relevant episodes."""
#         try:
#             # Create embedding for the query
#             query_embedding = self.embedding_model.encode(query)
#
#             # Calculate similarities
#             similarities = []
#             for episode_id, episode_embedding in self.episode_embeddings.items():
#                 similarity = cosine_similarity(
#                     query_embedding.reshape(1, -1),
#                     episode_embedding.reshape(1, -1)
#                 )[0][0]
#
#                 # Find corresponding episode
#                 season, episode_num = int(episode_id[1:3]), int(episode_id[4:6])
#                 episode = self.db.get_episode(season, episode_num)
#
#                 if episode:
#                     similarities.append((episode, similarity))
#
#             # Sort by similarity and return top_k
#             similarities.sort(key=lambda x: x[1], reverse=True)
#             return similarities[:top_k]
#
#         except Exception as e:
#             print(f"❌ Error in semantic search: {e}")
#             return []
#
#     def _generate_response(self, question: str, relevant_episodes: List[Tuple[EpisodeSummary, float]]) -> str:
#         """Generate natural language response using LLM."""
#         try:
#             # Prepare context from relevant episodes
#             context_parts = []
#             for i, (episode, similarity) in enumerate(relevant_episodes, 1):
#                 context_parts.append(f"""
# Episode {i}: {episode.basic_info.title} (S{episode.basic_info.season:02d}E{episode.basic_info.episode:02d})
# - Plot: {episode.plot.main_storyline}
# - Characters: {', '.join([c.name for c in episode.characters.main_characters])}
# - Themes: {', '.join(episode.themes.primary_themes)}
# - Cultural References: {', '.join([ref.reference for ref in episode.content_elements.cultural_references])}
# - Running Gags: {', '.join([gag.gag for gag in episode.continuity.running_gags])}
# - Significance: {episode.cultural_impact.significance}
# """)
#
#             context = "\n".join(context_parts)
#
#             # Create prompt for LLM
#             prompt = f"""You are an expert on South Park episodes with comprehensive knowledge of the show's characters, plots, themes, and cultural impact. Answer the user's question based on the provided episode information.
#
# Question: {question}
#
# Relevant Episode Information:
# {context}
#
# Instructions:
# - Provide a comprehensive, accurate answer based on the episode information
# - Use specific details from the episodes when relevant
# - Maintain the humorous and irreverent tone appropriate for South Park
# - If the question asks about multiple episodes, compare and contrast them
# - Include episode titles and season/episode numbers when referencing specific episodes
# - If the information doesn't fully answer the question, acknowledge what you can and cannot determine from the available data
#
# Answer:"""
#
#             # Generate response using LLM
#             response = self.llm_client.generate_response(
#                 prompt=prompt,
#                 temperature=0.7,
#                 max_tokens=1000
#             )
#
#             return response.strip()
#
#         except Exception as e:
#             return f"❌ Error generating response: {e}"
#
#     def get_similar_episodes(self, episode_title: str, top_k: int = 5) -> List[Tuple[str, float]]:
#         """Find episodes similar to a given episode."""
#         if not self.embedding_model:
#             return []
#
#         # Find the target episode
#         target_episode = None
#         for episode in self.db.get_all_episodes():
#             if episode.basic_info.title.lower() == episode_title.lower():
#                 target_episode = episode
#                 break
#
#         if not target_episode:
#             return []
#
#         target_id = f"s{target_episode.season:02d}e{target_episode.episode_number:02d}"
#
#         if target_id not in self.episode_embeddings:
#             return []
#
#         target_embedding = self.episode_embeddings[target_id]
#
#         # Calculate similarities with all other episodes
#         similarities = []
#         for episode_id, episode_embedding in self.episode_embeddings.items():
#             if episode_id == target_id:
#                 continue
#
#             similarity = cosine_similarity(
#                 target_embedding.reshape(1, -1),
#                 episode_embedding.reshape(1, -1)
#             )[0][0]
#
#             # Find corresponding episode
#             season, episode_num = int(episode_id[1:3]), int(episode_id[4:6])
#             episode = self.db.get_episode(season, episode_num)
#
#             if episode:
#                 similarities.append((episode.basic_info.title, similarity))
#
#         # Sort by similarity and return top_k
#         similarities.sort(key=lambda x: x[1], reverse=True)
#         return similarities[:top_k]
#
#     def get_stats(self) -> str:
#         """Get enhanced database statistics."""
#         all_episodes = self.db.get_all_episodes()
#         total_episodes = len(all_episodes)
#         total_embeddings = len(self.episode_embeddings)
#         seasons = set(ep.season for ep in all_episodes)
#         holiday_episodes = len([ep for ep in all_episodes if ep.episode_type.value == "HOLIDAY"])
#
#         all_characters = set()
#         all_gags = set()
#
#         for episode in all_episodes:
#             for char in episode.characters.main_characters + episode.characters.supporting_characters:
#                 all_characters.add(char.name)
#             for gag in episode.continuity.running_gags:
#                 all_gags.add(gag.gag)
#
#         result = f"📊 **Enhanced Episode RAG Statistics:**\n\n"
#         result += f"• **Total Episodes:** {total_episodes}\n"
#         result += f"• **Episodes with Embeddings:** {total_embeddings}\n"
#         result += f"• **Embedding Model:** {self.embedding_model_name}\n"
#         result += f"• **Seasons:** {', '.join(map(str, sorted(seasons)))}\n"
#         result += f"• **Holiday Episodes:** {holiday_episodes}\n"
#         result += f"• **Unique Characters:** {len(all_characters)}\n"
#         result += f"• **Running Gags:** {len(all_gags)}\n"
#         result += f"• **LLM Client:** {'✅ Available' if self.llm_client else '❌ Not Available'}\n"
#
#         return result
#
#
# def main():
#     """Interactive enhanced RAG demo."""
#     print("🎬 Enhanced South Park Episode RAG System")
#     print("=" * 60)
#
#     rag = EpisodeRAGEnhanced()
#
#     if not rag.db.get_all_episodes():
#         print("❌ No episodes loaded. Please ensure episode YAML files exist in 'episode_summaries/' directory.")
#         return
#
#     print(f"✅ Loaded {len(rag.db.get_all_episodes())} episodes with enhanced RAG capabilities")
#     print("\nExample questions:")
#     print("• 'What episodes deal with religious themes?'")
#     print("• 'Compare the Christmas episodes in Season 1'")
#     print("• 'What are the most controversial episodes and why?'")
#     print("• 'Which episodes feature the most character development for Cartman?'")
#     print("• 'What cultural references appear most frequently?'")
#     print("\nType 'stats' for database statistics, 'similar <episode_title>' for similar episodes, or 'quit' to exit.\n")
#
#     while True:
#         try:
#             question = input("❓ Ask a question: ").strip()
#
#             if question.lower() in ['quit', 'exit', 'q']:
#                 print("👋 Goodbye!")
#                 break
#             elif question.lower() == 'stats':
#                 print(rag.get_stats())
#             elif question.lower().startswith('similar '):
#                 episode_title = question[8:].strip()
#                 similar = rag.get_similar_episodes(episode_title)
#                 if similar:
#                     print(f"\n🔍 **Episodes similar to '{episode_title}':**\n")
#                     for title, similarity in similar:
#                         print(f"• {title} (similarity: {similarity:.3f})")
#                 else:
#                     print(f"❌ No similar episodes found for '{episode_title}'")
#                 print()
#             elif question:
#                 answer = rag.ask(question)
#                 print(f"\n🤖 **Answer:**\n{answer}\n")
#             else:
#                 print("Please enter a question or 'quit' to exit.")
#
#         except KeyboardInterrupt:
#             print("\n👋 Goodbye!")
#             break
#         except Exception as e:
#             print(f"❌ Error: {e}")
#
#
# if __name__ == "__main__":
#     main()
