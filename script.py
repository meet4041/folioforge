import argparse
from pathlib import Path

from portfolio_renderer import generate_site, slugify
from resume_parser import parse_resume

DEFAULT_OUTPUT_DIR = Path("generated_portfolio")


def resolve_input_paths(raw_inputs: list[str]) -> list[Path]:
    resolved = []
    for raw in raw_inputs:
        candidate = Path(raw).expanduser()
        if candidate.is_dir():
            resolved.extend(sorted(candidate.glob("*.pdf")))
        elif candidate.is_file():
            resolved.append(candidate)
    unique = []
    seen = set()
    for path in resolved:
        key = path.resolve()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def prompt_for_paths() -> list[str]:
    raw = input("Enter PDF path or folder path (you can separate multiple paths with commas): ").strip()
    return [item.strip() for item in raw.split(",") if item.strip()]


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run(paths: list[Path], base_output_dir: Path) -> None:
    if not paths:
        raise SystemExit("No PDF files found. Please provide a valid PDF path or a folder containing PDFs.")

    multiple = len(paths) > 1
    if multiple:
        ensure_output_dir(base_output_dir)

    for index, pdf_path in enumerate(paths, start=1):
        data = parse_resume(pdf_path)
        output_dir = base_output_dir if not multiple else base_output_dir / f"{index:02d}-{slugify(pdf_path.stem)}"
        generate_site(data, output_dir)
        print(f"Generated portfolio for {pdf_path.name} -> {output_dir}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a portfolio site from one or more resume PDFs.")
    parser.add_argument("paths", nargs="*", help="PDF file path(s) or a folder containing PDFs")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output folder for the generated site(s). Default: generated_portfolio",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    raw_inputs = args.paths or prompt_for_paths()
    paths = resolve_input_paths(raw_inputs)
    output_dir = Path(args.output)
    run(paths, output_dir)


if __name__ == "__main__":
    main()
