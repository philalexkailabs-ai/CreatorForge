from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.ollama import ask_ollama
from backend.prompts import (
    TITLE_PROMPT,
    SCRIPT_PROMPT,
    DESCRIPTION_PROMPT,
    TAGS_PROMPT,
)
app = FastAPI(title="CreatorForge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str


@app.get("/")
def home():
    return {"message": "CreatorForge Running 🚀"}


@app.post("/generate/titles")
def generate_titles(request: TopicRequest):

    prompt = TITLE_PROMPT.format(topic=request.topic)

    reply = ask_ollama(prompt)

    titles = [
        line.strip("- ").strip()
        for line in reply.split("\n")
        if line.strip()
    ]

    return {
        "titles": titles
    }
@app.post("/generate/script")
def generate_script(request: TopicRequest):

    prompt = SCRIPT_PROMPT.format(topic=request.topic)

    script = ask_ollama(prompt)

    return {
        "script": script
    }
@app.post("/generate/project")
def generate_project(request: TopicRequest):

    # Generate Titles
    title_reply = ask_ollama(
        TITLE_PROMPT.format(topic=request.topic)
    )

    titles = [
        line.strip("- ").strip()
        for line in title_reply.split("\n")
        if line.strip()
    ]

    # Generate Script
    script = ask_ollama(
        SCRIPT_PROMPT.format(topic=request.topic)
    )

    # Generate Description
    description = ask_ollama(
        DESCRIPTION_PROMPT.format(topic=request.topic)
    )

    # Generate Tags
    tags_reply = ask_ollama(
        TAGS_PROMPT.format(topic=request.topic)
    )

    tags = [
        tag.strip()
        for tag in tags_reply.split(",")
        if tag.strip()
    ]

    return {
        "titles": titles,
        "script": script,
        "description": description,
        "tags": tags
    }