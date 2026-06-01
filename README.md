# FolioForge

FolioForge is a PDF-to-portfolio generator that turns a resume PDF into a polished, multi-page portfolio site.

## What it does

- Reads resume content from one or more PDF files
- Extracts sections like About, Skills, Journey, Projects, and Contact
- Generates a responsive portfolio in `generated_portfolio/`
- Supports multiple PDFs from the command line

## Tech Stack

- Python
- PyMuPDF (`fitz`)
- HTML
- CSS
- Vanilla JavaScript

## Run it

Install the dependency:

```bash
pip install pymupdf
```

Generate a portfolio from a PDF:

```bash
python script.py Meet_Gandhi.pdf
```

Or run it without arguments and enter a path when prompted:

```bash
python script.py
```

## Output

The generated site is written to:

```text
generated_portfolio/
```

Open `generated_portfolio/index.html` in your browser to preview the site.

## Features

- Elegant, classic UI
- Dark-themed layout
- Animated page headings
- Contact form with validation
- Resume-driven content generation

## Project Structure

```text
script.py
resume_parser.py
portfolio_renderer.py
generated_portfolio/
Meet_Gandhi.pdf
```

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).

