import re

from backend.ollama import ask_ollama
from backend.prompts import (
    DESCRIPTION_PROMPT,
    OUTLINE_PROMPT,
    RESEARCH_PROMPT,
    RESEARCH_SUMMARY_PROMPT,
    SCRIPT_PROMPT,
    TAGS_PROMPT,
    THUMBNAIL_PROMPT,
    TITLE_PROMPT,
)


def generate_research(topic: str, model: str | None = None) -> str:
    return _generate(RESEARCH_PROMPT, model, topic)


def generate_research_summary(
    research: str,
    model: str | None = None,
) -> str:
    return _generate(RESEARCH_SUMMARY_PROMPT, model, research=research)


def generate_outline(
    topic: str,
    research: str | None = None,
    model: str | None = None,
    research_summary: str | None = None,
) -> str:
    return _generate(
        OUTLINE_PROMPT,
        model,
        topic,
        research=research,
        research_summary=research_summary,
    )


def generate_titles(
    topic: str,
    model: str | None = None,
    research: str | None = None,
    outline: str | None = None,
    research_summary: str | None = None,
) -> list[str]:
    reply = _generate(
        TITLE_PROMPT,
        model,
        topic,
        research=research,
        outline=outline,
        research_summary=research_summary,
    )

    return [
        line.strip("- ").strip()
        for line in reply.split("\n")
        if line.strip()
    ]


def generate_script(
    topic: str,
    model: str | None = None,
    research: str | None = None,
    outline: str | None = None,
    titles: list[str] | None = None,
    research_summary: str | None = None,
) -> str:
    return _generate(
        SCRIPT_PROMPT,
        model,
        topic,
        research=research,
        outline=outline,
        titles=titles,
        research_summary=research_summary,
    )


def generate_description(
    topic: str,
    model: str | None = None,
    research: str | None = None,
    outline: str | None = None,
    script: str | None = None,
    research_summary: str | None = None,
) -> str:
    return _generate(
        DESCRIPTION_PROMPT,
        model,
        topic,
        research=research,
        outline=outline,
        script=script,
        research_summary=research_summary,
    )


def generate_tags(
    topic: str,
    model: str | None = None,
    research: str | None = None,
    outline: str | None = None,
    script: str | None = None,
    research_summary: str | None = None,
) -> list[str]:
    reply = _generate(
        TAGS_PROMPT,
        model,
        topic,
        research=research,
        outline=outline,
        script=script,
        research_summary=research_summary,
    )

    return [
        tag.strip()
        for tag in reply.split(",")
        if tag.strip()
    ]


def generate_thumbnail(
    topic: str,
    model: str | None = None,
    research: str | None = None,
    outline: str | None = None,
    script: str | None = None,
    research_summary: str | None = None,
) -> str:
    return _generate(
        THUMBNAIL_PROMPT,
        model,
        topic,
        research=research,
        outline=outline,
        script=script,
        research_summary=research_summary,
    ).strip()


def _generate(
    prompt_template: str,
    model: str | None,
    topic: str = "",
    research: str | None = None,
    outline: str | None = None,
    titles: list[str] | None = None,
    script: str | None = None,
    research_summary: str | None = None,
) -> str:
    context = _build_context(
        topic,
        research,
        outline,
        titles,
        script,
        research_summary,
    )
    reply = ask_ollama(prompt_template.format(context=context), model=model)
    return _clean_output(reply)


def _clean_output(output: str) -> str:
    cleaned = output.strip()
    cleaned = re.sub(r"(?m)^\s*```[^\n]*\n?", "", cleaned)

    if len(cleaned) >= 2 and (
        (cleaned.startswith('"') and cleaned.endswith('"'))
        or (cleaned.startswith("'") and cleaned.endswith("'"))
        or (cleaned.startswith("“") and cleaned.endswith("”"))
        or (cleaned.startswith("‘") and cleaned.endswith("’"))
    ):
        cleaned = cleaned[1:-1].strip()

    return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", cleaned).strip()


def _build_context(
    topic: str,
    research: str | None = None,
    outline: str | None = None,
    titles: list[str] | None = None,
    script: str | None = None,
    research_summary: str | None = None,
) -> str:
    sections = (
        ("Topic", topic),
        ("Research", research),
        ("Research Summary", research_summary),
        ("Outline", outline),
        ("Titles", "\n".join(titles) if titles else None),
        ("Script", script),
    )

    return "\n\n".join(
        f"{label}:\n{content.strip()}"
        for label, content in sections
        if isinstance(content, str) and content.strip()
    )
