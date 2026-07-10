# Prompt Rules

## Prompt Construction

Prompt templates define the task, constraints, and expected output. `generator.py` builds shared context and supplies it through the template context placeholder.

## Output-Only Philosophy

Generation prompts should ask for the requested artifact only. Avoid conversational framing, follow-up offers, self-explanation, headings that were not requested, and Markdown code fences.

## No Conversational AI Output

Do not ask models to explain their process or address the user unless the artifact explicitly requires it. Output should be immediately usable by a creator.

## Prompt Consistency

- State clear structure and constraints.
- Specify counts and formats where needed.
- Keep terminology consistent across artifacts.
- Preserve model-agnostic prompt behavior.

## Context Builder Usage

Use the generator context builder instead of assembling topic, research, summary, outline, titles, or script text in individual generator functions. It omits empty sections and keeps labels consistent.

## Prompt Validation Philosophy

Prompts first prevent malformed output. Lightweight cleanup then removes obvious fences, surrounding quotes, and excess whitespace. More aggressive validation or retries require explicit approval.
