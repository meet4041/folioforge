(function () {
    const form = document.getElementById("upload-form");
    const fileInput = document.getElementById("resume");
    const fileName = document.getElementById("file-name");
    const statusBox = document.getElementById("status");
    const resultOverlay = document.getElementById("result-overlay");
    const resultBox = document.getElementById("result");
    const resultOpen = document.getElementById("result-open");
    const copyLinkButton = document.getElementById("copy-link");
    const copyFeedback = document.getElementById("copy-feedback");
    const resultClose = document.getElementById("result-close");
    const submitButton = document.getElementById("submit-button");
    const isLocalHost = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
    const configuredApiBase = window.FOLIOFORGE_API_BASE || "http://127.0.0.1:8000";
    const apiBase = (isLocalHost ? window.location.origin : configuredApiBase).replace(/\/+$/, "");
    const requestTimeoutMs = 45000;
    let latestPortfolioUrl = "";

    function showStatus(message, isError) {
        statusBox.hidden = false;
        statusBox.textContent = message;
        statusBox.classList.toggle("error", Boolean(isError));
    }

    function hideStatus() {
        statusBox.hidden = true;
        statusBox.textContent = "";
        statusBox.classList.remove("error");
    }

    function hideResultCard() {
        resultOverlay.hidden = true;
        document.body.classList.remove("has-result-overlay");
        copyFeedback.hidden = true;
    }

    async function copyPortfolioLink() {
        if (!latestPortfolioUrl) {
            return;
        }
        try {
            await navigator.clipboard.writeText(latestPortfolioUrl);
            copyFeedback.textContent = "Link copied to clipboard.";
            copyFeedback.hidden = false;
        } catch (_error) {
            copyFeedback.textContent = "Could not copy automatically. Please copy the link manually.";
            copyFeedback.hidden = false;
        }
    }

    async function fetchWithTimeout(url, options) {
        const controller = new AbortController();
        const timeoutId = window.setTimeout(function () {
            controller.abort();
        }, requestTimeoutMs);

        try {
            return await fetch(url, {
                ...options,
                signal: controller.signal
            });
        } finally {
            window.clearTimeout(timeoutId);
        }
    }

    fileInput.addEventListener("change", function () {
        const file = fileInput.files && fileInput.files[0];
        fileName.textContent = file ? file.name : "No file selected";
        hideStatus();
        hideResultCard();
    });

    copyLinkButton.addEventListener("click", function () {
        copyPortfolioLink();
    });

    resultClose.addEventListener("click", function () {
        hideResultCard();
    });

    resultOverlay.addEventListener("click", function () {
        hideResultCard();
    });

    resultBox.addEventListener("click", function (event) {
        event.stopPropagation();
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
        hideStatus();
        hideResultCard();

        try {
            const response = await fetchWithTimeout(apiBase + "/api/generate", {
                method: "POST",
                body: body
            });
            const payload = await response.json();

            if (!response.ok) {
                throw new Error(payload.error || "Portfolio generation failed.");
            }

            latestPortfolioUrl = payload.portfolio_url;
            resultOpen.href = payload.portfolio_url;
            copyFeedback.hidden = true;
            resultOverlay.hidden = false;
            document.body.classList.add("has-result-overlay");
        } catch (error) {
            const message = error.name === "AbortError"
                ? "Portfolio generation timed out. Please try again."
                : (error.message || "Something went wrong while generating the portfolio.");
            showStatus(message, true);
        } finally {
            submitButton.disabled = false;
        }
    });
})();
