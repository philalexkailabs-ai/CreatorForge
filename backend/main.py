from fastapi import FastAPI

app = FastAPI(
    title="CreatorForge",
    description="AI-Powered Content Creation Platform",
    version="0.1"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to CreatorForge 🚀",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }