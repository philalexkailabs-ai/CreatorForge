const projectCache = new Map();
const generationStages = [
    "Research",
    "Research Summary",
    "Outline",
    "Titles",
    "Script",
    "Voice",
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
        const generatedProjectId = await loadProjects(topic);
        setVoicePlayer(generatedProjectId, true);
        setVideoControls(generatedProjectId, true, false);
        setYouTubeUploadControls(generatedProjectId, false, null);

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

async function loadProjects(preferredTopic = "") {

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

            const exportButton = document.createElement("button");
            exportButton.type = "button";
            exportButton.textContent = "Export";
            exportButton.addEventListener("click", (event) => {
                event.stopPropagation();
                exportProject(project.id);
            });
            item.appendChild(exportButton);
            projectList.appendChild(item);
        });

        const preferredProject = projects.find(
            (project) => project.topic === preferredTopic
        );
        return preferredProject ? preferredProject.id : null;

    } catch (err) {

        console.error(err);
        return null;

    }

}

function exportProject(projectId) {

    const downloadLink = document.createElement("a");
    downloadLink.href =
        `http://127.0.0.1:8000/projects/${encodeURIComponent(projectId)}/export`;
    downloadLink.download = "";
    document.body.appendChild(downloadLink);
    downloadLink.click();
    downloadLink.remove();

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
    document.getElementById("play-voice").addEventListener("click", playVoice);
    document.getElementById("generate-video").addEventListener(
        "click",
        generateVideo
    );
    document.getElementById("preview-video").addEventListener(
        "click",
        previewVideo
    );
    document.getElementById("upload-youtube").addEventListener(
        "click",
        uploadToYouTube
    );
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
        setVoicePlayer(project.id, Boolean(project.voice));
        setVideoControls(project.id, Boolean(project.voice), Boolean(project.video));
        setYouTubeUploadControls(project.id, Boolean(project.video), project.youtube);

    } catch (err) {

        console.error(err);
        alert("Cannot load saved CreatorForge project.");

    }

}

function setVoicePlayer(projectId, available) {

    const playVoiceButton = document.getElementById("play-voice");
    playVoiceButton.disabled = !available || !projectId;
    playVoiceButton.dataset.projectId = available ? projectId : "";

}

function playVoice() {

    const projectId = document.getElementById("play-voice").dataset.projectId;
    if (!projectId) {
        return;
    }

    const narration = new Audio(
        `http://127.0.0.1:8000/projects/${encodeURIComponent(projectId)}/voice`
    );
    narration.play().catch((error) => console.error(error));

}

function setVideoControls(projectId, hasVoice, hasVideo) {

    const generateVideoButton = document.getElementById("generate-video");
    const previewVideoButton = document.getElementById("preview-video");
    generateVideoButton.disabled = !hasVoice || !projectId;
    previewVideoButton.disabled = !hasVideo || !projectId;
    generateVideoButton.dataset.projectId = hasVoice ? projectId : "";
    previewVideoButton.dataset.projectId = hasVideo ? projectId : "";

}

async function generateVideo() {

    const projectId = document.getElementById("generate-video").dataset.projectId;
    if (!projectId) {
        return;
    }

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/projects/${encodeURIComponent(projectId)}/video`,
            { method: "POST" }
        );
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Could not generate video.");
        }

        projectCache.delete(projectId);
        setVideoControls(projectId, true, true);
        setYouTubeUploadControls(projectId, true, null);
        previewVideo();

    } catch (err) {

        console.error(err);
        alert(err.message || "Cannot generate CreatorForge video.");

    }

}

function setYouTubeUploadControls(projectId, hasVideo, upload) {

    const uploadButton = document.getElementById("upload-youtube");
    const uploadStatus = document.getElementById("youtube-upload-status");
    const videoUrl = document.getElementById("youtube-video-url");
    uploadButton.disabled = !hasVideo || !projectId;
    uploadButton.dataset.projectId = hasVideo ? projectId : "";

    if (!upload) {
        uploadStatus.textContent = "";
        videoUrl.hidden = true;
        videoUrl.removeAttribute("href");
        return;
    }

    uploadStatus.textContent =
        `Upload Complete — Processing: ${upload.processing_status}`;
    videoUrl.href = upload.video_url;
    videoUrl.textContent = "Open YouTube Video";
    videoUrl.hidden = false;

}

async function uploadToYouTube() {

    const uploadButton = document.getElementById("upload-youtube");
    const projectId = uploadButton.dataset.projectId;
    if (!projectId || !window.confirm("Upload this video to YouTube as private?")) {
        return;
    }

    const uploadStatus = document.getElementById("youtube-upload-status");
    uploadButton.disabled = true;
    uploadStatus.textContent = "Uploading...";

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/projects/${encodeURIComponent(projectId)}/youtube-upload`,
            { method: "POST" }
        );
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Could not upload to YouTube.");
        }

        projectCache.delete(projectId);
        setYouTubeUploadControls(projectId, true, data);

    } catch (err) {

        console.error(err);
        uploadButton.disabled = false;
        uploadStatus.textContent = err.message || "YouTube upload failed.";

    }

}

function previewVideo() {

    const projectId = document.getElementById("preview-video").dataset.projectId;
    if (!projectId) {
        return;
    }

    const videoPreview = document.getElementById("video-preview");
    videoPreview.src =
        `http://127.0.0.1:8000/projects/${encodeURIComponent(projectId)}/video`;
    videoPreview.hidden = false;
    videoPreview.load();

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
