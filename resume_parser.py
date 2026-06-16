import re
import unicodedata
from pathlib import Path

import fitz

SECTION_ALIASES = {
    "about": ["about"],
    "summary": ["summary"],
    "education": ["education"],
    "experience": ["experience"],
    "skills": ["skills", "technical skills"],
    "projects": ["projects"],
    "responsibility": ["position of responsibility", "responsibility"],
    "achievements": ["achievements"],
}

MONTH_PATTERN = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\r", "\n")
    normalized = normalized.replace("\u00a0", " ")
    normalized = normalized.replace("\ufffd", "-")
    normalized = normalized.replace("•", "-")
    normalized = normalized.replace("‣", "-")
    normalized = normalized.replace("∙", "-")
    normalized = normalized.replace("·", "-")
    normalized = normalized.replace("â€¢", "- ")
    normalized = normalized.replace("Â·", "- ")
    normalized = normalized.replace("Â§", "")
    normalized = normalized.replace("â€“", "-")
    normalized = normalized.replace("â€”", "-")
    normalized = normalized.replace("ï¬", "fi").replace("ï¬‚", "fl").replace("ï¬€", "ff")
    normalized = normalized.replace("Ã¢â‚¬Â", '"').replace("Ã¢â‚¬Å“", '"').replace("Ã¢â‚¬â„¢", "'")
    normalized = normalized.replace("Ã¢â‚¬â€œ", "-").replace("Ã¢â‚¬â€", "-").replace("Ã¢Ë†Â¼", "~")
    normalized = normalized.replace("âˆ¼", "~")
    try:
        repaired = normalized.encode("latin1").decode("utf-8")
        normalized = repaired
    except UnicodeError:
        pass
    return normalized


def extract_pdf_text(pdf_path: Path) -> str:
    text = []
    doc = fitz.open(pdf_path)
    for page in doc:
        text.append(page.get_text())
    doc.close()
    return "\n".join(text)


def clean_lines(text: str) -> list[str]:
    lines = []
    for raw_line in normalize_text(text).splitlines():
        line = " ".join(raw_line.strip().split())
        if line:
            lines.append(line)
    return lines


def normalized_label(line: str) -> str:
    return re.sub(r"[^a-z]+", "", line.lower())


def is_heading(line: str) -> str | None:
    label = normalized_label(line.rstrip(":"))
    for canonical, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if label == normalized_label(alias):
                return canonical
    return None


def looks_like_email(line: str) -> bool:
    return bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", line))


def looks_like_url(line: str) -> bool:
    return bool(re.search(r"(https?://|www\.)\S+", line)) or "linkedin.com" in line or "github.com" in line


def split_pipe_parts(line: str) -> list[str]:
    return [part.strip() for part in line.split("|") if part.strip()]


def looks_like_date(line: str) -> bool:
    lowered = line.lower()
    if "present" in lowered:
        return True
    if re.fullmatch(r"\d{4}", line.strip()):
        return True
    if re.search(r"\b\d{4}\s*[-–—]\s*(?:present|\d{4})\b", lowered):
        return True
    if re.search(r"\b\d{4}\b", line) and ("-" in line or "to" in lowered):
        return True
    if re.search(rf"\b{MONTH_PATTERN}\b", lowered) and re.search(r"\b\d{4}\b", line):
        return True
    if re.search(rf"\b{MONTH_PATTERN}\b\s+\d{{4}}\s*[-–—]\s*(?:{MONTH_PATTERN}\s+\d{{4}}|present)", lowered):
        return True
    return False


def looks_like_bullet(line: str) -> bool:
    return line.startswith(("-", "*", "•", "‣", "∙", "·"))


def strip_bullet(line: str) -> str:
    return line.lstrip("-* ").strip()


def split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections = {
        "intro": [],
        "summary": [],
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "responsibility": [],
        "achievements": [],
    }
    current = "intro"
    for line in lines:
        heading = is_heading(line)
        if heading:
            current = heading
            continue
        sections[current].append(line)
    return sections


def first_non_contact(lines: list[str]) -> str:
    for line in lines:
        if not looks_like_email(line) and not looks_like_url(line) and not is_heading(line):
            return line
    return "Portfolio Owner"


def detect_title(lines: list[str], name: str) -> str:
    seen_name = False
    for line in lines:
        if not seen_name:
            if line == name:
                seen_name = True
            continue
        if not looks_like_email(line) and not looks_like_url(line) and not is_heading(line):
            return line
    return ""


def extract_location(lines: list[str]) -> str:
    for line in lines:
        if "|" not in line:
            continue
        for part in reversed(split_pipe_parts(line)):
            if looks_like_email(part) or looks_like_url(part) or re.search(r"\+?\d[\d\s-]{7,}", part):
                continue
            return part
    return ""


def extract_contacts(lines: list[str]) -> dict[str, str]:
    email = ""
    linkedin = ""
    github = ""
    for line in lines:
        if not email:
            match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", line)
            if match:
                email = match.group(0)
        if not linkedin:
            linkedin_match = re.search(r"((?:https?://)?(?:www\.)?linkedin\.com/[^\s|),;]+)", line, re.I)
            if linkedin_match:
                linkedin = linkedin_match.group(1)
                if not linkedin.startswith("http"):
                    linkedin = f"https://{linkedin}"
        if not github:
            github_match = re.search(r"((?:https?://)?(?:www\.)?github\.com/[^\s|),;]+)", line, re.I)
            if github_match:
                github = github_match.group(1)
                if not github.startswith("http"):
                    github = f"https://{github}"
    return {
        "email": email,
        "linkedin": linkedin,
        "github": github,
    }


def extract_links(lines: list[str]) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    pattern = re.compile(r"((?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s|),;]*)?)", re.I)
    for line in lines:
        for match in pattern.finditer(line):
            candidate = match.group(1).strip().rstrip(".,)")
            if "@" in candidate:
                continue
            bare_candidate = re.sub(r"^https?://", "", candidate, flags=re.I)
            bare_candidate = re.sub(r"^www\.", "", bare_candidate, flags=re.I)
            if f"@{bare_candidate.lower()}" in line.lower():
                continue
            normalized = candidate if candidate.startswith(("http://", "https://")) else f"https://{candidate}"
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            links.append(normalized)
    return links


def collect_bullets(lines: list[str]) -> tuple[list[str], list[str]]:
    bullets = []
    extras = []
    current = ""
    for line in lines:
        if looks_like_bullet(line):
            if current:
                bullets.append(current.strip())
            current = strip_bullet(line)
            continue
        if current and not looks_like_date(line) and not looks_like_url(line) and not looks_like_email(line):
            current = f"{current} {line}".strip()
            continue
        if current:
            bullets.append(current.strip())
            current = ""
        extras.append(line)
    if current:
        bullets.append(current.strip())
    return bullets, extras


def parse_skills(lines: list[str]) -> dict[str, list[str]]:
    skills: dict[str, list[str]] = {}
    current_key = ""
    current_values: list[str] = []

    def flush_current() -> None:
        nonlocal current_key, current_values
        if current_key and current_values:
            joined = " ".join(current_values)
            items = [item.strip() for item in joined.split(",") if item.strip()]
            if items:
                skills[current_key] = items
        current_key = ""
        current_values = []

    for line in lines:
        if not line or is_heading(line) or looks_like_date(line):
            continue

        is_label = (
            ":" not in line
            and "," not in line
            and not looks_like_bullet(line)
            and len(line) <= 40
            and not looks_like_url(line)
        )

        if is_label:
            flush_current()
            current_key = line.strip()
            continue

        if current_key:
            current_values.append(line.strip())

    flush_current()
    return skills


def parse_blocks(lines: list[str], is_start) -> list[list[str]]:
    starts = [index for index in range(len(lines)) if is_start(lines, index)]
    if not starts:
        return []
    blocks = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        blocks.append(lines[start:end])
    return blocks


def parse_education(lines: list[str]) -> list[dict]:
    def is_start(items, index):
        return index + 1 < len(items) and not looks_like_bullet(items[index]) and looks_like_date(items[index + 1])

    entries = []
    for block in parse_blocks(lines, is_start):
        title = block[0]
        if len(block) > 1 and block[1] == title:
            block = [block[0]] + block[2:]
        period = block[1] if len(block) > 1 else ""
        details = [line for line in block[2:] if not looks_like_bullet(line)]
        school = title
        detail = details[0] if details else ""
        location = details[-1] if len(details) > 1 else ""
        if details and "|" in details[0]:
            parts = split_pipe_parts(details[0])
            if parts:
                school = parts[0]
                location = parts[-1] if len(parts) > 1 else ""
                detail = " | ".join(parts[1:-1]) if len(parts) > 2 else ""
        entries.append(
            {
                "school": school,
                "period": period,
                "detail": detail,
                "location": location,
            }
        )
    return entries


def parse_experience(lines: list[str]) -> list[dict]:
    def is_start(items, index):
        return index + 1 < len(items) and not looks_like_bullet(items[index]) and looks_like_date(items[index + 1])

    entries = []
    for block in parse_blocks(lines, is_start):
        role = block[0]
        period = block[1] if len(block) > 1 else ""
        company_line = block[2] if len(block) > 2 else ""
        body = [line for line in block[3:] if line and line != "Â§"]
        bullets, non_bullets = collect_bullets(body)
        if non_bullets:
            bullets = non_bullets + bullets
        parts = split_pipe_parts(company_line)
        company = parts[0] if parts else company_line
        location = parts[-1] if len(parts) > 1 else ""
        entries.append(
            {
                "company": company,
                "period": period,
                "role": role,
                "location": location,
                "bullets": bullets,
            }
        )
    return entries


def parse_projects(lines: list[str]) -> list[dict]:
    def is_start(items, index):
        line = items[index]
        return "|" in line and not looks_like_bullet(line)

    entries = []
    for block in parse_blocks(lines, is_start):
        line = block[0]
        title, stack = line.split("|", 1)
        if "Machine Learning" in stack:
            stack = stack.split("Machine Learning", 1)[0]
        stack = stack.strip(" |,")
        body = [item for item in block[1:] if item and item != "Â§"]
        bullets, extras = collect_bullets(body)
        if extras and "machine learning" in extras[0].lower():
            stack = f"{stack.strip()} | {extras.pop(0)}"
        if extras:
            bullets.extend(extras)
        entries.append(
            {
                "name": title.strip(),
                "stack": stack.strip(),
                "bullets": bullets,
            }
        )
    return entries


def parse_responsibility(lines: list[str]) -> dict:
    bullets, non_bullets = collect_bullets(lines)
    return {
        "title": non_bullets[0] if len(non_bullets) > 0 else "",
        "period": non_bullets[1] if len(non_bullets) > 1 else "",
        "org": non_bullets[2] if len(non_bullets) > 2 else "",
        "bullets": bullets + non_bullets[3:],
    }


def parse_achievements(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        cleaned = strip_bullet(line)
        if cleaned:
            items.append(cleaned)
    return items


def parse_resume(pdf_path: Path) -> dict:
    text = extract_pdf_text(pdf_path)
    lines = clean_lines(text)
    sections = split_sections(lines)
    name = first_non_contact(lines)
    title = detect_title(lines, name)
    location = extract_location(lines)
    contacts = extract_contacts(lines)
    links = extract_links(lines)
    education = parse_education(sections["education"])
    experience = parse_experience(sections["experience"])
    projects = parse_projects(sections["projects"])
    skills = parse_skills(sections["skills"])
    summary_lines = [line for line in sections["summary"] if not looks_like_email(line) and not looks_like_url(line)]
    if not title and experience:
        title = experience[0]["role"]
    if title and (len(title) > 80 or " with " in title.lower()) and experience:
        title = experience[0]["role"]

    data = {
        "source": pdf_path,
        "name": name,
        "title": title or "Portfolio",
        "location": location,
        "email": contacts["email"],
        "linkedin": contacts["linkedin"],
        "github": contacts["github"],
        "links": links,
        "summary": "",
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": skills,
        "responsibility": parse_responsibility(sections["responsibility"]),
        "achievements": parse_achievements(sections["achievements"]),
    }

    if summary_lines:
        data["summary"] = " ".join(summary_lines[:2])
    else:
        focus = []
        if data["experience"]:
            focus.append("experience")
        if data["projects"]:
            focus.append("projects")
        if data["skills"]:
            focus.append("core skills")
        focus_text = ", ".join(focus[:-1] + [focus[-1]]) if len(focus) > 1 else (focus[0] if focus else "professional growth")
        location_text = f" based in {data['location']}" if data["location"] else ""
        data["summary"] = f"{data['name']} is a {data['title']}{location_text}, with a profile centered on {focus_text}."
    return data
