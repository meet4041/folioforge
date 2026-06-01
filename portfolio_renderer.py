import html
import re
import unicodedata
from pathlib import Path

NAV_ITEMS = [
    ("Home", "index.html"),
    ("About", "about.html"),
    ("Skills", "skills.html"),
    ("Journey", "journey.html"),
    ("Projects", "projects.html"),
    ("Contact", "contact.html"),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "portfolio"


def escape(value: str) -> str:
    return html.escape(value or "")


def skill_badges(items: list[str]) -> str:
    return "".join(f'<span class="pill">{escape(item)}</span>' for item in items)


def bullets(items: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items if item)


def nav(active: str, name: str) -> str:
    links = []
    for label, href in NAV_ITEMS:
        current = ' aria-current="page"' if href == active else ""
        links.append(f'<a href="{href}"{current}>{escape(label)}</a>')
    return f"""
        <nav class="topbar">
            <div class="nav-actions">
                <div class="nav-links">
                    {''.join(links)}
                </div>
            </div>
        </nav>
    """


def footer(name: str) -> str:
    return f"""
        <footer class="site-footer">
            <div>
                <p class="footer-title">{escape(name)}</p>
            </div>
            <div class="footer-meta">
                <div class="footer-contact">
                    <a href="mailto:meetgandhi4041@gmail.com" aria-label="Email" title="Email">@</a>
                    <a href="https://linkedin.com/in/meet4041" aria-label="LinkedIn" title="LinkedIn">in</a>
                    <a href="https://github.com/meet4041" aria-label="GitHub" title="GitHub" class="github-link">
                        <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false" class="github-mark">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2 .37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.58.82-2.14-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.65 7.65 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.14 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/>
                        </svg>
                    </a>
                </div>
            </div>
        </footer>
    """


def page_shell(title: str, active: str, name: str, content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="page-bg"></div>
    <div class="shell">
        {nav(active, name)}
        {content}
        {footer(name)}
    </div>
</body>
</html>
"""


def render_education_cards(data: dict) -> str:
    cards = []
    for item in data["education"]:
        cards.append(
            f"""
            <article class="card timeline-card">
                <div class="card-head">
                    <div>
                        <p class="eyebrow">{escape(item['period'])}</p>
                        <h3>{escape(item['school'])}</h3>
                    </div>
                    <span class="tag">{escape(item['location'])}</span>
                </div>
                <p class="muted">{escape(item['detail'])}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_experience_cards(data: dict) -> str:
    cards = []
    for item in data["experience"]:
        cards.append(
            f"""
            <article class="card timeline-card">
                <div class="card-head">
                    <div>
                        <p class="eyebrow">{escape(item['period'])}</p>
                        <h3>{escape(item['company'])}</h3>
                        <p class="muted">{escape(item['role'])}</p>
                    </div>
                    <span class="tag">{escape(item['location'])}</span>
                </div>
                <ul class="bullets">{bullets(item['bullets'])}</ul>
            </article>
            """
        )
    return "\n".join(cards)


def render_project_cards(data: dict) -> str:
    cards = []
    for item in data["projects"]:
        cards.append(
            f"""
            <article class="card">
                <div class="card-head">
                    <div>
                        <h3>{escape(item['name'])}</h3>
                    </div>
                </div>
                <p class="tagline">{escape(item['stack'])}</p>
                <ul class="bullets">{bullets(item['bullets'])}</ul>
            </article>
            """
        )
    return "\n".join(cards)


def render_skill_cards(data: dict) -> str:
    groups = []
    for label, values in data["skills"].items():
        groups.append(
            f"""
            <article class="card skill-card skill-card--accent">
                <h3>{escape(label)}</h3>
                <div class="pill-row">{skill_badges(values)}</div>
            </article>
            """
        )
    if not groups:
        groups.append(
            """
            <article class="card skill-card skill-card--accent">
                <h3>Skills</h3>
                <p class="muted">No structured skills section was detected in this PDF.</p>
            </article>
            """
        )
    return "\n".join(groups)


def render_home(data: dict) -> str:
    title = escape(data["title"])
    summary = escape(data["summary"])
    content = f"""
        <header class="hero">
            <div>
                <h1 class="typewriter"><span>{escape(data['name'])}</span></h1>
                <p class="subtitle">{title}</p>
                <p class="lede">{summary}</p>
                <div class="cta-row">
                    <a class="button primary" href="about.html">View About</a>
                    <a class="button secondary" href="projects.html">See Projects</a>
                </div>
            </div>
            <div class="hero-card">
                <div>
                    <p class="eyebrow">At a glance</p>
                    <h2 class="hero-card-title">Builder</h2>
                    <p class="hero-card-copy">AI/ML, web, deployment.</p>
                </div>
                <div class="hero-strip">
                    <span>{len(data['experience']) or 0} experience roles</span>
                    <span>{len(data['projects']) or 0} projects</span>
                    <span>{len(data['skills']) or 0} skill groups</span>
                </div>
            </div>
        </header>

        <section class="section">
            <div class="section-head">
                <p class="eyebrow">Quick Links</p>
                <h2>Explore the portfolio</h2>
            </div>
            <div class="quick-links-grid">
                <a class="card link-card" href="about.html">
                    <p class="link-kicker">01</p>
                    <h3>About</h3>
                    <p class="muted">A short overview of who I am and what I focus on.</p>
                    <span class="link-arrow">→</span>
                </a>
                <a class="card link-card" href="skills.html">
                    <p class="link-kicker">02</p>
                    <h3>Skills</h3>
                    <p class="muted">Programming languages, tools, frameworks, and interests.</p>
                    <span class="link-arrow">→</span>
                </a>
                <a class="card link-card" href="journey.html">
                    <p class="link-kicker">03</p>
                    <h3>Journey</h3>
                    <p class="muted">Education, experience, responsibility, and achievements.</p>
                    <span class="link-arrow">→</span>
                </a>
                <a class="card link-card" href="projects.html">
                    <p class="link-kicker">04</p>
                    <h3>Projects</h3>
                    <p class="muted">Selected work from the resume.</p>
                    <span class="link-arrow">→</span>
                </a>
            </div>
        </section>
    """
    return page_shell(f"{escape(data['name'])} | Portfolio", "index.html", data["name"], content)


def render_about(data: dict) -> str:
    skill_rows = []
    for label, values in list(data["skills"].items())[:3]:
        chips = "".join(f'<span class="pill">{escape(item)}</span>' for item in values[:4])
        skill_rows.append(
            f"""
            <div class="skill-row">
                <span>{escape(label)}</span>
                <div class="skill-row-pills">{chips}</div>
            </div>
            """
        )
    skill_rows_html = "".join(skill_rows)
    content = f"""
        <section class="section about-section">
            <div class="section-head">
                <h1 class="page-title about-title typewriter">A focused builder with an ML and web background</h1>
            </div>
            <div class="grid grid-2 about-grid">
                <article class="card profile-card about-main">
                    <div class="profile-head">
                        <div>
                            <h2>About Me</h2>
                        </div>
                        <span class="profile-pill">AI/ML + Web</span>
                    </div>
                    <p class="profile-summary">{escape(data['summary'])}</p>
                    <div class="about-quote">
                        Turning ideas into clear, usable systems with a calm, polished finish.
                    </div>
                    <p class="profile-note">
                        I like turning ideas into usable systems, whether that means model deployment,
                        clean UI, or an end-to-end workflow that actually works in the real world.
                    </p>
                    <div class="profile-points">
                        <div class="profile-point">
                            <span>Focus</span>
                            <strong>Practical problem solving</strong>
                        </div>
                        <div class="profile-point">
                            <span>Style</span>
                            <strong>Clean and polished delivery</strong>
                        </div>
                    </div>
                    <div class="hero-tags">
                        <span class="pill">Research-minded</span>
                        <span class="pill">Product-aware</span>
                        <span class="pill">Execution-focused</span>
                    </div>
                </article>
                <article class="card about-aside">
                    <h2>Snapshot</h2>
                    <div class="mini-metrics">
                        <div class="mini-metric">
                            <span>Focus</span>
                            <strong>ML + Web</strong>
                        </div>
                        <div class="mini-metric">
                            <span>Style</span>
                            <strong>Clean delivery</strong>
                        </div>
                        <div class="mini-metric">
                            <span>Approach</span>
                            <strong>Practical build</strong>
                        </div>
                    </div>
                    <div class="skill-rows">
                        {skill_rows_html}
                    </div>
                </article>
            </div>
            <div class="grid">
                <article class="card about-education">
                    <h2>Education</h2>
                    {render_education_cards(data)}
                </article>
            </div>
        </section>
    """
    return page_shell(f"About | {escape(data['name'])}", "about.html", data["name"], content)


def render_skills(data: dict) -> str:
    skill_total = sum(len(values) for values in data["skills"].values())
    content = f"""
        <section class="section">
            <div class="section-head">
                <h1 class="page-title typewriter">Toolkit that ships</h1>
            </div>
            <div class="skill-summary">
                <span>{len(data['skills']) or 0} groups</span>
                <span>{skill_total} total tools</span>
                <span>AI/ML + web focused</span>
            </div>
            <div class="grid grid-2">
                {render_skill_cards(data)}
            </div>
        </section>
    """
    return page_shell(f"Skills | {escape(data['name'])}", "skills.html", data["name"], content)


def render_journey(data: dict) -> str:
    responsibility = data["responsibility"]
    content = f"""
        <section class="section">
            <div class="section-head">
                <h1 class="page-title typewriter">Education, work, and leadership</h1>
            </div>
            <div class="journey-grid">
                <article class="card journey-panel">
                    <h2>Education</h2>
                    {render_education_cards(data)}
                </article>
                <article class="card journey-panel">
                    <h2>Experience</h2>
                    {render_experience_cards(data)}
                </article>
            </div>
        </section>

        <section class="section">
            <div class="journey-grid">
                <article class="card journey-panel journey-feature">
                    <h2>Position of responsibility</h2>
                    <p class="tagline">{escape(responsibility['title'])} - {escape(responsibility['period'])}</p>
                    <p class="muted">{escape(responsibility['org'])}</p>
                    <ul class="bullets">{bullets(responsibility['bullets'])}</ul>
                </article>
                <article class="card journey-panel journey-feature">
                    <h2>Achievements</h2>
                    <ul class="bullets">{bullets(data['achievements'])}</ul>
                </article>
            </div>
        </section>
    """
    return page_shell(f"Journey | {escape(data['name'])}", "journey.html", data["name"], content)


def render_projects(data: dict) -> str:
    content = f"""
        <section class="section">
            <div class="section-head">
                <h1 class="page-title typewriter">Selected work</h1>
            </div>
            <div class="grid grid-2">
                {render_project_cards(data)}
            </div>
        </section>
    """
    return page_shell(f"Projects | {escape(data['name'])}", "projects.html", data["name"], content)


def render_contact(data: dict) -> str:
    recipient_email = escape(data["email"])
    content = f"""
        <section class="section">
            <div class="section-head">
                <h1 class="page-title typewriter">Let's connect</h1>
            </div>
            <div class="grid">
                <article class="card contact-card">
                    <h2>Send a message</h2>
                    <p class="muted">
                        Fill this out and it will open your email app with the message pre-filled.
                    </p>
                    <form id="contact-form" class="contact-form">
                        <div id="contact-error" class="contact-error" role="alert" aria-live="polite" hidden></div>
                        <label>
                            <span>Name</span>
                            <input type="text" name="name" placeholder="Your name" minlength="2" maxlength="60" required>
                        </label>
                        <label>
                            <span>Email</span>
                            <input type="email" name="email" placeholder="Your email" maxlength="120" required>
                        </label>
                        <label>
                            <span>Subject</span>
                            <input type="text" name="subject" placeholder="Project, internship, collaboration..." minlength="3" maxlength="120" required>
                        </label>
                        <label>
                            <span>Message</span>
                            <textarea name="message" rows="6" placeholder="Write your message here..." minlength="20" maxlength="3000" required></textarea>
                        </label>
                        <button class="button primary contact-submit" type="submit">Send</button>
                    </form>
                </article>
            </div>
        </section>
        <script>
        (function() {{
            const form = document.getElementById('contact-form');
            const errorBox = document.getElementById('contact-error');
            if (!form) return;

            const fields = Array.from(form.querySelectorAll('input, textarea'));

            function showError(message) {{
                if (!errorBox) return;
                errorBox.textContent = message;
                errorBox.hidden = false;
            }}

            function clearError() {{
                if (!errorBox) return;
                errorBox.textContent = '';
                errorBox.hidden = true;
            }}

            function setInvalidField(field, isInvalid) {{
                field.setAttribute('aria-invalid', isInvalid ? 'true' : 'false');
            }}

            function resetFieldStates() {{
                fields.forEach(function(field) {{
                    setInvalidField(field, false);
                }});
            }}

            fields.forEach(function(field) {{
                field.addEventListener('input', function() {{
                    setInvalidField(field, false);
                    clearError();
                }});
            }});

            form.addEventListener('submit', function(event) {{
                event.preventDefault();
                clearError();
                resetFieldStates();

                const formData = new FormData(form);
                const senderName = String(formData.get('name') || '').trim();
                const senderEmail = String(formData.get('email') || '').trim();
                const subject = String(formData.get('subject') || '').trim();
                const message = String(formData.get('message') || '').trim();

                const namePattern = /^[A-Za-z][A-Za-z\\s.'-]*$/;
                if (senderName.length < 2 || !namePattern.test(senderName)) {{
                    setInvalidField(form.elements.name, true);
                    showError('Please enter a valid name using letters only.');
                    form.elements.name.focus();
                    return;
                }}

                const emailPattern = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                if (!emailPattern.test(senderEmail)) {{
                    setInvalidField(form.elements.email, true);
                    showError('Please enter a valid email address.');
                    form.elements.email.focus();
                    return;
                }}

                if (subject.length < 3) {{
                    setInvalidField(form.elements.subject, true);
                    showError('Please add a subject for your message.');
                    form.elements.subject.focus();
                    return;
                }}

                if (message.length < 20) {{
                    setInvalidField(form.elements.message, true);
                    showError('Please write at least 20 characters in your message.');
                    form.elements.message.focus();
                    return;
                }}

                const body = [
                    `Name: ${{senderName}}`,
                    `Email: ${{senderEmail}}`,
                    '',
                    message
                ].join('\\n');
                const mailtoUrl = `mailto:{recipient_email}?subject=${{encodeURIComponent(subject)}}&body=${{encodeURIComponent(body)}}`;
                window.location.href = mailtoUrl;
            }});
        }})();
        </script>
    """
    return page_shell(f"Contact | {escape(data['name'])}", "contact.html", data["name"], content)


def create_css() -> str:
    return """*{box-sizing:border-box}
html{scroll-behavior:smooth}
:root{
    --bg:#0b1020;
    --bg-soft:#12192f;
    --surface:rgba(16,20,35,.72);
    --surface-strong:rgba(16,20,35,.88);
    --surface-light:rgba(255,255,255,.08);
    --border:rgba(255,255,255,.10);
    --text:#f6efe7;
    --muted:rgba(246,239,231,.72);
    --accent:#5aa9ff;
    --accent-2:#7dd3fc;
    --accent-3:#60a5fa;
    --shadow:0 24px 80px rgba(0,0,0,.28);
    --title-font:"Georgia","Times New Roman",serif;
}
body{
    margin:0;
    color:var(--text);
    background:
        radial-gradient(circle at top left, rgba(90,169,255,.18), transparent 24%),
        radial-gradient(circle at top right, rgba(125,211,252,.16), transparent 22%),
        radial-gradient(circle at 70% 20%, rgba(96,165,250,.10), transparent 18%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg-soft) 55%, #0e1426 100%);
    font-family:"Segoe UI","Trebuchet MS",Arial,sans-serif;
    line-height:1.6;
}
a{color:inherit}
::selection{
    background:rgba(90,169,255,.35);
    color:#fff;
}
.page-bg{
    position:fixed;
    inset:0;
    pointer-events:none;
    background:
        linear-gradient(120deg, rgba(255,255,255,.03), transparent 38%),
        radial-gradient(circle at 20% 20%, rgba(255,255,255,.06), transparent 22%);
    opacity:.9;
}
.shell{
    width:min(1160px, calc(100% - 32px));
    margin:0 auto;
    padding:24px 0 64px;
    position:relative;
    z-index:1;
}
.topbar{
    display:flex;
    justify-content:center;
    align-items:center;
    gap:16px;
    padding:10px 0 24px;
    position:sticky;
    top:0;
    z-index:10;
}
.brand{
    font-size:1rem;
    font-weight:700;
    letter-spacing:.18em;
    text-transform:uppercase;
    text-decoration:none;
    color:#fff;
}
.nav-actions{
    display:flex;
    align-items:center;
    gap:14px;
    flex-wrap:wrap;
    justify-content:center;
}
.nav-links{
    display:flex;
    gap:24px;
    flex-wrap:wrap;
}
.nav-links a{
    text-decoration:none;
    color:rgba(246,239,231,.76);
    padding:6px 2px 8px;
    font-size:.95rem;
    transition:color .2s ease, opacity .2s ease;
}
.nav-links a:hover{
    color:#fff;
}
.nav-links a[aria-current="page"]{
    color:#fff;
    border-bottom:1px solid rgba(90,169,255,.85);
}
.hero{
    display:grid;
    grid-template-columns:minmax(0,1.25fr) minmax(300px,.85fr);
    gap:24px;
    align-items:stretch;
    padding:36px 0 12px;
}
.hero h1{
    margin:0;
    font-size:clamp(3rem, 7vw, 5.8rem);
    line-height:.95;
    font-family:var(--title-font);
    font-weight:600;
    letter-spacing:-.04em;
}
.page-title{
    margin:0;
    font-size:clamp(2rem, 3.6vw, 3.2rem);
    line-height:.92;
    font-family:var(--title-font);
    font-weight:600;
    letter-spacing:-.03em;
}
.typewriter{
    display:inline-block;
    white-space:nowrap;
    opacity:0;
    transform:translateY(6px);
    clip-path:inset(0 100% 0 0);
    animation:titleReveal 3.4s cubic-bezier(.22, 1, .36, 1) .2s forwards;
}
.typewriter span{
    display:inline-block;
    padding-right:0;
}
.about-title{
    font-size:clamp(2rem, 3.6vw, 3.2rem) !important;
    max-width:none;
    width:100%;
    line-height:.92;
    white-space:nowrap;
    font-family:var(--title-font) !important;
}
.about-lede{
    max-width:72ch;
    margin:0;
}
.skills-intro{
    max-width:68ch;
    margin:4px 0 0;
}
.skill-summary{
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    margin:14px 0 18px;
}
.skill-summary span{
    display:inline-flex;
    align-items:center;
    padding:10px 14px;
    border-radius:999px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.08);
    color:rgba(246,239,231,.86);
    font-size:.86rem;
    letter-spacing:.02em;
}
.journey-intro{
    margin:4px 0 0;
    max-width:68ch;
    color:var(--muted);
}
.journey-grid{
    display:grid;
    grid-template-columns:repeat(2, minmax(0, 1fr));
    gap:24px;
}
.journey-panel{
    display:flex;
    flex-direction:column;
    gap:14px;
    background:
        linear-gradient(180deg, rgba(90,169,255,.06), transparent 30%),
        rgba(255,255,255,.03);
    border-color:rgba(255,255,255,.10);
    box-shadow:0 18px 50px rgba(0,0,0,.12);
}
.journey-feature{
    min-height:100%;
}
.timeline-card{
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.08);
    border-radius:20px;
    padding:20px;
    position:relative;
}
.timeline-card::before{
    content:"";
    position:absolute;
    left:20px;
    top:20px;
    width:12px;
    height:12px;
    border-radius:999px;
    background:linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    box-shadow:0 0 0 6px rgba(90,169,255,.10);
    opacity:.95;
}
.timeline-card .card-head,
.timeline-card .muted,
.timeline-card .bullets{
    padding-left:26px;
}
.timeline-card h3{
    margin-bottom:6px;
    font-size:1.18rem;
}
.timeline-card .tag{
    align-self:flex-start;
    white-space:nowrap;
}
.timeline-card .muted{
    margin-top:0;
    line-height:1.7;
}
.about-grid{
    align-items:start;
    gap:28px;
}
.profile-card{
    display:flex;
    flex-direction:column;
    gap:18px;
    background:
        linear-gradient(180deg, rgba(90,169,255,.06), transparent 28%),
        rgba(255,255,255,.03);
    border-color:rgba(255,255,255,.10);
    position:relative;
    overflow:hidden;
}
.profile-card::before{
    content:"";
    position:absolute;
    inset:0 auto auto 0;
    width:100%;
    height:1px;
    background:linear-gradient(90deg, rgba(201,164,106,.42), rgba(90,169,255,.24), transparent);
}
.about-main{
    padding-top:24px;
}
.about-education{
    margin-top:20px;
}
.profile-head{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:16px;
}
.profile-head h2{
    margin:0;
    font-size:1.75rem;
    font-family:var(--title-font);
}
.profile-pill{
    display:inline-flex;
    align-items:center;
    padding:8px 12px;
    border-radius:999px;
    background:rgba(90,169,255,.12);
    border:1px solid rgba(90,169,255,.22);
    color:#7dd3fc;
    font-size:.8rem;
    letter-spacing:.08em;
    text-transform:uppercase;
}
.profile-summary{
    margin:0;
    font-size:1.02rem;
    color:#fff;
    line-height:1.75;
}
.about-quote{
    padding:16px 18px;
    border-left:2px solid rgba(201,164,106,.5);
    background:rgba(255,255,255,.03);
    color:rgba(246,239,231,.86);
    border-radius:0 16px 16px 0;
    font-style:italic;
    line-height:1.65;
}
.profile-note{
    margin:0;
    color:var(--muted);
    line-height:1.7;
}
.profile-points{
    display:grid;
    grid-template-columns:repeat(2, minmax(0, 1fr));
    gap:12px;
}
.profile-point{
    padding:14px 16px;
    border-radius:18px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.08);
}
.profile-point span{
    display:block;
    margin-bottom:4px;
    font-size:.78rem;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:rgba(246,239,231,.62);
}
.profile-point strong{
    display:block;
    font-size:1rem;
    color:#fff;
    font-weight:600;
}
.about-aside{
    display:flex;
    flex-direction:column;
    gap:18px;
}
.about-aside h2,
.about-education h2{
    margin:0;
    font-size:1.35rem;
}
.mini-metrics{
    display:grid;
    grid-template-columns:repeat(3, minmax(0, 1fr));
    gap:10px;
}
.mini-metric{
    padding:14px 14px 12px;
    border-radius:16px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.08);
}
.mini-metric span{
    display:block;
    font-size:.72rem;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:rgba(246,239,231,.62);
    margin-bottom:6px;
}
.mini-metric strong{
    display:block;
    font-size:.98rem;
    color:#fff;
    font-weight:600;
}
.skill-rows{
    display:flex;
    flex-direction:column;
    gap:12px;
}
.skill-row{
    padding-top:12px;
    border-top:1px solid rgba(255,255,255,.08);
}
.skill-row:first-child{
    padding-top:0;
    border-top:0;
}
.skill-row > span{
    display:block;
    margin-bottom:10px;
    font-size:.78rem;
    letter-spacing:.16em;
    text-transform:uppercase;
    color:#e7c98a;
}
.skill-row-pills{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
}
.skill-card{
    min-height:100%;
}
.skill-card--accent{
    background:
        radial-gradient(circle at top right, rgba(90,169,255,.12), transparent 30%),
        linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
    border-color:rgba(90,169,255,.16);
}
.subtitle{
    margin:14px 0 0;
    font-size:1.15rem;
    color:#7dd3fc;
    letter-spacing:.02em;
}
.lede,.muted{
    color:var(--muted);
}
.eyebrow{
    margin:0 0 12px;
    text-transform:uppercase;
    letter-spacing:.2em;
    font-size:.74rem;
    color:#7dd3fc;
}
.cta-row{
    display:flex;
    gap:12px;
    flex-wrap:wrap;
    margin-top:24px;
}
.button{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-height:48px;
    padding:0 18px;
    border-radius:16px;
    text-decoration:none;
    border:1px solid var(--border);
    transition:transform .2s ease, border-color .2s ease, background .2s ease, color .2s ease;
}
.button:hover{
    transform:translateY(-1px);
}
.button.primary{
    background:linear-gradient(135deg, var(--accent) 0%, var(--accent-3) 100%);
    color:#0b1020;
    font-weight:700;
    border-color:transparent;
}
.button.secondary{
    background:rgba(255,255,255,.04);
    color:#fff;
}
.hero-card,.card{
    border:1px solid var(--border);
    background:linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
    backdrop-filter:blur(16px);
    border-radius:24px;
    box-shadow:var(--shadow);
}
.hero-card{
    padding:24px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    gap:18px;
    position:relative;
    overflow:hidden;
}
.hero-card::after,
.card::before{
    content:"";
    position:absolute;
    inset:auto auto -30% -20%;
    width:180px;
    height:180px;
    border-radius:50%;
    background:radial-gradient(circle, rgba(90,169,255,.22), transparent 65%);
    pointer-events:none;
}
.stats{
    display:grid;
    grid-template-columns:1fr;
    gap:16px;
}
.hero-card-title{
    margin:0 0 10px;
    font-family:var(--title-font);
    font-size:1.45rem;
    line-height:1.18;
    letter-spacing:-.02em;
}
.hero-card-copy{
    margin:0;
    color:var(--muted);
}
.hero-tags{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
}
.hero-strip{
    display:flex;
    gap:12px;
    flex-wrap:wrap;
    color:rgba(246,239,231,.78);
    font-size:.94rem;
}
.hero-strip span{
    display:inline-flex;
    align-items:center;
    gap:8px;
}
.hero-strip span + span::before{
    content:"•";
    margin-right:12px;
    color:rgba(255,255,255,.35);
}
.section{
    padding:40px 0 0;
}
.section-head{
    margin-bottom:18px;
    position:relative;
}
.section-head::after{
    content:"";
    display:block;
    width:88px;
    height:3px;
    border-radius:999px;
    margin-top:12px;
    background:linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
}
.section-head h2{
    margin:0;
    font-size:clamp(1.45rem, 3vw, 2.1rem);
    font-family:var(--title-font);
    font-weight:600;
    letter-spacing:-.02em;
}
.grid{
    display:grid;
    gap:18px;
}
.grid-2{
    grid-template-columns:repeat(2, minmax(0, 1fr));
}
.grid-3{
    grid-template-columns:repeat(3, minmax(0, 1fr));
}
.quick-links-grid{
    display:grid;
    grid-template-columns:repeat(2, minmax(0, 1fr));
    gap:18px;
}
.card{
    padding:22px;
    text-decoration:none;
    position:relative;
    overflow:hidden;
}
.link-card{
    transition:transform .22s ease, border-color .22s ease, background .22s ease;
    min-height:180px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}
.link-card:hover{
    transform:translateY(-4px);
    border-color:rgba(90,169,255,.4);
    background:linear-gradient(180deg, rgba(255,255,255,.12), rgba(255,255,255,.06));
}
.link-kicker{
    margin:0;
    font-size:.74rem;
    letter-spacing:.22em;
    color:rgba(246,239,231,.46);
}
.link-arrow{
    display:inline-flex;
    align-self:flex-end;
    font-size:1.4rem;
    color:#7dd3fc;
}
.card h2,.card h3{
    margin:0 0 10px;
    font-family:var(--title-font);
    font-weight:600;
    letter-spacing:-.02em;
}
.contact-card{
    display:flex;
    flex-direction:column;
    gap:14px;
}
.contact-form{
    display:flex;
    flex-direction:column;
    gap:14px;
}
.contact-error{
    border:1px solid rgba(239,68,68,.35);
    background:rgba(239,68,68,.10);
    color:#fecaca;
    border-radius:16px;
    padding:12px 14px;
    font-size:.95rem;
    line-height:1.5;
}
.contact-form label{
    display:flex;
    flex-direction:column;
    gap:8px;
}
.contact-form span{
    font-size:.78rem;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:rgba(246,239,231,.62);
}
.contact-form input,
.contact-form textarea{
    width:100%;
    border-radius:16px;
    border:1px solid rgba(255,255,255,.10);
    background:rgba(255,255,255,.04);
    color:var(--text);
    padding:14px 16px;
    font:inherit;
    outline:none;
    transition:border-color .2s ease, background .2s ease, box-shadow .2s ease;
}
.contact-form input::placeholder,
.contact-form textarea::placeholder{
    color:rgba(246,239,231,.42);
}
.contact-form input:focus,
.contact-form textarea:focus{
    border-color:rgba(90,169,255,.42);
    background:rgba(255,255,255,.06);
    box-shadow:0 0 0 4px rgba(90,169,255,.10);
}
.contact-form [aria-invalid="true"]{
    border-color:rgba(239,68,68,.55);
    box-shadow:0 0 0 4px rgba(239,68,68,.10);
}
.contact-submit{
    width:fit-content;
    min-width:150px;
}
.card-head{
    display:flex;
    justify-content:space-between;
    gap:16px;
    align-items:flex-start;
}
.tag,.pill{
    display:inline-flex;
    align-items:center;
    border-radius:999px;
    background:rgba(90,169,255,.12);
    border:1px solid rgba(90,169,255,.22);
    color:#7dd3fc;
    padding:6px 10px;
    font-size:.82rem;
}
.tagline{
    margin:0 0 14px;
    color:#7dd3fc;
    font-weight:600;
}
.bullets{
    margin:14px 0 0;
    padding-left:20px;
    color:rgba(246,239,231,.82);
}
.bullets li + li{margin-top:8px}
.timeline-card + .timeline-card{
    margin-top:18px;
}
.pill-row{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
}
.site-footer{
    margin-top:44px;
    padding:24px 4px 8px;
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:20px;
    flex-wrap:wrap;
    position:relative;
    background:linear-gradient(180deg, rgba(201,164,106,.05), transparent 72%);
}
.site-footer::before{
    content:"";
    position:absolute;
    top:0;
    left:50%;
    width:100vw;
    height:1px;
    background:linear-gradient(90deg, transparent 0%, rgba(201,164,106,.30) 18%, rgba(90,169,255,.22) 50%, rgba(201,164,106,.30) 82%, transparent 100%);
    transform:translateX(-50%);
}
.footer-title{
    margin:0 0 4px;
    font-family:var(--title-font);
    font-size:1.05rem;
    color:#fbf4e8;
}
.footer-meta{
    display:flex;
    flex-direction:column;
    align-items:flex-end;
    gap:12px;
}
.footer-contact{
    display:flex;
    gap:14px;
    flex-wrap:wrap;
    align-items:center;
    justify-content:flex-end;
}
.footer-contact a{
    display:inline-flex;
    align-items:center;
    gap:6px;
    text-decoration:none;
    color:#fff;
    width:40px;
    height:40px;
    justify-content:center;
    border-radius:999px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.08);
    transition:transform .2s ease, border-color .2s ease, color .2s ease;
    font-size:1rem;
    font-weight:600;
}
.footer-contact a.github-link{
    font-size:0;
}
.footer-contact a .github-mark{
    width:19px;
    height:19px;
    display:block;
    fill:currentColor;
}
.footer-contact a:hover{
    transform:translateY(-1px);
    border-color:rgba(201,164,106,.42);
    color:#e7c98a;
}
@media (max-width: 900px){
    .journey-grid{
        grid-template-columns:1fr;
    }
    .about-title{
        white-space:normal;
    }
    .hero,.grid-2,.grid-3{
        grid-template-columns:1fr;
    }
    .quick-links-grid{
        grid-template-columns:1fr;
    }
    .topbar{
        flex-direction:column;
        align-items:flex-start;
        position:static;
        background:transparent;
        backdrop-filter:none;
    }
    .nav-actions{
        justify-content:flex-start;
    }
    .site-footer{
        flex-direction:column;
    }
    .footer-meta{
        align-items:flex-start;
    }
    .footer-contact{
        justify-content:flex-start;
    }
}
@keyframes titleReveal{
    from{
        opacity:0;
        transform:translateY(6px);
        clip-path:inset(0 100% 0 0);
    }
    to{
        opacity:1;
        transform:translateY(0);
        clip-path:inset(0 0 0 0);
    }
}
@media (prefers-reduced-motion: reduce){
    .typewriter{
        animation:none;
        opacity:1;
        transform:none;
        clip-path:none;
    }
}
"""


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_page(output_dir: Path, filename: str, content: str) -> None:
    (output_dir / filename).write_text(content, encoding="utf-8")


def generate_site(data: dict, output_dir: Path) -> None:
    ensure_output_dir(output_dir)
    (output_dir / "style.css").write_text(create_css(), encoding="utf-8")
    write_page(output_dir, "index.html", render_home(data))
    write_page(output_dir, "about.html", render_about(data))
    write_page(output_dir, "skills.html", render_skills(data))
    write_page(output_dir, "journey.html", render_journey(data))
    write_page(output_dir, "projects.html", render_projects(data))
    write_page(output_dir, "contact.html", render_contact(data))
