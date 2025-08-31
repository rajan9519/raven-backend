import json
import re
from typing import List, Dict, Any, Optional, Tuple
from models import ContentItem, ContentType, Citation, BoundingBox
from config import Config

class DataParser:
    """Parses and extracts structured content from manual data files"""
    
    def __init__(self, config: Config):
        self.config = config
        self.mmd_data = None
        
    def load_data(self):
        """Load JSON metadata"""
        # Load JSON metadata
        with open(self.config.MMD_DATA_PATH, 'r', encoding='utf-8') as f:
            self.mmd_data = json.load(f)
    
    def extract_figures(self) -> List[ContentItem]:
        """Extract figure content from JSON data"""
        figures = []
        figure_pattern = r'\\begin\{figure\}(.*?)\\end\{figure\}'
        caption_pattern = r'\\caption\{(.*?)\}'
        
        if not self.mmd_data or 'pages' not in self.mmd_data:
            return figures
            
        figure_count = 0
        
        for page in self.mmd_data['pages']:
            page_num = page['page']
            
            for line in page.get('lines', []):
                text = line.get('text', '')
                
                # Check if this line contains figure LaTeX
                figure_match = re.search(figure_pattern, text, re.DOTALL)
                if figure_match:
                    figure_count += 1
                    
                    # Extract caption
                    caption_match = re.search(caption_pattern, figure_match.group(1))
                    caption = caption_match.group(1) if caption_match else f"Figure {figure_count}"
                    
                    citation = Citation(
                        page_no=page_num,
                        bounding_box=BoundingBox(
                            top_left_x=line['region']['top_left_x'],
                            top_left_y=line['region']['top_left_y'],
                            width=line['region']['width'],
                            height=line['region']['height']
                        )
                    )
                    
                    figures.append(ContentItem(
                        id=f"figure_{figure_count}",
                        content_type=ContentType.FIGURE,
                        title=caption,
                        content=figure_match.group(1).strip(),
                        citation=citation,
                        metadata={
                            'confidence': line.get('confidence', 1.0),
                            'font_size': line.get('font_size')
                        },
                        type="figure"
                    ))
                
        return figures
    
    def extract_tables(self) -> List[ContentItem]:
        """Extract table content from JSON data"""
        tables = []
        table_pattern = r'\\begin\{table\}(.*?)\\end\{table\}'
        tabular_pattern = r'\\begin\{tabular\}(.*?)\\end\{tabular\}'
        caption_pattern = r'\\caption\{(.*?)\}'
        
        if not self.mmd_data or 'pages' not in self.mmd_data:
            return tables
            
        table_count = 0
        
        for page in self.mmd_data['pages']:
            page_num = page['page']
            
            for line in page.get('lines', []):
                text = line.get('text', '')
                
                # Check if this line contains table LaTeX
                table_match = re.search(table_pattern, text, re.DOTALL)
                if table_match:
                    table_count += 1
                    
                    # Extract caption
                    caption_match = re.search(caption_pattern, table_match.group(1))
                    caption = caption_match.group(1) if caption_match else f"Table {table_count}"
                    
                    # Extract tabular content
                    tabular_match = re.search(tabular_pattern, table_match.group(1), re.DOTALL)
                    tabular_content = tabular_match.group(1) if tabular_match else table_match.group(1)
                    
                    citation = Citation(
                        page_no=page_num,
                        bounding_box=BoundingBox(
                            top_left_x=line['region']['top_left_x'],
                            top_left_y=line['region']['top_left_y'],
                            width=line['region']['width'],
                            height=line['region']['height']
                        )
                    )
                    
                    tables.append(ContentItem(
                        id=f"table_{table_count}",
                        content_type=ContentType.TABLE,
                        title=caption,
                        content=tabular_content.strip(),
                        citation=citation,
                        metadata={
                            'confidence': line.get('confidence', 1.0),
                            'font_size': line.get('font_size')
                        },
                        type="table"
                    ))
                
        return tables
    
    def extract_text_blocks(self) -> List[ContentItem]:
        """Extract significant text blocks from JSON data"""
        text_blocks = []
        
        if not self.mmd_data or 'pages' not in self.mmd_data:
            return text_blocks
            
        for page in self.mmd_data['pages']:
            page_num = page['page']
            
            # Group lines by proximity and font size to identify blocks
            blocks = self._group_text_lines(page.get('lines', []))
            
            for i, block in enumerate(blocks):
                if len(block['text']) > 100:  # Only significant text blocks
                    citation = Citation(
                        page_no=page_num,
                        bounding_box=BoundingBox(**block['bounding_box'])
                    )
                    
                    text_blocks.append(ContentItem(
                        id=f"text_{page_num}_{i+1}",
                        content_type=ContentType.TEXT,
                        title=block.get('title'),
                        content=block['text'],
                        citation=citation,
                        metadata={
                            'font_size': block.get('font_size'),
                            'confidence': block.get('confidence')
                        },
                        type="text"
                    ))
                    
        return text_blocks
    
    def _group_text_lines(self, lines: List[Dict]) -> List[Dict]:
        """Group nearby text lines into logical blocks"""
        if not lines:
            return []
            
        blocks = []
        current_block = {
            'text': '',
            'bounding_box': None,
            'font_size': None,
            'confidence': 1.0
        }
        
        for line in lines:
            text = line.get('text', '').strip()
            if not text:
                continue
                
            region = line.get('region', {})
            
            # Initialize first block
            if not current_block['text']:
                current_block['text'] = text
                current_block['bounding_box'] = region.copy()
                current_block['font_size'] = line.get('font_size')
                current_block['confidence'] = line.get('confidence', 1.0)
            else:
                # Check if this line should be part of current block
                # (similar font size, reasonable proximity)
                prev_y = current_block['bounding_box']['top_left_y']
                curr_y = region.get('top_left_y', 0)
                
                if (abs(curr_y - prev_y) < 100 and  # Close proximity
                    abs(line.get('font_size', 0) - current_block['font_size']) < 5):
                    
                    # Extend current block
                    current_block['text'] += ' ' + text
                    
                    # Update bounding box to encompass both
                    bbox = current_block['bounding_box']
                    bbox['width'] = max(bbox['top_left_x'] + bbox['width'], 
                                      region['top_left_x'] + region['width']) - bbox['top_left_x']
                    bbox['height'] = max(bbox['top_left_y'] + bbox['height'],
                                       region['top_left_y'] + region['height']) - bbox['top_left_y']
                else:
                    # Start new block
                    if len(current_block['text']) > 50:
                        blocks.append(current_block.copy())
                    
                    current_block = {
                        'text': text,
                        'bounding_box': region.copy(),
                        'font_size': line.get('font_size'),
                        'confidence': line.get('confidence', 1.0)
                    }
        
        # Add final block
        if len(current_block['text']) > 50:
            blocks.append(current_block)
            
        return blocks
    
    def parse_all_content(self) -> Tuple[List[ContentItem], List[ContentItem], List[ContentItem]]:
        """Parse and return all content: figures, tables, text blocks"""
        self.load_data()
        
        figures = self.extract_figures()
        tables = self.extract_tables()
        text_blocks = self.extract_text_blocks()
        
        return figures, tables, text_blocks
