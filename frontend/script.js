async function analyzeMessage() {
    const message = document.getElementById("message").value;
    const lang = document.getElementById("language").value;

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message, lang: lang })
        });

        const data = await response.json();

        if (!message) {
            alert("Please enter a message");
            return;
        }

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