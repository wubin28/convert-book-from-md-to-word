#!/usr/bin/env python3
import sys
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown
from bs4 import BeautifulSoup
import os

def convert_markdown_to_docx(input_file, output_file):
    # Read Markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create a new Document
    doc = Document()
    
    # Set document margins (observed from ch04-to.docx)
    sections = doc.sections
    for section in sections:
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
    
    # Convert Markdown to HTML for easier processing
    html = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    soup = BeautifulSoup(html, 'html.parser')
    
    # Process the content by paragraphs
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'ul', 'ol', 'li', 'blockquote'])
    
    current_list = None
    list_item_level = 0
    
    for element in elements:
        if element.name.startswith('h'):
            # Handle headings
            level = int(element.name[1])
            heading = doc.add_heading('', level=level)
            heading.add_run(element.get_text()).bold = True
            
            # Add specific formatting for headings
            for paragraph in doc.paragraphs:
                if paragraph.text == element.get_text():
                    # Format heading font size based on level
                    if level == 1:
                        for run in paragraph.runs:
                            run.font.size = Pt(16)
                    elif level == 2:
                        for run in paragraph.runs:
                            run.font.size = Pt(14)
                    else:
                        for run in paragraph.runs:
                            run.font.size = Pt(12)
        
        elif element.name == 'p':
            # Handle paragraphs
            if element.find('img'):
                # Image handling - just adding placeholder text
                img_tag = element.find('img')
                img_alt = img_tag.get('alt', 'Image')
                # For now, we're just adding a placeholder for images
                p = doc.add_paragraph(f"[{img_alt} - image placeholder]")
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                # Regular paragraph
                text = element.get_text()
                
                # Special handling for notes inside square brackets (like 【避坑指南】)
                if text.startswith('【') and '】' in text:
                    p = doc.add_paragraph()
                    note_title = text[:text.find('】')+1]
                    note_content = text[text.find('】')+1:].strip()
                    p.add_run(note_title).bold = True
                    p.add_run(note_content)
                else:
                    p = doc.add_paragraph(text)
        
        elif element.name == 'pre':
            # Handle code blocks
            code_text = element.get_text()
            # Remove markdown code block indicators if present
            code_text = re.sub(r'^```.*?\n|```$', '', code_text, flags=re.DOTALL)
            p = doc.add_paragraph(code_text)
            # Style as monospace for code
            for run in p.runs:
                run.font.name = 'Courier New'
        
        elif element.name == 'blockquote':
            # Handle blockquotes
            p = doc.add_paragraph(element.get_text())
            p.style = 'Quote'
        
        elif element.name in ('ul', 'ol'):
            # Start a new list
            current_list = element.name
            list_item_level = 0
        
        elif element.name == 'li' and current_list:
            # Add list item with appropriate level
            list_marker = '•' if current_list == 'ul' else f"{list_item_level+1}."
            p = doc.add_paragraph(f"{list_marker} {element.get_text()}")
            
            # Increment list item count if ordered list
            if current_list == 'ol':
                list_item_level += 1
    
    # Save the document
    doc.save(output_file)
    print(f"Successfully converted {input_file} to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 converter.py <input_markdown_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    # Generate output filename based on input
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name.replace('-from', '-to')}.docx"
    
    # If direct replacement doesn't work, just use the base filename
    if output_file == input_file:
        output_file = f"{base_name}_converted.docx"
    
    convert_markdown_to_docx(input_file, output_file)