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

## How To Use

1. Put your resume PDF in the project folder, or note the full path to the file.
2. Open a terminal in this folder.
3. Install the dependency with `pip install pymupdf` if you have not already.
4. Run `python script.py <your-pdf-file.pdf>`.
5. If you want, you can also run `python script.py` and type the PDF path when prompted.
6. Wait for the generator to finish.
7. Open `generated_portfolio/index.html` in a browser.
8. Browse the pages and check whether the extracted content looks correct.
9. If needed, replace the PDF with a different one and run the script again.

## For Other Users

If someone else wants to use this project:

- They only need Python installed
- They should install `pymupdf`
- They can use any resume PDF they want
- The script will generate a fresh portfolio from that PDF
- The output can be shared or deployed as a static site

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
