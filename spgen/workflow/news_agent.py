"""News research agent for dynamic prompt generation."""

import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict

from ddgs import DDGS
from spgen.workflow.llm_provider import llm_call


class NewsResearchAgent:
    """Agent for researching current events and creating contextual content."""

    def __init__(self):
        self.ddgs = DDGS()
        self._latest_news_results: List[Dict] = []

    def search_news(self, query: str, num_results: int = 5, append_news_suffix: bool = True) -> List[Dict]:
        """Search for recent news using DuckDuckGo."""
        try:
            search_query = f"{query}"
            if append_news_suffix:
                search_query = f"{query} news"

            if "southpark" in search_query:
                return []

            print(f"📰 Searching for news with query: '{search_query}'")
            results = []

            # Search for recent news
            for result in self.ddgs.news(
                query=search_query,
                region='us-en',
                safesearch='moderate',
                timelimit='h',  # Past week
                max_results=num_results
            ):
                res = {
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('url', ''),
                    'date': result.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d')),
                    'source': result.get('source', '')
                }
                results.append(res)

            if results:
                print(f"✅ Found {len(results)} news results.")
            else:
                print(f"❌ No results found.")
            return results

        except Exception as e:
            print(f"❌ News search failed: {e}")
            return []

    def analyze_news_for_south_park(self, news_results: List[Dict], original_prompt: str) -> str:
        """Analyze news results and create South Park-relevant context."""
        if not news_results:
            return "No recent news found to inform this episode."

        news_summaries = []
        for item in news_results:
            news_summaries.append(f"- {item['title']}: {item['snippet']}")

        news_text = "\n".join(news_summaries)

        analysis_prompt = f"""
You are a South Park writer analyzing current events to inform episode creation.

Original Episode Concept: {original_prompt}

Recent News Context:
{news_text}

Analyze these news stories and identify:

1. SATIRICAL OPPORTUNITIES: What aspects of these stories could South Park satirize?
2. SOCIAL COMMENTARY: What deeper social issues do these stories reveal?
3. CHARACTER CONNECTIONS: How might Stan, Kyle, Cartman, and Kenny react to these events?
4. SOUTH PARK ANGLES: What unique perspective could South Park bring to these topics?
5. EPISODE INTEGRATION: How could these current events be woven into the original episode concept?

Provide your analysis in markdown format with clear sections.
"""

        try:
            print("🧠 Analyzing news for South Park context...")
            analysis, model_name = llm_call(analysis_prompt, temperature=0.7)
            print("✅ News analysis complete. Model: ", model_name)
            return analysis
        except Exception as e:
            return f"News analysis failed: {e}"

    def _extract_keywords(self, prompt: str) -> List[str]:
        """Extract keywords from a prompt using an LLM call."""
        keyword_prompt = f'''
From the following South Park episode concept, extract 3-5 main keywords or short phrases that would be effective for searching for related news articles.
IMPORTANT: Do NOT include "South Park", "SouthPark", "Trey Parker", "Matt Stone", or "Comedy Central" in your keywords.

Return only a comma-separated list of these keywords.

Concept: "{prompt}"
'''
        try:
            print("🔑 Extracting keywords from prompt...")
            keywords_str, model_name = llm_call(keyword_prompt, temperature=0.2)
            keywords = [k.strip() for k in keywords_str.split(',')]
            print(f"✅ Extracted keywords: {keywords}")
            return keywords
        except Exception as e:
            print(f"❌ Keyword extraction failed: {e}")
            return []

    def create_news_context_files(self, prompt: str, log_dir: str) -> Dict[str, str]:
        """Create news context markdown files for Matt and Trey."""
        news_dir = os.path.join(log_dir, "news_context")
        os.makedirs(news_dir, exist_ok=True)

        unique_news = []
        if self._latest_news_results:
            print("♻️ Using news from dynamic prompt generation for context.")
            unique_news = self._latest_news_results
            self._latest_news_results = [] # Reset after use
        else:
            search_terms = self._extract_keywords(prompt)
            if not search_terms:
                print("⚠️ Keyword extraction failed. Using the full prompt as a single search term.")
                search_terms = [prompt]

            print(f"🔍 Creating news context with search terms: {search_terms}")

            all_news = []
            for term in search_terms:
                # Try searching without "news" suffix first
                results = self.search_news(term, num_results=3, append_news_suffix=False)
                if not results:
                    # If no results, try with "news" suffix
                    print(f"🔄 Retrying search for '{term}' with 'news' suffix.")
                    results = self.search_news(term, num_results=3, append_news_suffix=True)

                print(f"🔎 Raw search results for '{term}': {len(results)} articles.")
                for r in results:
                    print(f"    - Title: {r.get('title', 'N/A')}, Source: {r.get('source', 'N/A')}")

                all_news.extend(results)

            print(f"📚 Total articles collected before deduplication: {len(all_news)} articles.")
            for a in all_news:
                print(f"    - Title: {a.get('title', 'N/A')}, Source: {a.get('source', 'N/A')}")

            # Remove duplicates based on title
            seen_titles = set()
            for item in all_news:
                if item['title'] not in seen_titles:
                    unique_news.append(item)
                    seen_titles.add(item['title'])

        print(f"📰 Using {len(unique_news)} unique news articles for context after deduplication.")
        for u in unique_news:
            print(f"    - Title: {u.get('title', 'N/A')}, Source: {u.get('source', 'N/A')}")

        # Exit if no news found
        if not unique_news:
            print("❌ No news results found for dynamic prompt generation.")
            print("💡 Try running without --dynamic-prompt or check your internet connection.")
            exit(1)

        # Create analysis
        analysis = self.analyze_news_for_south_park(unique_news, prompt)

        # Save news context file
        news_file = os.path.join(news_dir, "current_events_analysis.md")
        print(f"📝 Saving current events analysis to: {news_file}")
        with open(news_file, "w", encoding="utf-8") as f:
            f.write(f"# Current Events Analysis\n\n")
            f.write(f"**Episode Concept:** {prompt}\n\n")
            f.write(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n")

            f.write("## Recent News Headlines\n\n")
            for item in unique_news:
                f.write(f"### {item['title']}\n")
                f.write(f"*{item['date']} - {item.get('source', 'Unknown Source')}*\n\n")
                f.write(f"{item['snippet']}\n\n")
                f.write(f"[Source]({item['url']})\n\n")

            f.write("## South Park Writer's Analysis\n\n")
            f.write(analysis)

        # Create Matt Stone's perspective file
        matt_analysis = self.create_matt_stone_analysis(unique_news, prompt)
        matt_file = os.path.join(news_dir, "matt_stone_perspective.md")
        print(f"📝 Saving Matt Stone's perspective to: {matt_file}")
        with open(matt_file, "w", encoding="utf-8") as f:
            f.write(f"# Matt Stone's Perspective on Current Events\n\n")
            f.write(matt_analysis)

        # Create Trey Parker's perspective file
        trey_analysis = self.create_trey_parker_analysis(unique_news, prompt)
        trey_file = os.path.join(news_dir, "trey_parker_perspective.md")
        print(f"📝 Saving Trey Parker's perspective to: {trey_file}")
        with open(trey_file, "w", encoding="utf-8") as f:
            f.write(f"# Trey Parker's Perspective on Current Events\n\n")
            f.write(trey_analysis)

        return {
            "news_context": news_file,
            "matt_perspective": matt_file,
            "trey_perspective": trey_file
        }

    def create_matt_stone_analysis(self, news_results: List[Dict], prompt: str) -> str:
        """Create Matt Stone's pragmatic analysis of current events."""
        news_text = "\n".join([f"- {item['title']}: {item['snippet']}" for item in news_results])

        matt_prompt = f"""
You are Matt Stone, co-creator of South Park. You're known for your pragmatic, libertarian perspective and ability to see through BS on both sides of any issue.

Episode Concept: {prompt}
Current News: {news_text}

Analyze these current events from your perspective:

1. What's the REAL story behind these headlines?
2. What are both sides getting wrong?
3. How are people overreacting or missing the point?
4. What would a reasonable person think about this?
5. How could we make fun of the extreme reactions without being preachy?
6. What's the human truth underneath all the noise?

Write in your direct, no-nonsense style. Be skeptical of both liberal and conservative takes.
"""

        try:
            print("🧠 Generating Matt Stone's perspective...")
            analysis, model_name = llm_call(matt_prompt, temperature=0.6)
            print("✅ Matt Stone's perspective generated.")
            return analysis
        except Exception as e:
            return f"Analysis failed: {e}"

    def create_trey_parker_analysis(self, news_results: List[Dict], prompt: str) -> str:
        """Create Trey Parker's satirical analysis of current events."""
        news_text = "\n".join([f"- {item['title']}: {item['snippet']}" for item in news_results])

        trey_prompt = f"""
You are Trey Parker, co-creator of South Park. You have a gift for finding the absurd in any situation and turning it into brilliant satire.

Episode Concept: {prompt}
Current News: {news_text}

Analyze these current events from your satirical perspective:

1. What's completely absurd about these situations?
2. What are people taking too seriously?
3. How could we exaggerate these to reveal deeper truths?
4. What musical or theatrical elements could enhance the satire?
5. Which characters would react most hilariously to these events?
6. How could we make this both shocking and meaningful?

Write with your sharp, irreverent style. Look for the satirical gold in these stories.
"""

        try:
            print("🧠 Generating Trey Parker's perspective...")
            analysis, model_name = llm_call(trey_prompt, temperature=0.8)
            print("✅ Trey Parker's perspective generated.")
            return analysis
        except Exception as e:
            return f"Analysis failed: {e}"

    def generate_episode_prompt_from_news(self) -> str:
        """Generate a South Park episode prompt based on current trending news."""
        try:
            print("📰 Searching for trending news to generate dynamic prompt...")
            trending_results = []

            # Get general trending news
            for result in self.ddgs.news(
                query="breaking news",
                region='us-en',
                safesearch='off',
                timelimit='d',  # Past week
                max_results=20
            ):
                res = {
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('url', ''),
                    'date': result.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d')),
                    'source': result.get('source', '')
                }
                trending_results.append(res)

            if not trending_results:
                print("❌ No trending news found. Cannot generate dynamic prompt.")
                print("💡 Try running without --dynamic-prompt or check your internet connection.")
                exit(1)

            print(f"✅ Found {len(trending_results)} trending news articles.")
            self._latest_news_results = trending_results

            # Create a summary of trending topics
            news_summaries = []
            for item in trending_results[:5]:  # Top 5 stories
                news_summaries.append(f"- {item.get('title', '')}: {item.get('snippet', '')[:100]}...")

            news_text = "\n".join(news_summaries)
            print(f"🗞️ News summary for prompt generation:\n{news_text}")

            prompt_generation = f"""
You are a South Park writer tasked with creating an episode concept based on today's trending news.

Current Trending News:
{news_text}

Generate a creative South Park episode prompt that:
1. Takes inspiration from one or more of these trending topics
2. Could realistically happen in South Park with the main kids (Stan, Kyle, Cartman, Kenny)
3. Has potential for both humor and social commentary
4. Is something that would air on Comedy Central
5. Can be told in a 22-minute episode format

Respond with ONLY the episode prompt as a single sentence, like:
"The boys discover that AI chatbots are replacing all the teachers at South Park Elementary"

Do not include any explanation, just the prompt.
"""

            print("🤖 Generating dynamic episode prompt from news...")
            generated_prompt, model_name = llm_call(prompt_generation, temperature=0.7)
            
            # Parse the response to extract just the final prompt
            # Handle responses with reasoning channels (LM Studio models)
            clean_prompt = generated_prompt.strip()
            
            # Look for the final message in channel format
            if '<|channel|>final<|message|>' in clean_prompt:
                # Extract content after the final channel marker
                parts = clean_prompt.split('<|channel|>final<|message|>')
                if len(parts) > 1:
                    clean_prompt = parts[-1].strip()
            
            # Look for content between quotes if it exists
            import re
            quote_match = re.search(r'"([^"]+)"', clean_prompt)
            if quote_match:
                clean_prompt = quote_match.group(1)
            else:
                # If no quotes, take the last sentence that looks like an episode prompt
                sentences = clean_prompt.split('.')
                for sentence in reversed(sentences):
                    sentence = sentence.strip()
                    if (sentence and 
                        len(sentence) > 50 and  # Long enough to be a prompt
                        ('boys' in sentence.lower() or 'south park' in sentence.lower())):
                        clean_prompt = sentence
                        break
            
            # Final cleanup
            clean_prompt = clean_prompt.strip().strip('"').strip("'").strip('.')
            
            print(f"✅ Generated dynamic prompt: '{clean_prompt}'")
            return clean_prompt

        except Exception as e:
            print(f"❌ Prompt generation failed: {e}")
            print("💡 Try running without --dynamic-prompt or check your internet connection.")
            exit(1)


if __name__ == "__main__":
    agent = NewsResearchAgent()
    resp = agent.search_news("", num_results=20)
    for r in resp:
        print(r)
