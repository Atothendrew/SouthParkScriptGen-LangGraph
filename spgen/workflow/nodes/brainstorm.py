"""
Multi-agent brainstorming and collaborative refinement system.

This module implements the core creative collaboration features of the episode
generation workflow. It orchestrates multiple AI personas through structured
brainstorming sessions, interactive Q&A, and iterative refinement processes
that simulate a real writers' room environment.

Key Components:
- Initial brainstorming with multiple personas
- Targeted Q&A sessions between specific agents  
- Follow-up conversation support with multi-round discussions
- Collaborative outline refinement based on group feedback

The module emphasizes realistic creative collaboration patterns:
- Agents ask specific, targeted questions to other agents
- Responses can trigger follow-up conversations
- All interactions are preserved for context in later workflow steps
- File outputs maintain complete conversation history for human review

Technical Features:
- Comprehensive logging of all agent interactions
- Robust follow-up question parsing and routing
- Separate file organization for questions, responses, and follow-ups
- Error handling for malformed follow-up questions
- Debug logging for troubleshooting conversation flows
"""

import os
import random
from typing import Dict, List

from spgen.workflow.state import EpisodeState
from spgen.workflow.llm_client import llm_call, search_tool
from spgen.workflow.logger import get_logger
from spgen.workflow.utils import should_include_persona
from spgen.agents import PERSONAS


def brainstorm(state: EpisodeState) -> Dict:
    """
    Initial brainstorming phase where each persona generates independent episode ideas.
    
    This function orchestrates the first creative phase of the workflow, where
    multiple AI personas simultaneously develop initial episode concepts based on
    the user's prompt. Each persona applies their unique comedic style and perspective
    to create diverse creative starting points.
    
    Process Flow:
    1. Filter active personas based on include/exclude settings
    2. Prepare context including continuity from previous episodes
    3. Generate persona-specific prompts with news context if available
    4. Collect independent episode ideas from each participating persona
    5. Save individual ideas to separate files for later reference
    
    Args:
        state (EpisodeState): Current workflow state containing:
            - prompt: User's episode idea/theme
            - include_personas/exclude_personas: Persona filtering
            - continuity: Context from previous episode parts
            - news_context_files: Optional current events context
            - log_dir: Output directory for generated files
    
    Returns:
        Dict: Updated state with:
            - agent_outputs: List of {name, outline} pairs
            - discussion_history: Empty list (reset for next phase)
    
    Output Files:
        - ideas/{persona_name}.md: Individual brainstorming results
        
    Technical Details:
        - Uses persona-specific temperature settings for creativity
        - Supports multi-part episode continuity
        - Integrates current events context when available
        - Comprehensive logging of each persona's participation
    """
    logger = get_logger()
    logger.info("🧠 Starting initial brainstorming phase...")
    prompt = state["prompt"]
    continuity = state.get("continuity")
    outputs: List[Dict] = []
    ideas_dir = os.path.join(state["log_dir"], "ideas")
    os.makedirs(ideas_dir, exist_ok=True)
    
    # Count participating agents
    participating_agents = []
    for name in PERSONAS.keys():
        if name == "Deep Thought":
            continue
        if not should_include_persona(name, state):
            continue
        participating_agents.append(name)
    
    logger.info(f"📝 {len(participating_agents)} personas will brainstorm ideas: {', '.join(participating_agents)}")

    # Get user feedback if available
    user_feedback_str = ""
    if state.get("user_feedback"):
        feedback_list = state["user_feedback"]
        # Assuming user_feedback is a list of dicts like [{"step": "USER_NEWS_REVIEW", "feedback": "..."}]
        # We'll concatenate all feedback from the USER_NEWS_REVIEW step
        relevant_feedback = [
            item["feedback"] for item in feedback_list 
            if item.get("step") == "USER_NEWS_REVIEW" and item.get("feedback")
        ]
        if relevant_feedback:
            user_feedback_str = "\n\nUSER FEEDBACK ON NEWS:\n" + "\n".join(relevant_feedback)

    for name, persona in PERSONAS.items():
        if name == "Deep Thought":
            continue
        if not should_include_persona(name, state):
            continue

        logger.info(f"💡 {name} is generating an initial idea...")
        # Prepare prompt with continuity and news context
        prompt_kwargs = {"prompt": prompt}
        
        # Add news context if available
        news_context = ""
        if state.get("news_context_files"):
            news_files = state["news_context_files"]
            if name == "Matt Stone" and "matt_perspective" in news_files:
                try:
                    with open(news_files["matt_perspective"], "r", encoding="utf-8") as f:
                        news_context = f"\n\nCURRENT EVENTS CONTEXT (Matt Stone's Perspective):\n{f.read()}"
                except:
                    pass
            elif name == "Trey Parker" and "trey_perspective" in news_files:
                try:
                    with open(news_files["trey_perspective"], "r", encoding="utf-8") as f:
                        news_context = f"\n\nCURRENT EVENTS CONTEXT (Trey Parker's Perspective):\n{f.read()}"
                except:
                    pass
            elif "news_context" in news_files:
                try:
                    with open(news_files["news_context"], "r", encoding="utf-8") as f:
                        news_context = f"\n\nCURRENT EVENTS CONTEXT:\n{f.read()}"
                except:
                    pass
        
        # Append user feedback to news context if it exists
        if user_feedback_str:
            news_context += user_feedback_str

        prompt_kwargs["news_context"] = news_context
        
        if continuity:
            prompt_kwargs.update({
                "part_number": continuity.get("part_number", ""),
                "total_parts": continuity.get("total_parts", ""),
                "original_prompt": continuity.get("original_prompt", ""),
                "previous_summaries": "\n".join([f"Part {i+1}: {summary}" for i, summary in enumerate(continuity.get("previous_summaries", []))]) if continuity.get("previous_summaries") else "",
                "character_developments": "\n".join([f"- {dev}" for dev in continuity.get("character_developments", [])]) if continuity.get("character_developments") else "",
                "running_gags": "\n".join([f"- {gag}" for gag in continuity.get("running_gags", [])]) if continuity.get("running_gags") else "",
                "unresolved_plotlines": "\n".join([f"- {plot}" for plot in continuity.get("unresolved_plotlines", [])]) if continuity.get("unresolved_plotlines") else "",
                "established_locations": ", ".join(continuity.get("established_locations", [])) if continuity.get("established_locations") else ""
            })
        else:
            # Provide empty values for template variables when no continuity
            prompt_kwargs.update({
                "part_number": "",
                "total_parts": "",
                "original_prompt": "",
                "previous_summaries": "",
                "character_developments": "",
                "running_gags": "",
                "unresolved_plotlines": "",
                "established_locations": ""
            })

        outline = llm_call(
            persona["brainstorm_prompt"], 
            temperature=persona["temperature"]["brainstorm"], 
            tools=[search_tool], 
            **prompt_kwargs
        )
        outputs.append({"name": name, "outline": outline})
        with open(os.path.join(ideas_dir, f"{name}.md"), "w", encoding="utf-8") as f:
            f.write(f"# {name}\n\n{outline}")
        logger.info(f"✅ {name} completed their idea (saved to ideas/{name}.md)")

    state["agent_outputs"] = outputs
    state["discussion_history"] = []
    
    logger.info(f"🧠 Initial brainstorming complete! {len(outputs)} ideas generated.")
    return {"agent_outputs": outputs, "discussion_history": []}


def interactive_brainstorm_questions(state: EpisodeState) -> Dict:
    """Agents ask each other questions about their brainstorming ideas."""
    logger = get_logger()
    logger.info("🤝 Starting interactive Q&A session...")
    agent_outputs = state["agent_outputs"]
    
    # Enhanced logging for debugging Q&A flow
    logger.info(f"📊 Q&A session context:")
    logger.info(f"  - Available agents: {len(agent_outputs)}")
    for agent in agent_outputs:
        logger.info(f"    - {agent['name']}: {len(agent['outline'])} characters")
    
    questions_dir = os.path.join(state["log_dir"], "brainstorm_questions")
    responses_dir = os.path.join(state["log_dir"], "brainstorm_responses")
    os.makedirs(questions_dir, exist_ok=True)
    os.makedirs(responses_dir, exist_ok=True)
    
    # Create a summary of all agent outlines for context
    all_outlines = "\n\n".join([
        f"**{agent['name']}:**\n{agent['outline']}" 
        for agent in agent_outputs
    ])
    
    questions_and_responses = []
    
    # Each agent asks questions to one specific other agent to keep it focused
    import random
    available_agents = [agent["name"] for agent in agent_outputs]
    
    for asker_name, asker_persona in PERSONAS.items():
        if asker_name == "Deep Thought":
            continue
        if not should_include_persona(asker_name, state):
            continue
            
        # Skip if this agent didn't participate in brainstorming
        if not any(agent["name"] == asker_name for agent in agent_outputs):
            continue
        
        # Pick one other agent to ask questions to (not themselves)
        other_agents = [name for name in available_agents if name != asker_name]
        if not other_agents:
            continue
        target_agent = random.choice(other_agents)
        target_outline = next((agent["outline"] for agent in agent_outputs if agent["name"] == target_agent), "")
        
        logger.info(f"❓ {asker_name} is asking questions to {target_agent}...")
        
        # Generate targeted questions to specific agent
        question_prompt = f"""
You are {asker_name} in a writers' room brainstorming session. You want to collaborate with {target_agent} on their episode idea.

{target_agent}'s outline:
{target_outline}

As {asker_name}, ask {target_agent} 2-3 specific, constructive questions about their idea. Focus on:
- What's funny and what could be funnier?
- Plot holes or unclear motivations  
- Character dynamics that could be enhanced
- Satirical opportunities that might be missed
- Ways to build on their concept

Address {target_agent} directly and keep your questions in character for {asker_name}'s voice and comedy style.
"""
        
        questions = llm_call(
            question_prompt,
            temperature=asker_persona["temperature"]["discussion"],
            tools=[search_tool]
        )
        
        logger.info(f"📊 {asker_name}'s questions size: {len(questions)} characters")
        questions_and_responses.append(f"**{asker_name} asks {target_agent}:**\n{questions}")
        
        # Save individual questions
        questions_file = os.path.join(questions_dir, f"{asker_name}.md")
        with open(questions_file, "w", encoding="utf-8") as f:
            f.write(f"# {asker_name}'s Questions\n\n{questions}\n\n")
        logger.info(f"✅ {asker_name}'s questions saved to brainstorm_questions/{asker_name}.md")
    
    # Now each agent responds only to questions specifically directed at them
    responses = []
    for responder_name, responder_persona in PERSONAS.items():
        if responder_name == "Deep Thought":
            continue
        if not should_include_persona(responder_name, state):
            continue
            
        # Skip if this agent didn't participate in brainstorming
        if not any(agent["name"] == responder_name for agent in agent_outputs):
            continue
        
        # Find questions directed specifically at them
        directed_questions = []
        for q in questions_and_responses:
            if f"asks {responder_name}:" in q:
                directed_questions.append(q)
        
        # Skip if no questions were directed at them
        if not directed_questions:
            continue
            
        logger.info(f"💬 {responder_name} is responding to questions...")
        
        # Get their original outline
        original_outline = next(
            (agent["outline"] for agent in agent_outputs if agent["name"] == responder_name),
            ""
        )
        
        targeted_questions = "\n\n".join(directed_questions)
        
        response_prompt = f"""
You are {responder_name} in a writers' room. Another writer has asked you specific questions about your brainstormed idea.

Your original outline:
{original_outline}

Questions directed at you:
{targeted_questions}

Respond to these specific questions in a conversational way. Show how you might:
- Adapt your ideas based on the feedback
- Build on the suggestions  
- Address any concerns raised
- Collaborate to improve the concept

If your response raises NEW questions or you want to dig deeper into something they suggested, end your response with:
"FOLLOW-UP QUESTION FOR [WRITER NAME]: [Your follow-up question here]"

This will trigger another round of back-and-forth discussion.

Stay true to {responder_name}'s voice and comedy perspective.
"""
        
        response = llm_call(
            response_prompt,
            temperature=responder_persona["temperature"]["discussion"],
            tools=[search_tool]
        )
        
        logger.info(f"📊 {responder_name}'s response size: {len(response)} characters")
        responses.append(f"**{responder_name} responds:**\n{response}")
        
        # Save responses to separate file in responses directory
        responses_file = os.path.join(responses_dir, f"{responder_name}.md")
        with open(responses_file, "w", encoding="utf-8") as f:
            f.write(f"# {responder_name}'s Responses\n\n{response}\n\n")
        logger.info(f"✅ {responder_name}'s response saved to brainstorm_responses/{responder_name}.md")
    
    # Check for follow-up questions in responses and handle iterative conversation
    all_interactions = questions_and_responses + responses
    max_rounds = 2  # Limit to prevent infinite loops
    
    total_interactions_size = sum(len(item) for item in all_interactions)
    logger.info(f"📊 After initial Q&A: {len(all_interactions)} interactions, {total_interactions_size} characters")
    logger.info("🔄 Checking for follow-up questions...")
    for round_num in range(max_rounds):
        follow_up_questions = []
        
        # Extract follow-up questions from the latest responses
        logger.info(f"🔍 Analyzing {len(responses)} responses for follow-up questions...")
        for i, response in enumerate(responses):
            logger.debug(f"Response {i+1}: {response[:100]}...")
            # Check for follow-up questions with case-insensitive matching
            import re
            if re.search(r'follow[‑\-]?up\s+question\s+for', response, re.IGNORECASE):
                logger.info(f"🔍 Found follow-up question marker in response {i+1}")
                # Parse the follow-up question
                lines = response.split('\n')
                for line_num, line in enumerate(lines):
                    # Handle both formats: "FOLLOW-UP QUESTION FOR" and "**FOLLOW-UP QUESTION FOR" and case variations
                    clean_line = line.strip().replace("**", "").replace("*", "")
                    if re.search(r'^follow[‑\-]?up\s+question\s+for', clean_line, re.IGNORECASE):
                        logger.info(f"🔍 Processing follow-up question on line {line_num}: {line}")
                        # Extract target and question
                        try:
                            # Use case-insensitive parsing
                            import re
                            # Match various formats: "Follow-up question for", "FOLLOW-UP QUESTION FOR", etc.
                            pattern = r'follow[‑\-]?up\s+question\s+for\s*(.+)'
                            match = re.search(pattern, clean_line, re.IGNORECASE)
                            if not match:
                                continue
                            
                            remainder = match.group(1)
                            target_and_question = remainder.split(":", 1)
                            if len(target_and_question) == 2:
                                target_name = target_and_question[0].strip()
                                follow_up_q = target_and_question[1].strip()
                                
                                # If the question is empty, check the next line
                                if not follow_up_q and line_num + 1 < len(lines):
                                    follow_up_q = lines[line_num + 1].strip()
                                
                                # Find the original responder (who's now asking)
                                asker_name = None
                                # Extract name from response header
                                if response.startswith("**") and " responds:**" in response:
                                    asker_name = response.split("**")[1].split(" responds:")[0]
                                
                                # Map first names to full persona names
                                full_target_name = target_name
                                if target_name and target_name not in PERSONAS:
                                    # Try to find a persona that starts with this first name
                                    for persona_name in PERSONAS.keys():
                                        if persona_name.lower().startswith(target_name.lower()):
                                            full_target_name = persona_name
                                            logger.info(f"🔄 Mapped '{target_name}' to full name '{full_target_name}'")
                                            break
                                
                                if asker_name and full_target_name:
                                    logger.info(f"✅ Successfully parsed follow-up: {asker_name} -> {full_target_name}: {follow_up_q[:50]}...")
                                    follow_up_questions.append({
                                        "asker": asker_name,
                                        "target": full_target_name, 
                                        "question": follow_up_q
                                    })
                                else:
                                    logger.warning(f"⚠️ Could not parse follow-up: asker={asker_name}, target={target_name}")
                        except Exception as e:
                            logger.warning(f"⚠️ Error parsing follow-up question: {e}")
                            continue
            else:
                logger.debug(f"No follow-up question marker found in response {i+1}")
        
        # If no follow-up questions, break the loop
        if not follow_up_questions:
            logger.info("✅ No follow-up questions found, Q&A session complete")
            break
            
        logger.info(f"🔄 Found {len(follow_up_questions)} follow-up question(s) for round {round_num + 1}...")
        for fq in follow_up_questions:
            logger.info(f"  - {fq['asker']} asks {fq['target']}: {fq['question'][:50]}...")
            
        # Process follow-up questions
        new_responses = []
        for fq in follow_up_questions:
            asker_name = fq["asker"]
            target_name = fq["target"]
            question = fq["question"]
            
            # Get target's persona
            if target_name not in PERSONAS:
                continue
            target_persona = PERSONAS[target_name]
            
            logger.info(f"🔄 {target_name} responding to {asker_name}'s follow-up...")
            
            # Get target's original outline
            target_outline = next(
                (agent["outline"] for agent in agent_outputs if agent["name"] == target_name),
                ""
            )
            
            follow_up_prompt = f"""
You are {target_name} in a writers' room. {asker_name} just asked you a follow-up question after your previous discussion.

Your original outline:
{target_outline}

{asker_name}'s follow-up question:
{question}

Respond to this follow-up question. You can also ask your own follow-up question back using the same format:
"FOLLOW-UP QUESTION FOR [WRITER NAME]: [Your question]"

Stay true to {target_name}'s voice and comedy perspective.
"""
            
            follow_up_response = llm_call(
                follow_up_prompt,
                temperature=target_persona["temperature"]["discussion"],
                tools=[search_tool]
            )
            
            logger.info(f"📊 {target_name}'s follow-up response size: {len(follow_up_response)} characters")
            new_responses.append(f"**{target_name} responds to {asker_name}'s follow-up:**\n{follow_up_response}")
            
            # Save the follow-up response
            responses_file = os.path.join(responses_dir, f"{target_name}_followup_{round_num + 1}.md")
            with open(responses_file, "w", encoding="utf-8") as f:
                f.write(f"# {target_name}'s Follow-up Response (Round {round_num + 1})\n\n{follow_up_response}\n\n")
            logger.info(f"✅ {target_name}'s follow-up saved to brainstorm_responses/{target_name}_followup_{round_num + 1}.md")
        
        # Add new responses to the overall discussion
        all_interactions.extend(new_responses)
        responses = new_responses  # Update responses for next iteration
        
        # Log round completion
        round_size = sum(len(item) for item in new_responses)
        total_size_now = sum(len(item) for item in all_interactions)
        logger.info(f"📊 Round {round_num + 1} complete: {len(new_responses)} responses, {round_size} characters")
        logger.info(f"📊 Total interactions so far: {len(all_interactions)} items, {total_size_now} characters")
    
    # Combine all interactions into discussion history
    final_interaction_size = sum(len(item) for item in all_interactions)
    logger.info(f"📊 Final Q&A session results:")
    logger.info(f"  - Total interactions: {len(all_interactions)}")
    logger.info(f"  - Total size: {final_interaction_size} characters")
    logger.info(f"  - Questions generated: {len(questions_and_responses)}")
    logger.info(f"  - Responses generated: {len([r for r in all_interactions if 'responds' in r])}")
    
    state["discussion_history"] = all_interactions
    
    # Save combined Q&A session with all rounds
    with open(os.path.join(state["log_dir"], "brainstorm_questions_session.md"), "w", encoding="utf-8") as f:
        f.write("# Interactive Brainstorm Q&A Session\n\n")
        f.write("## Complete Conversation (All Rounds)\n\n")
        for interaction in all_interactions:
            f.write(f"{interaction}\n\n")
    
    logger.info(f"🤝 Interactive Q&A session complete! {len(all_interactions)} interactions saved.")
    return {"discussion_history": all_interactions}


def refine_outline(state: EpisodeState) -> Dict:
    """Each agent refines the merged outline."""
    logger = get_logger()
    logger.info("🔧 Starting outline refinement phase...")
    merged_outline = state["merged_outline"]
    outputs: List[Dict] = []
    refine_dir = os.path.join(state["log_dir"], "refine")
    os.makedirs(refine_dir, exist_ok=True)

    for name, persona in PERSONAS.items():
        if name == "Deep Thought":
            continue
        if not should_include_persona(name, state):
            continue

        logger.info(f"🔧 {name} is refining the merged outline...")
        refined_outline = llm_call(
            persona["refine_prompt"], 
            temperature=persona["temperature"]["refine"], 
            tools=[search_tool], 
            outline=merged_outline
        )
        outputs.append({"name": name, "outline": refined_outline})
        with open(os.path.join(refine_dir, f"{name}.md"), "w", encoding="utf-8") as f:
            f.write(f"# {name}\n\n{refined_outline}")
        logger.info(f"✅ {name} completed refinement (saved to refine/{name}.md)")

    state["agent_outputs"] = outputs  # Overwrite agent_outputs with refined outlines for final discussion
    # Preserve discussion history instead of resetting it
    
    logger.info(f"🔧 Outline refinement complete! {len(outputs)} refined outlines ready.")
    return {"agent_outputs": outputs}