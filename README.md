# Markdown to Word (.docx) Converter

This Python program converts a Markdown file to a Word document (.docx) with specific formatting.

## Features

- Converts headings (h1, h2, h3, etc.) with appropriate formatting
- Handles paragraphs and text content
- Supports code blocks with monospace formatting
- Processes lists (both ordered and unordered)
- Special handling for notes in square brackets (like 【避坑指南】)
- Creates placeholders for images in the original markdown

## Requirements

- Python 3.7+
- Required packages: python-docx, markdown, beautifulsoup4

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the program with the input Markdown file as an argument:

```bash
python3 converter.py ch04-from.md
```

The program will create a Word document named `ch04-to.docx` in the same directory.

## Format Differences Observed

The program takes into account these key formatting differences between the Markdown and Word document:

1. **Headings**: Different font sizes and styles for different heading levels
2. **Lists**: Proper indentation and bullet/number formatting
3. **Code blocks**: Monospaced font for code sections
4. **Special notes**: Highlighted formatting for notes in square brackets
5. **Document margins**: Appropriate margin settings for the Word document

## Limitations

- Images from the original Markdown are replaced with placeholder text
- Some complex formatting might not be perfectly preserved
- Tables might need additional formatting adjustments