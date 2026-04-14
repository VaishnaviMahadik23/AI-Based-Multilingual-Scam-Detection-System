async function analyzeMessage() {
    const message = document.getElementById("message").value;

    if (!message) {
        alert("Please enter a message");
        return;
    }

    document.getElementById("output").innerHTML = "Analyzing...";

    try {
        const response = await fetch("https://ai-based-multilingual-scam-detection.onrender.com/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        let className = "";

        if (data.result_key === "safe") {
            className = "safe";
        } else if (data.result_key === "suspicious") {
            className = "suspicious";
        } else {
            className = "danger";
        }

        document.getElementById("output").innerHTML = `
            <div class="result ${className}">
                <h3>${data.result_text}</h3>
                <p><b>${data.labels.probability}:</b> ${data.scam_probability}%</p>
                <p><b>${data.labels.keywords}:</b> ${data.keywords_found.join(", ") || "None"}</p>
                <p><b>${data.labels.links}:</b> ${data.links_found.join(", ") || "None"}</p>
            </div>
        `;

    } catch (error) {
        console.error(error);
        alert("Error connecting to server");
    }
}

function setExample(text) {
    document.getElementById("message").value = text;
}