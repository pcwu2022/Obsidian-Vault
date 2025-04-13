# Obsidian Vault Formatter

A Python tool to standardize the formatting across your entire Obsidian vault, ensuring consistency and readability in your notes.

## Features

- **Format Standardization**
  - Remove horizontal lines (---, ___, ***)
  - Eliminate empty lines between bullet points
  - Ensure one empty line before subtitles
  - Convert all subtitles to start at h2 level (## Subtitle)
  - Remove emojis from subtitles
  - Eliminate duplicate wikilinks on the same page

- **Enhanced Functionality**
  - Translate Chinese notes to English while preserving the original text
  - Automatically create wikilinks for words/phrases that match existing file names

## Requirements

- Python 3.6 or higher
- Required Python package: `googletrans==4.0.0-rc1`

## Installation

1. Clone or download this repository
2. Install the required package:
   ```
   pip install googletrans==4.0.0-rc1
   ```

## Usage

### Basic Usage

```bash
python obsidian_formatter.py /path/to/your/vault
```

### Options

```
usage: obsidian_formatter.py [-h] [--dry-run] [--no-translate] [--no-wikilinks] vault_path

Format Obsidian vault markdown files

positional arguments:
  vault_path      Path to the Obsidian vault

optional arguments:
  -h, --help      show this help message and exit
  --dry-run       Do not modify files, just show what would be changed
  --no-translate  Disable Chinese to English translation
  --no-wikilinks  Disable automatic wikilink creation
```

## Examples

### Dry Run to Preview Changes

```bash
python obsidian_formatter.py /path/to/your/vault --dry-run
```

### Format Without Translation

```bash
python3 ./.formatter/formatter.py . --no-translate
```

### Format Without Automatic Wikilinks

```bash
python3 ./.formatter/formatter.py . --no-wikilinks
```

## How It Works

1. The script recursively searches for all `.md` files in your Obsidian vault
2. Each file is processed according to the formatting rules
3. For Chinese notes, the content is translated to English and the original text is preserved at the end
4. Words and phrases that match existing file names are converted to wikilinks
5. Statistics about the changes are displayed after processing

## Output Example

```
Found 120 markdown files in the vault.
Formatted: daily_notes/2023-03-15.md
Formatted and translated: projects/project_ideas.md
No changes needed: templates/meeting_notes.md
...

===== Formatting Statistics =====
Files processed: 120
Horizontal lines removed: 45
Empty lines between bullets removed: 67
Subtitle spacing fixed: 89
Subtitle levels adjusted: 23
Emojis removed from subtitles: 12
Duplicate wikilinks removed: 34
Files translated from Chinese: 5
Wikilinks created: 78
```

## Notes

- Always backup your vault before running this script, especially for the first time
- Translation requires an internet connection as it uses Google's translation service
- The script avoids creating self-links and links for very short file names (less than 4 characters)
- The wikilink creation feature only creates links for the first instance of a matching word/phrase

## Troubleshooting

- If you encounter encoding issues, the script uses 'replace' error handling for reading files
- For large vaults, the translation might take some time due to API rate limits
- If translation fails, the original text is preserved