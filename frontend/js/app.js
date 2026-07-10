async function generateProject() {

    const topic = document.getElementById("topic").value;

    if (!topic) {
        alert("Please enter a topic.");
        return;
    }

    document.getElementById("titles").textContent = "Generating...";
    document.getElementById("script").textContent = "Generating...";
    document.getElementById("description").textContent = "Generating...";
    document.getElementById("tags").textContent = "Generating...";

    try {

        const response = await fetch("http://127.0.0.1:8000/generate/project", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                topic: topic
            })
        });

        const data = await response.json();

        document.getElementById("titles").textContent =
            data.titles.join("\n");

        document.getElementById("script").textContent =
            data.script;

        document.getElementById("description").textContent =
            data.description;

        document.getElementById("tags").textContent =
            data.tags.join(", ");

    } catch (err) {

        console.error(err);

        alert("Cannot connect to CreatorForge backend.");

    }

}