(function () {
    const form = document.getElementById("upload-form");
    const reviewForm = document.getElementById("review-form");
    const fileInput = document.getElementById("resume");
    const fileName = document.getElementById("file-name");
    const statusBox = document.getElementById("status");
    const submitButton = document.getElementById("submit-button");

    const reviewOverlay = document.getElementById("review-overlay");
    const reviewModal = document.getElementById("review-modal");
    const reviewClose = document.getElementById("review-close");
    const reviewCancel = document.getElementById("review-cancel");
    const reviewName = document.getElementById("review-name");
    const reviewTitleInput = document.getElementById("review-title-input");
    const reviewLocation = document.getElementById("review-location");
    const reviewEmail = document.getElementById("review-email");
    const reviewLinkedin = document.getElementById("review-linkedin");
    const reviewGithub = document.getElementById("review-github");
    const reviewSummary = document.getElementById("review-summary");
    const reviewLinks = document.getElementById("review-links");
    const skillsEditor = document.getElementById("skills-editor");
    const educationEditor = document.getElementById("education-editor");
    const experienceEditor = document.getElementById("experience-editor");
    const projectsEditor = document.getElementById("projects-editor");
    const reviewResponsibilityTitle = document.getElementById("review-responsibility-title");
    const reviewResponsibilityPeriod = document.getElementById("review-responsibility-period");
    const reviewResponsibilityOrg = document.getElementById("review-responsibility-org");
    const reviewResponsibilityBullets = document.getElementById("review-responsibility-bullets");
    const reviewAchievements = document.getElementById("review-achievements");
    const addSkillGroupButton = document.getElementById("add-skill-group");
    const addEducationButton = document.getElementById("add-education");
    const addExperienceButton = document.getElementById("add-experience");
    const addProjectButton = document.getElementById("add-project");

    const resultOverlay = document.getElementById("result-overlay");
    const resultBox = document.getElementById("result");
    const resultOpen = document.getElementById("result-open");
    const copyLinkButton = document.getElementById("copy-link");
    const copyFeedback = document.getElementById("copy-feedback");
    const resultClose = document.getElementById("result-close");

    const isLocalHost = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
    const configuredApiBase = window.FOLIOFORGE_API_BASE || "http://127.0.0.1:8000";
    const apiBase = (isLocalHost ? window.location.origin : configuredApiBase).replace(/\/+$/, "");
    const requestTimeoutMs = 45000;

    let latestPortfolioUrl = "";
    let latestJobId = "";

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

    function showPageLock() {
        document.body.classList.add("has-overlay");
    }

    function hidePageLockIfNeeded() {
        if (reviewOverlay.hidden && resultOverlay.hidden) {
            document.body.classList.remove("has-overlay");
        }
    }

    function hideResultCard() {
        resultOverlay.hidden = true;
        copyFeedback.hidden = true;
        hidePageLockIfNeeded();
    }

    function showReviewOverlay() {
        reviewOverlay.hidden = false;
        showPageLock();
    }

    function hideReviewOverlay() {
        reviewOverlay.hidden = true;
        hidePageLockIfNeeded();
    }

    function escapeHtml(value) {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function splitLines(value) {
        return value
            .split(/\r?\n/)
            .map(function (item) {
                return item.trim();
            })
            .filter(Boolean);
    }

    function createInput(label, className, value) {
        return [
            '<label class="review-field">',
            "<span>" + label + "</span>",
            '<input type="text" class="' + className + '" value="' + escapeHtml(value) + '">',
            "</label>"
        ].join("");
    }

    function createTextarea(label, className, value, rows) {
        return [
            '<label class="review-field review-field--full">',
            "<span>" + label + "</span>",
            '<textarea class="' + className + '" rows="' + rows + '">' + escapeHtml(value) + "</textarea>",
            "</label>"
        ].join("");
    }

    function renderSkills(skills) {
        const groups = Object.entries(skills || {});
        skillsEditor.innerHTML = groups.length ? groups.map(function (entry, index) {
            return [
                '<div class="review-item" data-skill-index="' + index + '">',
                '<div class="review-item-top"><span class="review-item-title">Skill Group</span><button type="button" class="review-remove" data-remove-skill="' + index + '">Remove</button></div>',
                '<div class="review-grid">',
                createInput("Group Label", "skill-label", entry[0]),
                createInput("Items", "skill-items", (entry[1] || []).join(", ")),
                "</div></div>"
            ].join("");
        }).join("") : '<div class="review-empty">No skill groups yet. Add one if you want.</div>';
    }

    function renderEducation(items) {
        educationEditor.innerHTML = items.length ? items.map(function (item, index) {
            return [
                '<div class="review-item" data-education-index="' + index + '">',
                '<div class="review-item-top"><span class="review-item-title">Education</span><button type="button" class="review-remove" data-remove-education="' + index + '">Remove</button></div>',
                '<div class="review-grid">',
                createInput("School", "education-school", item.school),
                createInput("Period", "education-period", item.period),
                createInput("Detail", "education-detail", item.detail),
                createInput("Location", "education-location", item.location),
                "</div></div>"
            ].join("");
        }).join("") : '<div class="review-empty">No education entries detected yet.</div>';
    }

    function renderExperience(items) {
        experienceEditor.innerHTML = items.length ? items.map(function (item, index) {
            return [
                '<div class="review-item" data-experience-index="' + index + '">',
                '<div class="review-item-top"><span class="review-item-title">Experience</span><button type="button" class="review-remove" data-remove-experience="' + index + '">Remove</button></div>',
                '<div class="review-grid">',
                createInput("Company", "experience-company", item.company),
                createInput("Role", "experience-role", item.role),
                createInput("Period", "experience-period", item.period),
                createInput("Location", "experience-location", item.location),
                createTextarea("Bullets", "experience-bullets", (item.bullets || []).join("\n"), 4),
                "</div></div>"
            ].join("");
        }).join("") : '<div class="review-empty">No experience entries detected yet.</div>';
    }

    function renderProjects(items) {
        projectsEditor.innerHTML = items.length ? items.map(function (item, index) {
            return [
                '<div class="review-item" data-project-index="' + index + '">',
                '<div class="review-item-top"><span class="review-item-title">Project</span><button type="button" class="review-remove" data-remove-project="' + index + '">Remove</button></div>',
                '<div class="review-grid">',
                createInput("Project Name", "project-name", item.name),
                createInput("Stack", "project-stack", item.stack),
                createTextarea("Bullets", "project-bullets", (item.bullets || []).join("\n"), 4),
                "</div></div>"
            ].join("");
        }).join("") : '<div class="review-empty">No project entries detected yet.</div>';
    }

    function fillReviewForm(data) {
        reviewName.value = data.name || "";
        reviewTitleInput.value = data.title || "";
        reviewLocation.value = data.location || "";
        reviewEmail.value = data.email || "";
        reviewLinkedin.value = data.linkedin || "";
        reviewGithub.value = data.github || "";
        reviewSummary.value = data.summary || "";
        reviewLinks.value = (data.links || []).join("\n");
        reviewResponsibilityTitle.value = data.responsibility ? (data.responsibility.title || "") : "";
        reviewResponsibilityPeriod.value = data.responsibility ? (data.responsibility.period || "") : "";
        reviewResponsibilityOrg.value = data.responsibility ? (data.responsibility.org || "") : "";
        reviewResponsibilityBullets.value = data.responsibility ? ((data.responsibility.bullets || []).join("\n")) : "";
        reviewAchievements.value = (data.achievements || []).join("\n");
        renderSkills(data.skills || {});
        renderEducation(data.education || []);
        renderExperience(data.experience || []);
        renderProjects(data.projects || []);
    }

    function collectReviewData() {
        return {
            name: reviewName.value.trim(),
            title: reviewTitleInput.value.trim(),
            location: reviewLocation.value.trim(),
            email: reviewEmail.value.trim(),
            linkedin: reviewLinkedin.value.trim(),
            github: reviewGithub.value.trim(),
            summary: reviewSummary.value.trim(),
            links: splitLines(reviewLinks.value),
            skills: Array.from(skillsEditor.querySelectorAll(".review-item[data-skill-index]")).reduce(function (acc, item) {
                const label = item.querySelector(".skill-label").value.trim();
                const values = item.querySelector(".skill-items").value.split(",").map(function (entry) {
                    return entry.trim();
                }).filter(Boolean);
                if (label) {
                    acc[label] = values;
                }
                return acc;
            }, {}),
            education: Array.from(educationEditor.querySelectorAll(".review-item[data-education-index]")).map(function (item) {
                return {
                    school: item.querySelector(".education-school").value.trim(),
                    period: item.querySelector(".education-period").value.trim(),
                    detail: item.querySelector(".education-detail").value.trim(),
                    location: item.querySelector(".education-location").value.trim()
                };
            }).filter(function (item) {
                return item.school || item.period || item.detail || item.location;
            }),
            experience: Array.from(experienceEditor.querySelectorAll(".review-item[data-experience-index]")).map(function (item) {
                return {
                    company: item.querySelector(".experience-company").value.trim(),
                    role: item.querySelector(".experience-role").value.trim(),
                    period: item.querySelector(".experience-period").value.trim(),
                    location: item.querySelector(".experience-location").value.trim(),
                    bullets: splitLines(item.querySelector(".experience-bullets").value)
                };
            }).filter(function (item) {
                return item.company || item.role || item.period || item.location || item.bullets.length;
            }),
            projects: Array.from(projectsEditor.querySelectorAll(".review-item[data-project-index]")).map(function (item) {
                return {
                    name: item.querySelector(".project-name").value.trim(),
                    stack: item.querySelector(".project-stack").value.trim(),
                    bullets: splitLines(item.querySelector(".project-bullets").value)
                };
            }).filter(function (item) {
                return item.name || item.stack || item.bullets.length;
            }),
            responsibility: {
                title: reviewResponsibilityTitle.value.trim(),
                period: reviewResponsibilityPeriod.value.trim(),
                org: reviewResponsibilityOrg.value.trim(),
                bullets: splitLines(reviewResponsibilityBullets.value)
            },
            achievements: splitLines(reviewAchievements.value)
        };
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

    async function readApiPayload(response) {
        const contentType = response.headers.get("content-type") || "";
        if (contentType.toLowerCase().includes("application/json")) {
            return await response.json();
        }

        const text = await response.text();
        throw new Error(
            text.trim().toLowerCase().startsWith("<!doctype") || text.trim().startsWith("<")
                ? "The backend returned an HTML page instead of API JSON. Restart or redeploy the backend, then try again."
                : (text || "The backend returned an unexpected response.")
        );
    }

    function appendSkillGroup() {
        skillsEditor.insertAdjacentHTML(
            "beforeend",
            '<div class="review-item" data-skill-index="new"><div class="review-item-top"><span class="review-item-title">Skill Group</span><button type="button" class="review-remove" data-remove-skill="new">Remove</button></div><div class="review-grid">' +
            createInput("Group Label", "skill-label", "") +
            createInput("Items", "skill-items", "") +
            "</div></div>"
        );
    }

    function appendEducation() {
        educationEditor.insertAdjacentHTML(
            "beforeend",
            '<div class="review-item" data-education-index="new"><div class="review-item-top"><span class="review-item-title">Education</span><button type="button" class="review-remove" data-remove-education="new">Remove</button></div><div class="review-grid">' +
            createInput("School", "education-school", "") +
            createInput("Period", "education-period", "") +
            createInput("Detail", "education-detail", "") +
            createInput("Location", "education-location", "") +
            "</div></div>"
        );
    }

    function appendExperience() {
        experienceEditor.insertAdjacentHTML(
            "beforeend",
            '<div class="review-item" data-experience-index="new"><div class="review-item-top"><span class="review-item-title">Experience</span><button type="button" class="review-remove" data-remove-experience="new">Remove</button></div><div class="review-grid">' +
            createInput("Company", "experience-company", "") +
            createInput("Role", "experience-role", "") +
            createInput("Period", "experience-period", "") +
            createInput("Location", "experience-location", "") +
            createTextarea("Bullets", "experience-bullets", "", 4) +
            "</div></div>"
        );
    }

    function appendProject() {
        projectsEditor.insertAdjacentHTML(
            "beforeend",
            '<div class="review-item" data-project-index="new"><div class="review-item-top"><span class="review-item-title">Project</span><button type="button" class="review-remove" data-remove-project="new">Remove</button></div><div class="review-grid">' +
            createInput("Project Name", "project-name", "") +
            createInput("Stack", "project-stack", "") +
            createTextarea("Bullets", "project-bullets", "", 4) +
            "</div></div>"
        );
    }

    fileInput.addEventListener("change", function () {
        const file = fileInput.files && fileInput.files[0];
        fileName.textContent = file ? file.name : "No file selected";
        hideStatus();
        hideResultCard();
        hideReviewOverlay();
    });

    reviewClose.addEventListener("click", hideReviewOverlay);
    reviewCancel.addEventListener("click", hideReviewOverlay);
    reviewOverlay.addEventListener("click", hideReviewOverlay);
    reviewModal.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    resultClose.addEventListener("click", hideResultCard);
    resultOverlay.addEventListener("click", hideResultCard);
    resultBox.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    copyLinkButton.addEventListener("click", copyPortfolioLink);
    addSkillGroupButton.addEventListener("click", appendSkillGroup);
    addEducationButton.addEventListener("click", appendEducation);
    addExperienceButton.addEventListener("click", appendExperience);
    addProjectButton.addEventListener("click", appendProject);

    skillsEditor.addEventListener("click", function (event) {
        if (event.target.matches("[data-remove-skill]")) {
            event.target.closest(".review-item").remove();
        }
    });
    educationEditor.addEventListener("click", function (event) {
        if (event.target.matches("[data-remove-education]")) {
            event.target.closest(".review-item").remove();
        }
    });
    experienceEditor.addEventListener("click", function (event) {
        if (event.target.matches("[data-remove-experience]")) {
            event.target.closest(".review-item").remove();
        }
    });
    projectsEditor.addEventListener("click", function (event) {
        if (event.target.matches("[data-remove-project]")) {
            event.target.closest(".review-item").remove();
        }
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
        hideReviewOverlay();

        try {
            const response = await fetchWithTimeout(apiBase + "/api/parse", {
                method: "POST",
                body: body
            });
            const payload = await readApiPayload(response);

            if (!response.ok) {
                throw new Error(payload.error || "Resume parsing failed.");
            }

            latestJobId = payload.job_id;
            fillReviewForm(payload.data || {});
            showReviewOverlay();
        } catch (error) {
            const message = error.name === "AbortError"
                ? "Resume parsing timed out. Please try again."
                : (error.message || "Something went wrong while parsing the resume.");
            showStatus(message, true);
        } finally {
            submitButton.disabled = false;
        }
    });

    reviewForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        if (!latestJobId) {
            hideReviewOverlay();
            showStatus("Please upload and review a resume first.", true);
            return;
        }

        submitButton.disabled = true;
        hideStatus();

        try {
            const response = await fetchWithTimeout(apiBase + "/api/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    job_id: latestJobId,
                    data: collectReviewData()
                })
            });
            const payload = await readApiPayload(response);

            if (!response.ok) {
                throw new Error(payload.error || "Portfolio generation failed.");
            }

            latestPortfolioUrl = payload.portfolio_url;
            resultOpen.href = payload.portfolio_url;
            copyFeedback.hidden = true;
            hideReviewOverlay();
            resultOverlay.hidden = false;
            showPageLock();
        } catch (error) {
            hideReviewOverlay();
            const message = error.name === "AbortError"
                ? "Portfolio generation timed out. Please try again."
                : (error.message || "Something went wrong while generating the portfolio.");
            showStatus(message, true);
        } finally {
            submitButton.disabled = false;
        }
    });
})();
