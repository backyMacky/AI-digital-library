**Book Metadata Enrichment Tool**

A powerful Python tool for enriching book metadata using the Google Books API and web scraping fallbacks. Perfect for librarians, book collectors, and data analysts working with book datasets.
Features

📚 Fetches comprehensive book metadata from multiple sources
🔄 Supports both CSV and XLSX file formats
🔍 Google Books API integration
🌐 Web scraping fallback for missing data
👤 Interactive selection for ambiguous matches
⚡ Asynchronous processing for better performance
🛡️ Ethical web scraping with rate limiting
📊 Structured output with consistent formatting

Installation
bashCopy# Clone the repository
git clone https://github.com/yourusername/book-enrichment-tool.git
cd book-enrichment-tool

# Install dependencies
pip install -r requirements.txt
Requirements
txtCopypandas>=1.5.0
aiohttp>=3.8.0
beautifulsoup4>=4.9.0
inquirer>=3.1.0
openpyxl>=3.0.0  # For Excel support
Quick Start

Get a Google Books API key from Google Cloud Console
Prepare your input file (CSV or XLSX) with columns:

book_name: Title of the book
isbn: ISBN-10 or ISBN-13 number


Run the script:

bashCopypython book_enricher.py
Input/Output Format
Input File Example (books.csv or books.xlsx):
csvCopybook_name,isbn
"The Great Gatsby","9780743273565"
"1984","9780451524935"
Output Fields:

book_name: Title from source
isbn: ISBN number
authors: Comma-separated list of authors
publisher: Publisher name
year: Publication year
pages: Page count
rating: Average rating (0-5)
url: Source URL
source: Data source (google/goodreads/worldcat)

Usage Examples
Basic Usage
pythonCopyfrom book_enricher import BookEnricher
import asyncio
from pathlib import Path

async def main():
    async with BookEnricher("YOUR_API_KEY") as enricher:
        await enricher.process_books(
            Path("books.xlsx"),
            Path("enriched_books.xlsx")
        )

asyncio.run(main())
Custom Source Integration
pythonCopyfrom book_enricher import BookSource, BookData

class CustomSource(BookSource):
    async def search(self, book_name: str, isbn: str) -> List[BookData]:
        # Your implementation here
        pass

# Add to enricher
enricher.sources.append(CustomSource(enricher.session))
Advanced Features
Rate Limiting
The tool implements respectful rate limiting:

1 second delay between API requests
Custom user agent headers
Error handling with backoff

Data Sources

Google Books API (primary)
Goodreads (fallback)
WorldCat (fallback)

Interactive Selection
When multiple matches are found, the tool presents an interactive selection:
Copy? Choose the correct book for 'The Great Gatsby':
  ❯ The Great Gatsby by F. Scott Fitzgerald (1925) - from google
    The Great Gatsby by F. Scott Fitzgerald (2004) - from goodreads
    Skip this book
Contributing

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments

Google Books API for primary data source
Beautiful Soup for web scraping capabilities
Pandas for data handling
Inquirer for interactive CLI

Documentation
For detailed documentation, see:

Python API Documentation
Contributing Guidelines
Change Log

Support
For support:

Check existing Issues
Open a new issue
Include sample data and full error traceback when reporting bugs


Built with ❤️ by [Your Name]
