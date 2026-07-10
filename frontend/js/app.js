const projectCache = new Map();
const generationStages = [
    "Research",
    "Research Summary",
    "Outline",
    "Titles",
    "Script",
    "Description",
    "Tags",
    "Thumbnail",
    "Saving",
];
let generationPollingTimer = null;

async function generateProject() {

    const topic = document.getElementById("topic").value;
    const model = document.getElementById("model").value;

    if (!topic) {
        alert("Please enter a topic.");
        return;
    }

    document.getElementById("titles").textContent = "Generating...";
    document.getElementById("script").textContent = "Generating...";
    document.getElementById("description").textContent = "Generating...";
    document.getElementById("tags").textContent = "Generating...";
    document.getElementById("research").textContent = "Generating...";
    document.getElementById("research-summary").textContent = "Generating...";
    document.getElementById("outline").textContent = "Generating...";
    document.getElementById("thumbnail-prompt").textContent = "Generating...";
    startGenerationPolling();

    try {

        const response = await fetch("http://127.0.0.1:8000/generate/project", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                topic: topic,
                model: model
            })
        });

        const data = await response.json();

        stopGenerationPolling();
        renderGenerationProgress("Completed", false);

        projectCache.clear();
        loadProjects();

        document.getElementById("titles").textContent =
            data.titles.join("\n");

        document.getElementById("script").textContent =
            data.script;

        document.getElementById("description").textContent =
            data.description;

        document.getElementById("tags").textContent =
            data.tags.join(", ");

        document.getElementById("research").textContent = data.research;
        document.getElementById("research-summary").textContent =
            data.research_summary;
        document.getElementById("outline").textContent = data.outline;
        document.getElementById("thumbnail-prompt").textContent =
            data.thumbnail_prompt;

    } catch (err) {

        console.error(err);

        alert("Cannot connect to CreatorForge backend.");

        stopGenerationPolling();
        renderGenerationProgress("Idle", false);

    }

}

async function loadProjects() {

    const projectList = document.getElementById("project-list");

    try {

        const response = await fetch("http://127.0.0.1:8000/projects");

        if (!response.ok) {
            throw new Error("Could not load saved projects.");
        }

        const projects = await response.json();
        projectList.replaceChildren();

        projects.forEach((project) => {
            const item = document.createElement("li");
            item.textContent = project.name;
            item.addEventListener("click", () => loadProject(project.id));
            projectList.appendChild(item);
        });

    } catch (err) {

        console.error(err);

    }

}

function startGenerationPolling() {

    stopGenerationPolling();
    renderGenerationProgress("Research", true);
    generationPollingTimer = setInterval(pollGenerationStatus, 1000);

}

function stopGenerationPolling() {

    if (generationPollingTimer) {
        clearInterval(generationPollingTimer);
        generationPollingTimer = null;
    }

}

async function pollGenerationStatus() {

    try {

        const response = await fetch("http://127.0.0.1:8000/generation/status");

        if (!response.ok) {
            throw new Error("Could not load generation status.");
        }

        const status = await response.json();
        renderGenerationProgress(status.stage, status.running);

        if (status.stage === "Idle") {
            stopGenerationPolling();
        }

    } catch (err) {

        console.error(err);
        stopGenerationPolling();
        renderGenerationProgress("Idle", false);

    }

}

function renderGenerationProgress(stage, running) {

    const currentIndex = generationStages.indexOf(stage);
    const progress = generationStages.map((stageName, index) => {
        if (stage === "Completed" || index < currentIndex) {
            return `✅ ${stageName}`;
        }

        if (running && index === currentIndex) {
            return `⏳ ${stageName}`;
        }

        return `○ ${stageName}`;
    });

    document.getElementById("generation-progress").textContent =
        progress.join("\n");

}

document.addEventListener("DOMContentLoaded", () => {
    loadProjects();
    renderGenerationProgress("Idle", false);
});

async function loadProject(projectId) {

    let project = projectCache.get(projectId);

    try {

        if (!project) {
            const response = await fetch(
                `http://127.0.0.1:8000/projects/${encodeURIComponent(projectId)}`
            );

            if (!response.ok) {
                throw new Error("Could not load saved project.");
            }

            project = await response.json();
            projectCache.set(projectId, project);
        }

        document.getElementById("titles").textContent =
            project.titles.join("\n");
        document.getElementById("script").textContent = project.script;
        document.getElementById("description").textContent = project.description;
        document.getElementById("tags").textContent = project.tags.join(", ");
        document.getElementById("research").textContent = project.research;
        document.getElementById("research-summary").textContent =
            project.research_summary;
        document.getElementById("outline").textContent = project.outline;
        document.getElementById("thumbnail-prompt").textContent =
            project.thumbnail_prompt;

    } catch (err) {

        console.error(err);
        alert("Cannot load saved CreatorForge project.");

    }

}

async function generateThumbnail() {

    const topic = document.getElementById("topic").value;
    const model = document.getElementById("model").value;

    if (!topic) {
        alert("Please enter a topic.");
        return;
    }

    const thumbnailPrompt = document.getElementById("thumbnail-prompt");
    thumbnailPrompt.textContent = "Generating...";

    try {

        const response = await fetch("http://127.0.0.1:8000/generate/thumbnail", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                topic: topic,
                model: model
            })
        });

        const data = await response.json();

        thumbnailPrompt.textContent = data.thumbnail_prompt;

    } catch (err) {

        console.error(err);

        thumbnailPrompt.textContent = "";
        alert("Cannot connect to CreatorForge backend.");

    }

}
