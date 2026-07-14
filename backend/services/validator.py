import re


ValidationResult = dict[str, bool | list[str]]


def validate_titles(titles: list[str]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if len(titles) != 10:
        errors.append("Titles must contain exactly 10 items.")

    normalized_titles = [title.strip().casefold() for title in titles if title.strip()]
    if len(normalized_titles) != len(titles):
        errors.append("Titles must be non-empty.")
    if len(set(normalized_titles)) != len(normalized_titles):
        errors.append("Titles must not contain duplicates.")

    for title in titles:
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", title):
            errors.append("Titles must not include bullets or numbering.")
            break
        if title and not 5 <= len(title.strip()) <= 100:
            errors.append("Titles must have a reasonable length.")
            break

    return _result(errors, warnings)


def validate_script(script: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    cleaned_script = script.strip()

    if not cleaned_script:
        errors.append("Script must not be empty.")
    elif len(cleaned_script.split()) < 100:
        errors.append("Script must contain at least 100 words.")

    filler_phrases = (
        "as an ai language model",
        "i cannot",
        "let me know if",
        "here is the script",
    )
    if any(phrase in cleaned_script.casefold() for phrase in filler_phrases):
        warnings.append("Script contains possible AI filler.")

    call_to_action_terms = ("subscribe", "comment", "like", "follow")
    if cleaned_script and not any(
        term in cleaned_script.casefold() for term in call_to_action_terms
    ):
        warnings.append("Script may not contain a call to action.")

    return _result(errors, warnings)


def validate_description(description: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    cleaned_description = description.strip()

    if not cleaned_description:
        errors.append("Description must not be empty.")
    if re.search(r"(?m)^\s*#{1,6}\s+", cleaned_description):
        errors.append("Description must not contain Markdown headings.")
    if cleaned_description and len(cleaned_description.split()) < 50:
        warnings.append("Description is very short.")

    return _result(errors, warnings)


def validate_tags(tags: list[str]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if len(tags) != 20:
        errors.append("Tags must contain exactly 20 items.")

    normalized_tags = [tag.strip().casefold() for tag in tags if tag.strip()]
    if len(normalized_tags) != len(tags):
        errors.append("Tags must be non-empty.")
    if len(set(normalized_tags)) != len(normalized_tags):
        errors.append("Tags must not contain duplicates.")

    return _result(errors, warnings)


def validate_thumbnail(thumbnail: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    cleaned_thumbnail = thumbnail.strip()

    if not cleaned_thumbnail:
        errors.append("Thumbnail prompt must not be empty.")
    if len([line for line in cleaned_thumbnail.splitlines() if line.strip()]) > 1:
        errors.append("Thumbnail output must contain one prompt.")
    if re.search(r"```|^\s*#{1,6}\s+", cleaned_thumbnail, re.MULTILINE):
        errors.append("Thumbnail prompt must not contain Markdown.")
    if re.search(r"\b(here is|let me know|i can|this prompt)\b", cleaned_thumbnail, re.I):
        errors.append("Thumbnail prompt must not contain conversational text.")

    return _result(errors, warnings)


def validate_research(research: str) -> ValidationResult:
    return _validate_non_empty("Research", research)


def validate_outline(outline: str) -> ValidationResult:
    return _validate_non_empty("Outline", outline)


def validate_research_summary(research_summary: str) -> ValidationResult:
    return _validate_non_empty("Research summary", research_summary)


def _validate_non_empty(name: str, content: str) -> ValidationResult:
    errors = [] if content.strip() else [f"{name} must not be empty."]
    return _result(errors, [])


def _result(errors: list[str], warnings: list[str]) -> ValidationResult:
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }
