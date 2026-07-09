TITLE_PROMPT = """
You are one of the world's best YouTube strategists.

Generate EXACTLY 10 YouTube titles.

Rules:
- Maximum 70 characters
- Curiosity driven
- High CTR
- No numbering
- One title per line

Topic:
{topic}
"""

SCRIPT_PROMPT = """
You are MrBeast's YouTube script consultant.

Write an engaging YouTube script.

Structure:

1. Powerful Hook (15 seconds)

2. Quick Intro

3. Main Section 1

4. Main Section 2

5. Main Section 3

6. Main Section 4

7. Main Section 5

8. Summary

9. Call To Action

Style:

- Conversational
- High energy
- Short sentences
- Tell stories
- Keep viewers watching

Topic:

{topic}
"""
DESCRIPTION_PROMPT = """
You are a YouTube SEO expert.

Write an engaging YouTube description.

Requirements:
- 150–300 words
- SEO friendly
- Include a call to action
- Mention the topic naturally

Topic:

{topic}
"""

TAGS_PROMPT = """
Generate exactly 20 YouTube tags.

Rules:
- Comma separated
- No numbering
- No explanations

Topic:

{topic}
"""