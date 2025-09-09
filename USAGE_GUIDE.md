# South Park Episode Generator - Usage Guide 📖

## Quick Start

### Prerequisites
1. **LM Studio** running locally with a model loaded
2. **Python 3.8+** with required dependencies
3. **LMSTUDIO_ENDPOINT** environment variable (optional, defaults to localhost:1234)

### Basic Commands

```bash
# Generate a single episode
python cli.py "The kids accidentally discover time travel"

# Generate a 3-part episode series
python cli.py "Randy becomes mayor and chaos ensues" -n 3

# Use only specific writers
python cli.py "Kyle starts a podcast" --include_personas "Trey Parker,Matt Stone,Bill Hader"

# Exclude certain writers  
python cli.py "Cartman opens a restaurant" --exclude_personas "Chris Farley,Conan O'Brian"

# Include current events context
python cli.py "The town deals with social media drama" --dynamic_prompt
```

## Output Structure

Each episode generates a timestamped directory with complete creative process documentation:

```
logs/
└── Episode_Title_20250110_153045/
    └── part_01/
        ├── process.txt                 # Complete workflow log
        ├── prompt.md                   # Original user prompt
        ├── ideas/                      # Initial brainstorming
        │   ├── Trey Parker.md
        │   ├── Matt Stone.md
        │   ├── Bill Hader.md
        │   └── Andy Samberg.md
        ├── brainstorm_questions/       # Agent questions
        │   ├── Trey Parker.md
        │   ├── Matt Stone.md
        │   └── Bill Hader.md
        ├── brainstorm_responses/       # Agent responses
        │   ├── Trey Parker.md
        │   ├── Matt Stone.md
        │   ├── Bill Hader.md
        │   └── Bill Hader_followup_1.md
        ├── brainstorm_session/         # Agent feedback
        ├── final_discussion_feedback/  # Final round feedback
        ├── final_merged_outline.md     # Consolidated episode outline
        └── script.md                   # Complete episode script
```

## Example Workflow Output

### Console Output
```
--- Generating Part 1/1 ---
🔧 Built episode generation workflow with 12 steps
🔧 Episode generation workflow initialized
🚀 Starting episode generation for part 1 of 1...
📁 Working directory: logs/The_kids_accidentally_discover_time_travel_20250110_153045/part_01
📋 Workflow has 12 steps total
================================================================

⏳ Step 1/12: Brainstorm
📊 Progress: [█░░░░░░░░░░░] 1/12
🧠 Starting initial brainstorming phase...
📝 4 personas will brainstorm ideas: Trey Parker, Matt Stone, Bill Hader, Andy Samberg
💡 Trey Parker is generating an initial idea...
✅ Trey Parker completed their idea (saved to ideas/Trey Parker.md)
💡 Matt Stone is generating an initial idea...
✅ Matt Stone completed their idea (saved to ideas/Matt Stone.md)
💡 Bill Hader is generating an initial idea...
✅ Bill Hader completed their idea (saved to ideas/Bill Hader.md)
💡 Andy Samberg is generating an initial idea...
✅ Andy Samberg completed their idea (saved to ideas/Andy Samberg.md)
🧠 Initial brainstorming complete! 4 ideas generated.
✅ Step 1/12 complete: Brainstorm

⏳ Step 2/12: Interactive Brainstorm Questions
📊 Progress: [██░░░░░░░░░░] 2/12
🤝 Starting interactive Q&A session...
❓ Trey Parker is asking questions to Bill Hader...
✅ Trey Parker's questions saved to brainstorm_questions/Trey Parker.md
❓ Matt Stone is asking questions to Andy Samberg...
✅ Matt Stone's questions saved to brainstorm_questions/Matt Stone.md
💬 Bill Hader is responding to questions...
✅ Bill Hader's response saved to brainstorm_responses/Bill Hader.md
💬 Andy Samberg is responding to questions...
✅ Andy Samberg's response saved to brainstorm_responses/Andy Samberg.md
🔄 Checking for follow-up questions...
🔄 Found 1 follow-up question(s) for round 1...
🔄 Trey Parker responding to Bill Hader's follow-up...
✅ Trey Parker's follow-up saved to brainstorm_responses/Trey Parker_followup_1.md
🔄 Checking for follow-up questions...
✅ No follow-up questions found, Q&A session complete
🤝 Interactive Q&A session complete! 6 interactions saved.
✅ Step 2/12 complete: Interactive Brainstorm Questions

[... continues through all 12 steps ...]

================================================================
🎉 Episode part 1 generation complete!
📁 Episode logs written to: logs/The_kids_accidentally_discover_time_travel_20250110_153045/part_01
```

### Sample Generated Content

#### Initial Brainstorming (ideas/Trey Parker.md)
```markdown
# Trey Parker

## "Temporal Meltdown" - A South Park Time Travel Catastrophe

**Cold Open**: The boys find Cartman's "science project" - actually a broken microwave 
he's been using to heat up his mom's leftover KFC. When Kyle points out that it's 
just a microwave, Cartman insists it's a "temporal displacement device" and 
dramatically presses buttons. Suddenly, the kitchen starts glitching...

**Act 1**: The kids realize they've accidentally created a time loop where South Park 
keeps reliving the same Tuesday. Every reset, Cartman becomes more convinced he's a 
time-travel genius, while Kyle desperately tries to fix things. Stan keeps asking 
his dad for help, but Randy is too busy trying to exploit the time loop for his 
latest get-rich-quick scheme.

**The Comedy**: Each loop, the boys try different approaches to fix the temporal 
anomaly, but their kid logic makes everything worse. Meanwhile, the adults of South 
Park start noticing the loops and form conspiracy theories about government time 
experiments, while Randy tries to patent "temporal weed farming."

**Resolution**: The fix isn't science - it's Cartman admitting he doesn't know 
everything. But of course, he does this accidentally while having a tantrum, 
breaking the real temporal device (which was hidden in the school basement all along).
```

#### Interactive Q&A (brainstorm_questions/Matt Stone.md)
```markdown
# Matt Stone's Questions

Hey Trey, I love the time loop concept, but what if we pushed the Randy subplot further? 

What if Randy doesn't just try to exploit the loop, but he actually thinks he caused it with 
his latest scientific experiment (maybe he was trying to age his marijuana faster)? 

And then he starts a whole conspiracy theory about how the government is stealing his 
"chronological agriculture" research? That could give us a great B-plot where Randy 
becomes convinced he's the real time travel genius, not Cartman.

Also, should we have a moment where the loop breaks at the worst possible time - like 
right when the boys finally think they have it figured out?
```

#### Follow-up Conversation (brainstorm_responses/Trey Parker_followup_1.md)
```markdown
# Trey Parker's Follow-up Response (Round 1)

Matt, that's brilliant! Randy thinking HE caused the time loop with his "chronological 
agriculture" is perfect. We could have him set up a whole lab in the garage with 
increasingly ridiculous time-related weed experiments.

And yes! The loop should break at the absolute worst moment - maybe right when they're 
in the middle of explaining to the whole town how to fix it, so suddenly everyone's 
confused and blaming them for the whole mess in the first place.

FOLLOW-UP QUESTION FOR MATT: Should we have a scene where Randy and Cartman both think 
they're time travel experts and start competing? Like they both set up rival "temporal 
research facilities" and try to out-science each other with increasingly stupid theories?
```

#### Final Episode Script (script.md - excerpt)
```markdown
# Episode Script

**FADE IN:**

**INT. CARTMAN'S KITCHEN - DAY**

*The boys are gathered around a beat-up microwave that's sparking slightly. Cartman stands 
proudly next to it wearing safety goggles made from swim goggles and duct tape.*

**CARTMAN**
Behold! My temporal displacement device!

**KYLE**
Cartman, that's just your mom's broken microwave.

**CARTMAN**
Wrong, Kyle! This is a sophisticated piece of chronological engineering that will allow 
us to travel through time and space!

*Cartman dramatically presses several buttons. The microwave starts making weird noises.*

**STAN**
Dude, I don't think you should—

*FLASH OF LIGHT. Everything freezes for a moment, then resets.*

**CARTMAN**
Behold! My temporal displacement device!

**KYLE**
(confused)
Didn't you just say that?

**KENNY**
(muffled)
Mmmph mmmph mmmph!

**STAN**
Wait... why do I feel like we've done this before?

*Cartman presses the buttons again. FLASH. Reset.*

**CARTMAN**
Behold! My temporal displacement device!

**KYLE**
(panicking)
Oh my God, we're in a time loop!

**CARTMAN**
(smugly)
See? I told you it was a temporal displacement device. I'm basically a genius scientist now.
```

### Process Log (process.txt - excerpt)
```
2025-01-10 15:30:45 - 🔧 Episode generation workflow initialized
2025-01-10 15:30:45 - 🚀 Starting episode generation for part 1 of 1...
2025-01-10 15:30:45 - 📁 Working directory: logs/The_kids_accidentally_discover_time_travel_20250110_153045/part_01
2025-01-10 15:30:45 - 📋 Workflow has 12 steps total
2025-01-10 15:30:45 - ================================================================
2025-01-10 15:30:45 - ⏳ Step 1/12: Brainstorm
2025-01-10 15:30:45 - 📊 Progress: [█░░░░░░░░░░░] 1/12
2025-01-10 15:30:45 - 🧠 Starting initial brainstorming phase...
2025-01-10 15:30:45 - 📝 4 personas will brainstorm ideas: Trey Parker, Matt Stone, Bill Hader, Andy Samberg
2025-01-10 15:30:46 - 💡 Trey Parker is generating an initial idea...
2025-01-10 15:31:15 - ✅ Trey Parker completed their idea (saved to ideas/Trey Parker.md)
2025-01-10 15:31:15 - 💡 Matt Stone is generating an initial idea...
2025-01-10 15:31:42 - ✅ Matt Stone completed their idea (saved to ideas/Matt Stone.md)
[... detailed timestamped log continues ...]
```

## Advanced Features

### Multi-Part Episodes
Generate episodic content with continuity tracking:

```bash
python cli.py "The boys start a business that grows over time" -n 3
```

This creates three connected episodes with:
- Character development tracking across parts
- Running gag continuation  
- Plot thread resolution
- Location and relationship continuity

### Persona Customization
Create custom writers by adding YAML files to the `configs/` directory:

```yaml
# configs/Custom Writer.yaml
bio: "A comedy writer who specializes in absurdist humor and pop culture references"
brainstorm_prompt: "Create a South Park episode that satirizes current trends with absurd escalation..."
discussion_prompt: "Provide feedback that pushes ideas to be more satirical and unexpected..."
refine_prompt: "Refine the outline to maximize comedic timing and cultural commentary..."
temperature:
  brainstorm: 0.9    # High creativity
  discussion: 0.7    # Balanced collaboration
  refine: 0.5        # Focused refinement
```

### Current Events Integration
Use `--dynamic_prompt` to incorporate news research:

```bash
python cli.py "Social media causes problems in South Park" --dynamic_prompt
```

This triggers the news research phase, gathering current events context before brainstorming.

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'langgraph'"**
   ```bash
   pip install langgraph
   ```

2. **"Connection refused" errors**
   - Ensure LM Studio is running
   - Check endpoint: `export LMSTUDIO_ENDPOINT="http://localhost:1234/v1"`

3. **Empty or incomplete outputs**
   - Check LM Studio model is loaded and responding
   - Verify sufficient system RAM for model inference
   - Review process.txt log for error details

4. **Follow-up questions not working**
   - Check brainstorm_responses/ for parsing debug messages
   - Ensure proper "FOLLOW-UP QUESTION FOR [NAME]:" format

### Performance Optimization

- **Faster Generation**: Use smaller/faster models in LM Studio
- **Better Quality**: Use larger models with more VRAM
- **Memory Usage**: Close other applications during generation
- **Storage**: Clean old logs periodically (episodes can be 10MB+ each)

## Tips for Best Results

1. **Specific Prompts**: "The boys discover social media algorithms" vs "Social media episode"
2. **Persona Selection**: Choose complementary writing styles for better collaboration
3. **Multi-Part Planning**: Design story arcs that benefit from multiple episodes
4. **Review Outputs**: Check intermediate files (ideas/, brainstorm_responses/) for quality
5. **Iterate**: Use successful patterns from previous generations

---

*For technical details and architecture information, see [README.md](README.md)*