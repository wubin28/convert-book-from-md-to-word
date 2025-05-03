#!/usr/bin/env python3
import sys
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import markdown
from bs4 import BeautifulSoup
import os

def convert_markdown_to_docx(input_file, output_file):
    # Read Markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Process special note blocks that might be in aside tags
    # This extracts any 【避坑指南】 content that might be in <aside> tags
    aside_notes = []
    aside_pattern = re.compile(r'<aside>(?:\n|.)*?【避坑指南】.*?</aside>', re.DOTALL)
    for match in aside_pattern.finditer(md_content):
        aside_notes.append(match.group(0))
    
    # Create a new Document
    doc = Document()
    
    # Set document margins (observed from ch04-to.docx)
    sections = doc.sections
    for section in sections:
        section.left_margin = Inches(0)  # Reduced to match the screenshot
        section.right_margin = Inches(0.5)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
    
    # Convert Markdown to HTML for easier processing
    html = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    soup = BeautifulSoup(html, 'html.parser')
    
    # First extract all aside/note tags for special handling
    note_blocks = []
    for aside in soup.find_all('aside'):
        note_blocks.append(aside.get_text())
        # Remove from soup to avoid double processing
        aside.extract()
    
    # Process the content by paragraphs
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'ul', 'ol', 'li', 'blockquote'])
    
    current_list = None
    list_item_level = 0
    
    # First, process the main content
    for element in elements:
        if element.name.startswith('h'):
            # Handle headings
            level = int(element.name[1])
            heading_text = element.get_text().strip()
            
            # Create heading with proper formatting
            heading = doc.add_heading('', level=level)
            run = heading.add_run(heading_text)
            run.bold = True
            
            # Set font to YaHei (Microsoft YaHei)
            run.font.name = '微软雅黑'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
            
            # Set font size based on heading level
            if level == 1:
                run.font.size = Pt(22)  # Increased to match screenshot
                heading.paragraph_format.left_indent = Inches(0)  # Zero indent for h1
            elif level == 2:
                run.font.size = Pt(18)  # Adjusted based on screenshot
            else:
                run.font.size = Pt(14)  # Adjusted for other headings
        
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
                if '【避坑指南】' in text:
                    p = doc.add_paragraph()
                    # Split the text at 【避坑指南】
                    parts = text.split('【避坑指南】', 1)
                    if parts[0]:  # If there's text before the note marker
                        p.add_run(parts[0])
                    
                    note_run = p.add_run('【避坑指南】')
                    note_run.bold = True
                    
                    if len(parts) > 1 and parts[1]:  # If there's text after the note marker
                        p.add_run(parts[1])
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
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Courier New')
        
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
    
    # Now process any additional aside/note blocks that weren't in the main flow
    # This handles the 【避坑指南】 blocks that were in <aside> tags
    for note_text in aside_notes:
        # Extract the content inside the aside tag
        match = re.search(r'【避坑指南】(.*?)(?:</aside>|$)', note_text, re.DOTALL)
        if match:
            note_content = match.group(1).strip()
            p = doc.add_paragraph()
            title_run = p.add_run('【避坑指南】')
            title_run.bold = True
            p.add_run(note_content)
    
    # Also process the extracted note blocks from BeautifulSoup
    for note_text in note_blocks:
        if '【避坑指南】' in note_text:
            p = doc.add_paragraph()
            parts = note_text.split('【避坑指南】', 1)
            if parts[0].strip():  # If there's text before the note marker
                p.add_run(parts[0].strip())
            
            note_run = p.add_run('【避坑指南】')
            note_run.bold = True
            
            if len(parts) > 1 and parts[1].strip():  # If there's text after the note marker
                p.add_run(parts[1].strip())
    
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