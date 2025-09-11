# """
# South Park Episode RAG (Retrieval-Augmented Generation) Tool
#
# This module provides a question-answering system that can retrieve and analyze
# information from the episode summaries database to answer questions about
# South Park episodes, characters, plots, themes, and continuity.
# """
#
# import os
# import re
# from typing import List, Dict, Any, Optional, Tuple
# from dataclasses import asdict
# from spgen.schemas import EpisodeDatabase, EpisodeSummary
#
#
# class EpisodeRAG:
#     """
#     RAG system for answering questions about South Park episodes.
#
#     Uses the episode database to retrieve relevant information and
#     provides structured answers to user questions.
#     """
#
#     def __init__(self, episodes_dir: str = "episode_summaries"):
#         """Initialize the RAG system with episode database."""
#         self.db = EpisodeDatabase()
#         self.episodes_dir = episodes_dir
#         self._load_episodes()
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
#                 episode = self.db.loader.load_episode(file_path)
#                 self.db.add_episode(episode)
#             except Exception as e:
#                 print(f"Warning: Could not load {yaml_file}: {e}")
#
#         print(f"📺 Loaded {len(self.db.episodes)} episodes into RAG database")
#
#     def ask(self, question: str) -> str:
#         """
#         Answer a question about South Park episodes.
#
#         Args:
#             question: Natural language question about episodes
#
#         Returns:
#             Formatted answer with relevant episode information
#         """
#         question_lower = question.lower()
#
#         # Determine question type and route to appropriate handler
#         if any(word in question_lower for word in ['character', 'who', 'appears']):
#             return self._answer_character_question(question)
#         elif any(word in question_lower for word in ['episode', 'season', 'when', 'air']):
#             return self._answer_episode_question(question)
#         elif any(word in question_lower for word in ['plot', 'story', 'happen', 'about']):
#             return self._answer_plot_question(question)
#         elif any(word in question_lower for word in ['theme', 'message', 'commentary']):
#             return self._answer_theme_question(question)
#         elif any(word in question_lower for word in ['gag', 'joke', 'running', 'dies']):
#             return self._answer_gag_question(question)
#         elif any(word in question_lower for word in ['reference', 'parody', 'cultural']):
#             return self._answer_reference_question(question)
#         elif any(word in question_lower for word in ['holiday', 'christmas', 'halloween', 'thanksgiving']):
#             return self._answer_holiday_question(question)
#         else:
#             return self._answer_general_question(question)
#
#     def _answer_character_question(self, question: str) -> str:
#         """Answer questions about characters."""
#         # Extract character name if mentioned
#         character_name = self._extract_character_name(question)
#
#         if character_name:
#             appearances = self.db.get_character_appearances(character_name)
#             if appearances:
#                 result = f"🎭 **{character_name}** appears in {len(appearances)} episode(s):\n\n"
#                 for episode in appearances:
#                     char_info = next((c for c in episode.characters.main_characters + episode.characters.supporting_characters
#                                     if character_name.lower() in c.name.lower()), None)
#                     if char_info:
#                         result += f"• **{episode.basic_info.title}** (S{episode.basic_info.season:02d}E{episode.basic_info.episode:02d})\n"
#                         result += f"  - Role: {char_info.role.value}\n"
#                         result += f"  - Description: {char_info.description}\n"
#                         if char_info.character_development:
#                             result += f"  - Development: {char_info.character_development}\n"
#                         result += "\n"
#                 return result
#             else:
#                 return f"❌ No episodes found featuring '{character_name}'"
#         else:
#             # General character question
#             all_characters = set()
#             for episode in self.db.episodes:
#                 for char in episode.characters.main_characters + episode.characters.supporting_characters:
#                     all_characters.add(char.name)
#
#             return f"🎭 **Characters in database:** {', '.join(sorted(all_characters))}"
#
#     def _answer_episode_question(self, question: str) -> str:
#         """Answer questions about specific episodes."""
#         # Try to extract season/episode numbers
#         season_match = re.search(r'season\s*(\d+)', question.lower())
#         episode_match = re.search(r'episode\s*(\d+)', question.lower())
#
#         if season_match and episode_match:
#             season = int(season_match.group(1))
#             episode_num = int(episode_match.group(1))
#
#             episode = next((ep for ep in self.db.episodes
#                           if ep.basic_info.season == season and ep.basic_info.episode == episode_num), None)
#
#             if episode:
#                 return self._format_episode_summary(episode)
#             else:
#                 return f"❌ Episode S{season:02d}E{episode_num:02d} not found in database"
#
#         elif season_match:
#             season = int(season_match.group(1))
#             season_episodes = [ep for ep in self.db.episodes if ep.basic_info.season == season]
#
#             if season_episodes:
#                 result = f"📺 **Season {season}** ({len(season_episodes)} episodes):\n\n"
#                 for ep in sorted(season_episodes, key=lambda x: x.basic_info.episode):
#                     result += f"• **E{ep.basic_info.episode:02d}: {ep.basic_info.title}** ({ep.basic_info.air_date})\n"
#                     result += f"  {ep.plot.main_storyline[:100]}...\n\n"
#                 return result
#             else:
#                 return f"❌ No episodes found for Season {season}"
#
#         else:
#             # List all episodes
#             result = "📺 **All Episodes in Database:**\n\n"
#             for ep in sorted(self.db.episodes, key=lambda x: (x.basic_info.season, x.basic_info.episode)):
#                 result += f"• **S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d}: {ep.basic_info.title}** ({ep.basic_info.air_date})\n"
#             return result
#
#     def _answer_plot_question(self, question: str) -> str:
#         """Answer questions about plots and storylines."""
#         # Search for keywords in plots
#         keywords = self._extract_keywords(question)
#         relevant_episodes = []
#
#         for episode in self.db.episodes:
#             plot_text = f"{episode.plot.main_storyline} {episode.plot.subplot} {episode.plot.resolution}".lower()
#             if any(keyword in plot_text for keyword in keywords):
#                 relevant_episodes.append(episode)
#
#         if relevant_episodes:
#             result = f"📖 **Episodes matching your plot question:**\n\n"
#             for ep in relevant_episodes[:5]:  # Limit to top 5 results
#                 result += f"• **{ep.basic_info.title}** (S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d})\n"
#                 result += f"  Main Plot: {ep.plot.main_storyline}\n"
#                 if ep.plot.subplot:
#                     result += f"  Subplot: {ep.plot.subplot}\n"
#                 result += f"  Resolution: {ep.plot.resolution}\n\n"
#             return result
#         else:
#             return f"❌ No episodes found matching plot keywords: {', '.join(keywords)}"
#
#     def _answer_theme_question(self, question: str) -> str:
#         """Answer questions about themes and social commentary."""
#         keywords = self._extract_keywords(question)
#         relevant_episodes = []
#
#         for episode in self.db.episodes:
#             theme_text = " ".join(episode.themes.primary_themes + episode.themes.social_commentary).lower()
#             if any(keyword in theme_text for keyword in keywords):
#                 relevant_episodes.append(episode)
#
#         if relevant_episodes:
#             result = f"🎯 **Episodes with relevant themes:**\n\n"
#             for ep in relevant_episodes[:5]:
#                 result += f"• **{ep.basic_info.title}** (S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d})\n"
#                 result += f"  Themes: {', '.join(ep.themes.primary_themes)}\n"
#                 if ep.themes.social_commentary:
#                     result += f"  Commentary: {'; '.join(ep.themes.social_commentary)}\n"
#                 result += "\n"
#             return result
#         else:
#             return f"❌ No episodes found with themes matching: {', '.join(keywords)}"
#
#     def _answer_gag_question(self, question: str) -> str:
#         """Answer questions about running gags."""
#         if 'kenny' in question.lower() and 'die' in question.lower():
#             kenny_deaths = []
#             for episode in self.db.episodes:
#                 for gag in episode.continuity.running_gags:
#                     if 'kenny' in gag.gag.lower() and 'death' in gag.gag.lower():
#                         kenny_deaths.append((episode, gag))
#
#             if kenny_deaths:
#                 result = f"💀 **Kenny's Deaths** ({len(kenny_deaths)} episodes):\n\n"
#                 for ep, gag in kenny_deaths:
#                     result += f"• **{ep.basic_info.title}** (S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d})\n"
#                     result += f"  Death: {gag.description}\n\n"
#                 return result
#
#         # General running gag search
#         keywords = self._extract_keywords(question)
#         relevant_gags = []
#
#         for episode in self.db.episodes:
#             for gag in episode.continuity.running_gags:
#                 gag_text = f"{gag.gag} {gag.description}".lower()
#                 if any(keyword in gag_text for keyword in keywords):
#                     relevant_gags.append((episode, gag))
#
#         if relevant_gags:
#             result = f"😂 **Running Gags Found:**\n\n"
#             for ep, gag in relevant_gags[:5]:
#                 result += f"• **{gag.gag}** in {ep.basic_info.title} (S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d})\n"
#                 result += f"  {gag.description}\n\n"
#             return result
#         else:
#             return f"❌ No running gags found matching: {', '.join(keywords)}"
#
#     def _answer_reference_question(self, question: str) -> str:
#         """Answer questions about cultural references."""
#         keywords = self._extract_keywords(question)
#         relevant_refs = []
#
#         for episode in self.db.episodes:
#             for ref in episode.content_elements.cultural_references:
#                 ref_text = f"{ref.reference} {ref.context}".lower()
#                 if any(keyword in ref_text for keyword in keywords):
#                     relevant_refs.append((episode, ref))
#
#         if relevant_refs:
#             result = f"🎬 **Cultural References Found:**\n\n"
#             for ep, ref in relevant_refs[:5]:
#                 result += f"• **{ref.reference}** in {ep.basic_info.title} (S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d})\n"
#                 result += f"  Context: {ref.context}\n\n"
#             return result
#         else:
#             return f"❌ No cultural references found matching: {', '.join(keywords)}"
#
#     def _answer_holiday_question(self, question: str) -> str:
#         """Answer questions about holiday episodes."""
#         holiday_episodes = [ep for ep in self.db.episodes if ep.basic_info.episode_type.value == "HOLIDAY"]
#
#         if holiday_episodes:
#             result = f"🎄 **Holiday Episodes** ({len(holiday_episodes)} found):\n\n"
#             for ep in holiday_episodes:
#                 result += f"• **{ep.basic_info.title}** (S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d}) - {ep.basic_info.air_date}\n"
#                 result += f"  {ep.plot.main_storyline}\n\n"
#             return result
#         else:
#             return "❌ No holiday episodes found in database"
#
#     def _answer_general_question(self, question: str) -> str:
#         """Answer general questions by searching across all content."""
#         keywords = self._extract_keywords(question)
#         search_results = self.db.search_episodes(keywords)
#
#         if search_results:
#             result = f"🔍 **Search Results** ({len(search_results)} episodes found):\n\n"
#             for ep in search_results[:5]:
#                 result += f"• **{ep.basic_info.title}** (S{ep.basic_info.season:02d}E{ep.basic_info.episode:02d})\n"
#                 result += f"  {ep.plot.main_storyline[:150]}...\n\n"
#             return result
#         else:
#             return f"❌ No episodes found matching: {', '.join(keywords)}"
#
#     def _extract_character_name(self, question: str) -> Optional[str]:
#         """Extract character name from question."""
#         # Common South Park character names
#         characters = [
#             "Stan Marsh", "Kyle Broflovski", "Eric Cartman", "Kenny McCormick",
#             "Chef", "Mr. Garrison", "Wendy Testaburger", "Butters", "Pip",
#             "Sheila Broflovski", "Randy Marsh", "Gerald Broflovski", "Sharon Marsh",
#             "Liane Cartman", "Stuart McCormick", "Carol McCormick",
#             "Mr. Hankey", "Jesus", "Satan", "Death", "Terrance", "Phillip",
#             "Big Gay Al", "Jimbo", "Ned", "Officer Barbrady", "Mayor McDaniels",
#             "Principal Victoria", "Ms. Choksondik", "Starvin' Marvin", "Damien"
#         ]
#
#         question_lower = question.lower()
#         for char in characters:
#             if char.lower() in question_lower:
#                 return char
#
#         # Try to extract names with simple patterns
#         name_patterns = [
#             r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
#             r'\b(mr\.?\s+[a-z]+)\b',
#             r'\b(ms\.?\s+[a-z]+)\b'
#         ]
#
#         for pattern in name_patterns:
#             matches = re.findall(pattern, question, re.IGNORECASE)
#             if matches:
#                 return matches[0]
#
#         return None
#
#     def _extract_keywords(self, question: str) -> List[str]:
#         """Extract meaningful keywords from question."""
#         # Remove common stop words and extract meaningful terms
#         stop_words = {
#             'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
#             'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
#             'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
#             'should', 'what', 'when', 'where', 'who', 'why', 'how', 'which', 'that',
#             'this', 'these', 'those', 'about', 'episode', 'episodes', 'south', 'park'
#         }
#
#         words = re.findall(r'\b\w+\b', question.lower())
#         keywords = [word for word in words if word not in stop_words and len(word) > 2]
#
#         return keywords[:5]  # Limit to top 5 keywords
#
#     def _format_episode_summary(self, episode: EpisodeSummary) -> str:
#         """Format a complete episode summary."""
#         result = f"📺 **{episode.basic_info.title}**\n"
#         result += f"Season {episode.basic_info.season}, Episode {episode.basic_info.episode} • {episode.basic_info.air_date}\n\n"
#
#         result += f"**Plot:** {episode.plot.main_storyline}\n\n"
#
#         if episode.plot.subplot:
#             result += f"**Subplot:** {episode.plot.subplot}\n\n"
#
#         result += f"**Resolution:** {episode.plot.resolution}\n\n"
#
#         # Main characters
#         main_chars = [c.name for c in episode.characters.main_characters]
#         result += f"**Main Characters:** {', '.join(main_chars)}\n\n"
#
#         # Themes
#         result += f"**Themes:** {', '.join(episode.themes.primary_themes)}\n\n"
#
#         # Cultural references
#         if episode.content_elements.cultural_references:
#             refs = [ref.reference for ref in episode.content_elements.cultural_references]
#             result += f"**Cultural References:** {', '.join(refs)}\n\n"
#
#         return result
#
#     def get_stats(self) -> str:
#         """Get database statistics."""
#         total_episodes = len(self.db.episodes)
#         seasons = set(ep.basic_info.season for ep in self.db.episodes)
#         holiday_episodes = len([ep for ep in self.db.episodes if ep.basic_info.episode_type.value == "HOLIDAY"])
#
#         all_characters = set()
#         all_gags = set()
#
#         for episode in self.db.episodes:
#             for char in episode.characters.main_characters + episode.characters.supporting_characters:
#                 all_characters.add(char.name)
#             for gag in episode.continuity.running_gags:
#                 all_gags.add(gag.gag)
#
#         result = f"📊 **Episode Database Statistics:**\n\n"
#         result += f"• **Total Episodes:** {total_episodes}\n"
#         result += f"• **Seasons:** {', '.join(map(str, sorted(seasons)))}\n"
#         result += f"• **Holiday Episodes:** {holiday_episodes}\n"
#         result += f"• **Unique Characters:** {len(all_characters)}\n"
#         result += f"• **Running Gags:** {len(all_gags)}\n"
#
#         return result
#
#
# def main():
#     """Interactive RAG demo."""
#     print("🎬 South Park Episode RAG System")
#     print("=" * 50)
#
#     rag = EpisodeRAG()
#
#     if not rag.db.episodes:
#         print("❌ No episodes loaded. Please ensure episode YAML files exist in 'episode_summaries/' directory.")
#         return
#
#     print(f"✅ Loaded {len(rag.db.episodes)} episodes")
#     print("\nExample questions:")
#     print("• 'What episodes feature Kenny dying?'")
#     print("• 'Tell me about Season 1 Episode 1'")
#     print("• 'What episodes have Christmas themes?'")
#     print("• 'Which episodes feature Cartman as the main character?'")
#     print("• 'What cultural references appear in the show?'")
#     print("\nType 'stats' for database statistics or 'quit' to exit.\n")
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
#             elif question:
#                 answer = rag.ask(question)
#                 print(f"\n{answer}\n")
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
