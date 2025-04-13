import os
import re
import glob
from pathlib import Path
import argparse
import hashlib
from googletrans import Translator
import time
from collections import Counter

class ObsidianVaultFormatter:
    def __init__(self, vault_path, dry_run=False, translate_chinese=True, create_wikilinks=True):
        self.vault_path = os.path.abspath(vault_path)
        self.dry_run = dry_run
        self.translate_chinese = translate_chinese
        self.create_wikilinks = create_wikilinks
        self.translator = Translator() if translate_chinese else None
        self.file_names = self._get_all_file_names()
        self.stats = {
            'files_processed': 0,
            'horizontal_lines_removed': 0,
            'empty_lines_between_bullets_removed': 0,
            'subtitle_spacing_fixed': 0,
            'subtitle_levels_adjusted': 0,
            'emojis_removed_from_subtitles': 0,
            'duplicate_wikilinks_removed': 0,
            'files_translated': 0,
            'wikilinks_created': 0,
        }

    def _get_all_file_names(self):
        """Get all markdown file names in the vault for wikilink creation"""
        all_files = glob.glob(f"{self.vault_path}/**/*.md", recursive=True)
        # Extract file names without extension and path
        return [os.path.splitext(os.path.basename(f))[0] for f in all_files]

    def _is_chinese_text(self, text):
        """Check if a text contains significant amount of Chinese characters"""
        chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')
        chinese_chars = chinese_char_pattern.findall(text)
        # Consider it Chinese if more than 20% of characters are Chinese
        return len(chinese_chars) > len(text) * 0.2
    
    def _translate_text(self, text):
        """Translate Chinese text to English while preserving formatting"""
        if not self._is_chinese_text(text):
            return text, False
        
        # Split the text into chunks for translation (to handle large files)
        lines = text.split('\n')
        translated_lines = []
        original_text = text
        is_translated = False
        
        for line in lines:
            if self._is_chinese_text(line):
                is_translated = True
                # Preserve formatting characters at beginning of line
                formatting_match = re.match(r'^(\s*(?:[#*\->\d.]+\s*|\[\[.*?\]\]|\s+))', line)
                formatting = formatting_match.group(1) if formatting_match else ''
                
                # Extract content to translate
                content = line[len(formatting):] if formatting else line
                
                if content.strip():
                    try:
                        # Add delay to avoid hitting API limits
                        time.sleep(0.5)
                        translated = self.translator.translate(content, src='zh-cn', dest='en').text
                        translated_lines.append(f"{formatting}{translated}")
                    except Exception as e:
                        print(f"Translation error: {e}")
                        translated_lines.append(line)  # Keep original if translation fails
                else:
                    translated_lines.append(line)
            else:
                translated_lines.append(line)
        
        if is_translated:
            # Add original Chinese version at the end
            translated_lines.append("\n\n## Original Chinese Version\n")
            translated_lines.append(original_text)
            
        return '\n'.join(translated_lines), is_translated

    def _remove_horizontal_lines(self, content):
        """Remove horizontal lines (---, ___, ***) from the content"""
        pattern = r'^[\s]*?[-_*]{3,}[\s]*?$'
        new_content, count = re.subn(pattern, '', content, flags=re.MULTILINE)
        self.stats['horizontal_lines_removed'] += count
        return new_content
    
    def _fix_empty_lines_between_bullets(self, content):
        """Remove empty lines between bullet points"""
        bullet_pattern = r'(^[\s]*?[*\-+][\s]+.*$)\n\n([\s]*?[*\-+][\s]+)'
        new_content, count = re.subn(bullet_pattern, r'\1\n\2', content, flags=re.MULTILINE)
        while count > 0:
            new_content, count = re.subn(bullet_pattern, r'\1\n\2', new_content, flags=re.MULTILINE)
            self.stats['empty_lines_between_bullets_removed'] += count
        return new_content
    
    def _fix_subtitle_spacing(self, content):
        """Ensure one empty line before subtitles"""
        # First, make sure there's at least one newline before each subtitle
        subtitle_pattern = r'([^\n])\n?(#{2,}[\s]+)'
        new_content, count = re.subn(subtitle_pattern, r'\1\n\n\2', content)
        self.stats['subtitle_spacing_fixed'] += count
        
        # Handle case where subtitle is at the very beginning of the file
        if content.startswith('#'):
            new_content = content
        
        # Then, ensure there's exactly one empty line before subtitles (not more)
        multiple_newlines_pattern = r'\n{3,}(#{2,}[\s]+)'
        new_content, count = re.subn(multiple_newlines_pattern, r'\n\n\1', new_content)
        self.stats['subtitle_spacing_fixed'] += count
        
        # Fix: Remove any empty headings that might have been introduced
        empty_heading_pattern = r'^(#+)\s*$'
        lines = new_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not re.match(empty_heading_pattern, line.strip()):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _adjust_subtitle_levels(self, content):
        """Ensure subtitles start at h2 (## Subtitle)"""
        # Check if file has any h1 headings
        h1_pattern = r'^#\s+[^\n#]+'
        h1_headings = re.findall(h1_pattern, content, re.MULTILINE)
        
        if h1_headings:
            # If h1 exists, we need to adjust all heading levels
            for i in range(5, 0, -1):  # From h5 to h1
                pattern = r'^' + ('#' * i) + r'\s+'
                replacement = '#' * (i + 1) + ' '
                new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
                if count > 0:
                    content = new_content
                    self.stats['subtitle_levels_adjusted'] += count
        else:
            # If no h1, we need to convert h3+ to h2
            # Fix: Convert each heading pattern directly to h2 without adding empty h1
            for i in range(6, 2, -1):  # From h6 to h3
                pattern = r'^(' + ('#' * i) + r'\s+)(.+)$'  # Match full header with text
                replacement = r'## \2'  # Replace with h2 and keep the header text
                new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
                if count > 0:
                    content = new_content
                    self.stats['subtitle_levels_adjusted'] += count
                        
        return content
    
    def _remove_emojis_from_subtitles(self, content):
        """Remove emojis from subtitles"""
        # Unicode ranges for emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+"
        )
        
        # Find subtitles with emojis
        subtitle_pattern = r'^(#{2,}[\s]+)(.*?)$'
        lines = content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            subtitle_match = re.match(subtitle_pattern, line)
            if subtitle_match:
                prefix = subtitle_match.group(1)
                subtitle_text = subtitle_match.group(2)
                
                # Fix: Only remove emojis, not the entire text
                # And check if the cleaned text is empty
                cleaned_text = emoji_pattern.sub('', subtitle_text).strip()
                
                # Keep original text if after cleaning it becomes empty
                # This preserves Chinese text and other non-emoji content
                if cleaned_text == "" and subtitle_text.strip() != "":
                    cleaned_text = subtitle_text
                
                if cleaned_text != subtitle_text:
                    lines[i] = f"{prefix}{cleaned_text}"
                    modified = True
                    self.stats['emojis_removed_from_subtitles'] += 1
        
        return '\n'.join(lines) if modified else content
    
    def _remove_duplicate_wikilinks(self, content):
        """Remove duplicate wikilinks in the same page"""
        wikilink_pattern = r'\[\[(.*?)(?:\|.*?)?\]\]'
        wikilinks = re.findall(wikilink_pattern, content)
        
        # Count occurrences of each wikilink
        wikilink_counter = Counter(wikilinks)
        duplicate_links = {link: count for link, count in wikilink_counter.items() if count > 1}
        
        if not duplicate_links:
            return content
        
        for link, count in duplicate_links.items():
            # Keep first occurrence, remove others
            pattern = r'\[\[' + re.escape(link) + r'(?:\|(.*?))?\]\]'
            matches = list(re.finditer(pattern, content))
            
            # Skip the first match (keep it)
            for match in matches[1:]:
                # If there's a display text, keep it without the wikilink
                if '|' in match.group(0):
                    display_text = match.group(1)
                    content = content[:match.start()] + display_text + content[match.end():]
                else:
                    content = content[:match.start()] + link + content[match.end():]
                
                self.stats['duplicate_wikilinks_removed'] += 1
                
        return content
    
    def _create_wikilinks(self, content, file_path):
        """Create wikilinks from plain text that matches file names"""
        if not self.create_wikilinks:
            return content
            
        # Get current file name to avoid self-links
        current_file = os.path.splitext(os.path.basename(file_path))[0]
        
        # Sort file_names by length (descending) to match longer names first
        sorted_file_names = sorted(self.file_names, key=len, reverse=True)
        
        # Remove current file from the list
        if current_file in sorted_file_names:
            sorted_file_names.remove(current_file)
            
        links_created = 0
        
        for file_name in sorted_file_names:
            # Skip very short file names (to avoid replacing common words)
            if len(file_name) < 4:
                continue
                
            # Look for exact word matches (not part of existing wikilinks or other words)
            pattern = r'(?<!\[\[)(?<!\w)' + re.escape(file_name) + r'(?!\w)(?!\]\])'
            
            # Check if file_name appears in the content
            if re.search(pattern, content, re.IGNORECASE):
                # Replace with wikilink, but only the first occurrence
                new_content = re.sub(pattern, f'[[{file_name}]]', content, count=1, flags=re.IGNORECASE)
                if new_content != content:
                    content = new_content
                    links_created += 1
        
        self.stats['wikilinks_created'] += links_created
        return content
    
    def format_file(self, file_path):
        """Apply all formatting rules to a single file"""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        original_content = content
        
        # Apply formatting rules
        content = self._remove_horizontal_lines(content)
        content = self._fix_empty_lines_between_bullets(content)
        content = self._fix_subtitle_spacing(content)
        content = self._adjust_subtitle_levels(content)
        content = self._remove_emojis_from_subtitles(content)
        content = self._remove_duplicate_wikilinks(content)
        
        # Create wikilinks from text if enabled
        content = self._create_wikilinks(content, file_path)
        
        # Translate Chinese to English if enabled
        translated = False
        if self.translate_chinese:
            content, translated = self._translate_text(content)
            if translated:
                self.stats['files_translated'] += 1
        
        # Save the changes if not in dry run mode
        if content != original_content and not self.dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return content != original_content, translated
    
    def format_vault(self):
        """Process all markdown files in the vault"""
        md_files = glob.glob(f"{self.vault_path}/**/*.md", recursive=True)
        print(f"Found {len(md_files)} markdown files in the vault.")
        
        for file_path in md_files:
            try:
                changed, translated = self.format_file(file_path)
                self.stats['files_processed'] += 1
                
                if changed:
                    action = "Formatted" + (" and translated" if translated else "")
                    print(f"{action}: {os.path.relpath(file_path, self.vault_path)}")
                else:
                    print(f"No changes needed: {os.path.relpath(file_path, self.vault_path)}")
                    
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                
        self._print_stats()
    
    def _print_stats(self):
        """Print statistics about the formatting process"""
        print("\n===== Formatting Statistics =====")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Horizontal lines removed: {self.stats['horizontal_lines_removed']}")
        print(f"Empty lines between bullets removed: {self.stats['empty_lines_between_bullets_removed']}")
        print(f"Subtitle spacing fixed: {self.stats['subtitle_spacing_fixed']}")
        print(f"Subtitle levels adjusted: {self.stats['subtitle_levels_adjusted']}")
        print(f"Emojis removed from subtitles: {self.stats['emojis_removed_from_subtitles']}")
        print(f"Duplicate wikilinks removed: {self.stats['duplicate_wikilinks_removed']}")
        
        if self.translate_chinese:
            print(f"Files translated from Chinese: {self.stats['files_translated']}")
        
        if self.create_wikilinks:
            print(f"Wikilinks created: {self.stats['wikilinks_created']}")

def main():
    parser = argparse.ArgumentParser(description='Format Obsidian vault markdown files')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files, just show what would be changed')
    parser.add_argument('--no-translate', action='store_true', help='Disable Chinese to English translation')
    parser.add_argument('--no-wikilinks', action='store_true', help='Disable automatic wikilink creation')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.vault_path):
        print(f"Error: {args.vault_path} is not a valid directory")
        return
    
    formatter = ObsidianVaultFormatter(
        args.vault_path, 
        dry_run=args.dry_run,
        translate_chinese=not args.no_translate,
        create_wikilinks=not args.no_wikilinks
    )
    
    print(f"{'DRY RUN - ' if args.dry_run else ''}Formatting Obsidian vault at: {args.vault_path}")
    formatter.format_vault()

if __name__ == "__main__":
    main()