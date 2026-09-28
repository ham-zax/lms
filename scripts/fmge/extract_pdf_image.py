#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdfium2>=4", "pillow>=10"]
# ///
"""Crop a figure from a source-notes PDF page for an FMGE image-based question.

The question-bank prompt marks image items with a line such as

    **Image source:** p.34 | chest radiograph, lower half of the page

Render that page, crop the figure, and paste the printed lines into the Markdown
question just before its options:

    uv run scripts/fmge/extract_pdf_image.py --page 34 --crop 0.05,0.50,0.95,0.95 \\
        --name psm-b2-q012

Crop box is left,top,right,bottom as fractions of the page (0-1). Run once
without --crop and --preview to write the whole page and pick the box.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF = ROOT / "research/pdf_extracted_questions_data/Day2_PSM_combined.pdf"
IMAGE_DIR = ROOT / "lms/public/fmge/images"
PUBLIC_PREFIX = "/assets/lms/fmge/images"


def parse_crop(value: str) -> tuple[float, float, float, float]:
	parts = [float(part) for part in value.split(",")]
	if len(parts) != 4:
		raise argparse.ArgumentTypeError("crop needs four numbers: left,top,right,bottom")
	left, top, right, bottom = parts
	if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
		raise argparse.ArgumentTypeError(
			"crop fractions must satisfy 0 <= left < right <= 1 and 0 <= top < bottom <= 1"
		)
	return left, top, right, bottom


def main() -> int:
	parser = argparse.ArgumentParser(
		description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
	)
	parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
	parser.add_argument("--page", type=int, required=True, help="PDF viewer page number (1-based)")
	parser.add_argument("--crop", type=parse_crop, help="left,top,right,bottom fractions of the page")
	parser.add_argument("--name", help="Output file stem, e.g. psm-b2-q012 (required unless --preview)")
	parser.add_argument(
		"--alt", default="", help="Alt text that describes the image without giving the answer"
	)
	parser.add_argument("--scale", type=float, default=2.5, help="Render scale (2.5 ~ 180 dpi)")
	parser.add_argument("--preview", type=Path, help="Write the whole rendered page here and exit")
	args = parser.parse_args()

	pdf = pdfium.PdfDocument(str(args.pdf))
	if not 1 <= args.page <= len(pdf):
		raise SystemExit(f"Page {args.page} is outside 1-{len(pdf)}")
	image = pdf[args.page - 1].render(scale=args.scale).to_pil().convert("RGB")

	if args.preview:
		image.save(args.preview)
		print(f"Wrote page {args.page} preview to {args.preview} ({image.width}x{image.height})")
		return 0
	if not args.name:
		raise SystemExit("--name is required when writing a question image")

	if args.crop:
		left, top, right, bottom = args.crop
		image = image.crop(
			(
				round(left * image.width),
				round(top * image.height),
				round(right * image.width),
				round(bottom * image.height),
			)
		)

	IMAGE_DIR.mkdir(parents=True, exist_ok=True)
	output = IMAGE_DIR / f"{args.name}.png"
	image.save(output, optimize=True)

	print(f"**Image:** {PUBLIC_PREFIX}/{output.name}")
	print(f"**Image alt:** {args.alt or 'Question image'}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
