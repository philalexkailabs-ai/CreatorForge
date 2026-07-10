TITLE_PROMPT = """
You are one of the world's best YouTube strategists.

Generate EXACTLY 10 high-CTR YouTube titles.

Rules:
- Maximum 70 characters per title
- Curiosity driven
- One title per line
- No numbering, bullets, markdown, headings, or explanations
- Do not include an introduction, closing sentence, or "Let me know" message
- Return titles only

{context}
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

Return only the finished script. Do not add AI explanations, closing remarks,
"Let me know" messages, or markdown code fences.

{context}
"""

DESCRIPTION_PROMPT = """
You are a YouTube SEO expert.

Write an engaging YouTube description.

Requirements:
- 150-300 words
- SEO friendly
- Include a call to action
- Mention the topic naturally
- Use plain text only; do not use markdown formatting

Return only the description. Do not add a heading, "Description:" label, or
explanation.

{context}
"""

TAGS_PROMPT = """
Generate exactly 20 YouTube tags.

Rules:
- Comma separated
- No numbering, bullets, markdown, or explanations
- No introduction or closing message
- Return tags only

{context}
"""

THUMBNAIL_PROMPT = """
You are a YouTube thumbnail strategist.

Create one detailed AI image-generation prompt for a high-CTR YouTube
thumbnail using the context below.

Requirements:
- Describe the main subject, expression, composition, background, lighting, and colors
- Make the focal point clear at a small size
- Use bold, high-contrast visual ideas
- Do not include text, logos, watermarks, or aspect-ratio instructions
- Return one image prompt only
- Do not add a heading, quotation marks, markdown, or explanations

{context}
"""

RESEARCH_PROMPT = """
You are a YouTube research strategist.

Create a structured markdown research document for a video about the topic.

Include clearly separated sections for:
- Important Facts
- Key Concepts
- Common Mistakes
- Current Best Practices
- Audience Pain Points
- Recommendations

Rules:
- Clearly distinguish verified facts from recommendations
- Prioritize current best practices
- Avoid speculative statements and invented statistics or sources
- Return only the research document
- Do not talk to the user, explain your process, or use markdown code fences

{context}
"""

RESEARCH_SUMMARY_PROMPT = """
Summarize the supplied research in approximately 200-300 words.

Include only:
- Key facts
- Important recommendations
- Important warnings
- Best practices

Return only the summary. Do not add conversational text, an introduction, a
conclusion, or markdown code fences.

{context}
"""

OUTLINE_PROMPT = """
You are a YouTube content strategist.

Create a detailed YouTube video outline using the available context.

Include:
- Introduction
- Clearly named sections
- Key talking points for each section
- Call To Action

Return only the outline. Do not add an introduction, closing remarks,
explanations, or markdown code fences.

{context}
"""
