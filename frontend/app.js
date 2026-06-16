(function () {
    const form = document.getElementById("upload-form");
    const fileInput = document.getElementById("resume");
    const fileName = document.getElementById("file-name");
    const statusBox = document.getElementById("status");
    const resultBox = document.getElementById("result");
    const portfolioLink = document.getElementById("portfolio-link");
    const submitButton = document.getElementById("submit-button");
    const apiBase = (window.FOLIOFORGE_API_BASE || "http://127.0.0.1:8000").replace(/\/+$/, "");

    function showStatus(message, isError) {
        statusBox.hidden = false;
        statusBox.textContent = message;
        statusBox.classList.toggle("error", Boolean(isError));
    }

    fileInput.addEventListener("change", function () {
        const file = fileInput.files && fileInput.files[0];
        fileName.textContent = file ? file.name : "No file selected";
        resultBox.hidden = true;
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const file = fileInput.files && fileInput.files[0];
        if (!file) {
            showStatus("Choose a PDF resume first.", true);
            return;
        }

        const body = new FormData();
        body.append("resume", file);

        submitButton.disabled = true;
        showStatus("Generating your portfolio. This can take a few seconds.", false);
        resultBox.hidden = true;

        try {
            const response = await fetch(apiBase + "/api/generate", {
                method: "POST",
                body: body
            });
            const payload = await response.json();

            if (!response.ok) {
                throw new Error(payload.error || "Portfolio generation failed.");
            }

            portfolioLink.href = payload.portfolio_url;
            portfolioLink.textContent = "Open Portfolio";
            resultBox.hidden = false;
            showStatus("Portfolio generated successfully.", false);
            window.open(payload.portfolio_url, "_blank", "noopener,noreferrer");
        } catch (error) {
            showStatus(error.message || "Something went wrong while generating the portfolio.", true);
        } finally {
            submitButton.disabled = false;
        }
    });
})();
