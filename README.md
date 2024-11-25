# Book Metadata Enrichment Tool with OpenAI and Google Books

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Stars](https://img.shields.io/github/stars/backyMacky/AI-digital-library.svg?style=social&label=Stars)

[![Clone Repository](https://img.shields.io/badge/Clone-GitHub-blue.svg)](https://github.com/backyMacky/AI-digital-library.git)
[![Download ZIP](https://img.shields.io/badge/Download-ZIP-green.svg)](https://github.com/backyMacky/AI-digital-library/archive/refs/heads/main.zip)
[![Installation Guide](https://img.shields.io/badge/Installation-Guide-yellow.svg)](#installation)
[![Usage Guide](https://img.shields.io/badge/Usage-Guide-orange.svg)](#quick-start)

A powerful Python tool for enriching book metadata using the Google Books API and web scraping fallbacks. Perfect for librarians, book collectors, and data analysts working with book datasets.

<a href="https://www.buymeacoffee.com/bloombrine" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Features

- 📚 **Comprehensive Metadata**: Fetches extensive book metadata from multiple sources.
- 🔄 **Multiple Formats**: Supports both CSV and XLSX file formats.
- 🔍 **Google Books API Integration**: Primary source for metadata.
- 🌐 **Web Scraping Fallbacks**: Ensures data availability by scraping alternative sources when needed.
- 👤 **Interactive Selection**: Facilitates user selection for ambiguous matches.
- ⚡ **Asynchronous Processing**: Enhances performance with async operations.
- 🛡️ **Ethical Web Scraping**: Implements rate limiting to respect source websites.
- 📊 **Structured Output**: Ensures consistent formatting in output files.

## Installation

### Clone the Repository

```bash
git clone https://github.com/backyMacky/AI-digital-library/
cd book-enrichment-tool
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Requirements

Ensure you have the following packages installed:

- `pandas>=1.5.0`
- `aiohttp>=3.8.0`
- `beautifulsoup4>=4.9.0`
- `inquirer>=3.1.0`
- `openpyxl>=3.0.0`  # For Excel support

## Quick Start

1. **Get a Google Books API Key**: Obtain it from the [Google Cloud Console](https://console.cloud.google.com/).

2. **Prepare Your Input File**: Create a CSV or XLSX file with the following columns:
   - `book_name`: Title of the book
   - `isbn`: ISBN-10 or ISBN-13 number

   **Example (`books.csv` or `books.xlsx`):**

   | name             | author         | isbn           |
   |------------------|----------------|----------------|
   | The Great Gatsby |   Lex Luthor   | 9780743273565  |
   | 1984             | George Orwell  | 9780743273565  |

3. **Run the Script**:

   ```bash
   python book_enricher.py
   ```

## Input/Output Format

### Input File Example

**`books.csv` or `books.xlsx`:**

```csv
book_name,isbn
"The Great Gatsby","9780743273565"
"1984","9780451524935"
```

### Output Fields

- `book_name`: Title from source
- `isbn`: ISBN number
- `authors`: Comma-separated list of authors
- `publisher`: Publisher name
- `year`: Publication year
- `pages`: Page count
- `rating`: Average rating (0-5)
- `url`: Source URL
- `source`: Data source (`google`, `goodreads`, `worldcat`)

## Usage Examples

### Basic Usage

```python
from book_enricher import BookEnricher
import asyncio
from pathlib import Path

async def main():
    async with BookEnricher("YOUR_API_KEY") as enricher:
        await enricher.process_books(
            Path("books.xlsx"),
            Path("enriched_books.xlsx")
        )

asyncio.run(main())
```

### Custom Source Integration

```python
from book_enricher import BookSource, BookData
from typing import List

class CustomSource(BookSource):
    async def search(self, book_name: str, isbn: str) -> List[BookData]:
        # Your implementation here
        pass

# Add to enricher
enricher.sources.append(CustomSource(enricher.session))
```

## Advanced Features

### Rate Limiting

The tool implements respectful rate limiting:

- **1 second delay** between API requests
- **Custom user agent headers**
- **Error handling** with exponential backoff

### Data Sources

- **Google Books API** (primary)
- **Goodreads** (fallback)
- **WorldCat** (fallback)

### Interactive Selection

When multiple matches are found, the tool presents an interactive selection:

```
Choose the correct book for 'The Great Gatsby':
❯ The Great Gatsby by F. Scott Fitzgerald (1925) - from google
  The Great Gatsby by F. Scott Fitzgerald (2004) - from goodreads
  Skip this book
```

## Contributing

Contributions are welcome! Follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**:

   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Commit Your Changes**:

   ```bash
   git commit -m 'Add amazing feature'
   ```

4. **Push to the Branch**:

   ```bash
   git push origin feature/amazing-feature
   ```

5. **Open a Pull Request**

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- **Google Books API** for primary data source
- **Beautiful Soup** for web scraping capabilities
- **Pandas** for data handling
- **Inquirer** for interactive CLI

## Documentation

For detailed documentation, see:

- [Python API Documentation](#)
- [Contributing Guidelines](#)
- [Change Log](#)

## Support

For support:

- **Check existing Issues**
- **Open a new issue**
  - Include sample data and full error traceback when reporting bugs

---

Built with ❤️ by [Martin Bacigal](https://github.com/backyMacky)
