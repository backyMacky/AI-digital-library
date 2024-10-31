"""
Book Enrichment Tool
===================

A comprehensive tool for enriching book metadata using Google Books API and web scraping.

This module provides functionality to:
1. Read book data from CSV/XLSX files
2. Fetch metadata from Google Books API
3. Fall back to web scraping when API data is unavailable
4. Interactive selection of correct book matches
5. Export enriched data to CSV/XLSX

Main Components:
---------------
- BookData: Data class for storing book information
- FileHandler: Manages file I/O operations
- BookSource: Base class for different data sources
- BookEnricher: Main class orchestrating the enrichment process
"""

#!/usr/bin/env python3
"""
Book Metadata Enrichment Tool
============================

This tool enriches book metadata from various sources, starting with Google Books API
and falling back to web scraping when necessary.

Author: Martin "Claude 3.5" Bacigal
License: MIT
Version: 1.1.0
"""

import asyncio
import sys
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, TypedDict, List, Tuple
from urllib.parse import quote_plus

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
import inquirer

# =============================================================================
# Configuration
# =============================================================================

CONFIG = {
    # File Settings
    'DEFAULT_INPUT_FILE': 'books',
    'DEFAULT_OUTPUT_FILE': 'enriched_books',
    'SUPPORTED_FORMATS': [('Excel (XLSX)', 'xlsx'), ('CSV', 'csv')],
    
    # API Settings
    'GOOGLE_BOOKS_API_URL': 'https://www.googleapis.com/books/v1/volumes',
    'GOODREADS_URL': 'https://www.goodreads.com/search',
    'WORLDCAT_URL': 'https://www.worldcat.org/search',
    
    # Scraping Settings
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'MAX_RESULTS_PER_SOURCE': 3,
    'RATE_LIMIT_DELAY': 1,  # seconds
    
    # Selectors
    'GOODREADS_SELECTORS': {
        'table_rows': '.tableList tr',
        'title': '.bookTitle',
        'author': '.authorName',
        'rating': '.average'
    },
    'WORLDCAT_SELECTORS': {
        'items': '.bibliography',
        'title': '.title',
        'author': '.author',
        'publisher': '.publisher'
    }
}

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class BookData:
    """Data structure for book metadata."""
    book_name: str
    isbn: str
    authors: str = ""
    publisher: str = ""
    year: str = ""
    pages: int = 0
    rating: float = 0.0
    url: str = ""
    source: str = "google"

class APIResponse(TypedDict):
    """Type hint for API response."""
    items: List[dict]
    totalItems: int

# =============================================================================
# File Handling
# =============================================================================

class FileHandler:
    """Handles file operations for both CSV and XLSX formats."""
    
    @staticmethod
    def get_file_preferences() -> Tuple[str, str, str]:
        """Prompt user for file format and name preferences."""
        questions = [
            inquirer.List('format',
                         message="Choose the file format for input/output:",
                         choices=CONFIG['SUPPORTED_FORMATS']),
            inquirer.Text('input_file',
                         message="Enter input file name (without extension):",
                         default=CONFIG['DEFAULT_INPUT_FILE']),
            inquirer.Text('output_file',
                         message="Enter output file name (without extension):",
                         default=CONFIG['DEFAULT_OUTPUT_FILE'])
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            sys.exit("File format selection cancelled")
            
        return (answers['format'],
                f"{answers['input_file']}.{answers['format']}",
                f"{answers['output_file']}.{answers['format']}")

    @staticmethod
    def read_file(path: Path) -> pd.DataFrame:
        """Read CSV or XLSX file."""
        try:
            if path.suffix == '.csv':
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            
            # Validate required columns
            required_columns = {'book_name', 'isbn'}
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Input file must contain columns: {required_columns}")
            
            return df
        except Exception as e:
            raise Exception(f"Error reading {path}: {str(e)}")

    @staticmethod
    def write_file(df: pd.DataFrame, path: Path) -> None:
        """Write to CSV or XLSX file."""
        try:
            if path.suffix == '.csv':
                df.to_csv(path, index=False)
            else:
                df.to_excel(path, index=False)
        except Exception as e:
            raise Exception(f"Error writing to {path}: {str(e)}")

# =============================================================================
# Data Sources
# =============================================================================

class BookSource:
    """Base class for book data sources."""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.headers = {"User-Agent": CONFIG['USER_AGENT']}

    async def search(self, book_name: str, isbn: str) -> List[BookData]:
        """Search for book data (to be implemented by subclasses)."""
        raise NotImplementedError

class GoodreadsSource(BookSource):
    """Goodreads web scraping source."""
    
    async def search(self, book_name: str, isbn: str) -> List[BookData]:
        try:
            search_url = f"{CONFIG['GOODREADS_URL']}?q={quote_plus(f'{book_name} {isbn}')}"
            async with self.session.get(search_url, headers=self.headers) as response:
                if response.status != 200:
                    return []
                
                soup = BeautifulSoup(await response.text(), 'html.parser')
                results = []
                selectors = CONFIG['GOODREADS_SELECTORS']
                
                for item in soup.select(selectors['table_rows'])[:CONFIG['MAX_RESULTS_PER_SOURCE']]:
                    title_elem = item.select_one(selectors['title'])
                    author_elem = item.select_one(selectors['author'])
                    if not title_elem or not author_elem:
                        continue
                        
                    year_match = re.search(r'published (\d{4})', item.text.lower())
                    rating_elem = item.select_one(selectors['rating'])
                    
                    results.append(BookData(
                        book_name=title_elem.text.strip(),
                        isbn=isbn,
                        authors=author_elem.text.strip(),
                        year=year_match.group(1) if year_match else "",
                        rating=float(rating_elem.text.strip()) if rating_elem else 0.0,
                        url=f"https://www.goodreads.com{title_elem['href']}",
                        source="goodreads"
                    ))
                    
                return results
        except Exception as e:
            print(f"Goodreads error: {e}", file=sys.stderr)
            return []

class WorldCatSource(BookSource):
    """WorldCat web scraping source."""
    
    async def search(self, book_name: str, isbn: str) -> List[BookData]:
        try:
            search_url = f"{CONFIG['WORLDCAT_URL']}?q={quote_plus(isbn)}"
            async with self.session.get(search_url, headers=self.headers) as response:
                if response.status != 200:
                    return []
                
                soup = BeautifulSoup(await response.text(), 'html.parser')
                results = []
                selectors = CONFIG['WORLDCAT_SELECTORS']
                
                for item in soup.select(selectors['items'])[:CONFIG['MAX_RESULTS_PER_SOURCE']]:
                    title_elem = item.select_one(selectors['title'])
                    author_elem = item.select_one(selectors['author'])
                    publisher_elem = item.select_one(selectors['publisher'])
                    if not title_elem:
                        continue
                        
                    book = BookData(
                        book_name=title_elem.text.strip(),
                        isbn=isbn,
                        authors=author_elem.text.strip() if author_elem else "",
                        publisher=publisher_elem.text.strip() if publisher_elem else "",
                        url=f"https://www.worldcat.org{title_elem['href']}" if title_elem.get('href') else "",
                        source="worldcat"
                    )
                    
                    if publisher_elem:
                        year_match = re.search(r'\b(19|20)\d{2}\b', publisher_elem.text)
                        if year_match:
                            book.year = year_match.group(0)
                    
                    results.append(book)
                    
                return results
        except Exception as e:
            print(f"WorldCat error: {e}", file=sys.stderr)
            return []

# =============================================================================
# Main Enrichment Class
# =============================================================================

class BookEnricher:
    """Main class for book metadata enrichment."""
    
    def __init__(self, api_key: str):
        """Initialize with Google Books API key."""
        self.session = aiohttp.ClientSession()
        self.api_key = api_key
        self.base_url = CONFIG['GOOGLE_BOOKS_API_URL']
        self.sources = [
            GoodreadsSource(self.session),
            WorldCatSource(self.session)
        ]
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, *_):
        await self.session.close()
    
    async def fetch_google_books(self, isbn: str) -> Optional[BookData]:
        """Fetch book data from Google Books API."""
        try:
            async with self.session.get(
                f"{self.base_url}?q=isbn:{isbn}&key={self.api_key}"
            ) as r:
                if r.status != 200:
                    print(f"Google Books API error: Status {r.status}")
                    return None
                    
                data = await r.json()
                if not data.get("totalItems", 0):
                    return None
                
                info = data["items"][0]["volumeInfo"]
                return BookData(
                    book_name=info.get("title", ""),
                    isbn=isbn,
                    authors=", ".join(info.get("authors", [])),
                    publisher=info.get("publisher", ""),
                    year=info.get("publishedDate", "")[:4],
                    pages=info.get("pageCount", 0),
                    rating=info.get("averageRating", 0.0),
                    url=data["items"][0].get("selfLink", ""),
                    source="google"
                )
        except Exception as e:
            print(f"Google Books API error for ISBN {isbn}: {e}", file=sys.stderr)
            return None

    async def get_book_data(self, book_name: str, isbn: str) -> Optional[BookData]:
        """Get book data from all available sources."""
        book = await self.fetch_google_books(isbn)
        if book:
            print(f"Found '{book_name}' in Google Books")
            return book
            
        print(f"\nNo Google Books data for '{book_name}' ({isbn}). Searching other sources...")
        
        all_results = []
        for source in self.sources:
            results = await source.search(book_name, isbn)
            all_results.extend(results)
            await asyncio.sleep(CONFIG['RATE_LIMIT_DELAY'])
        
        if not all_results:
            print(f"No results found for '{book_name}' ({isbn})")
            return None
            
        choices = [
            {
                'name': f"{b.book_name} by {b.authors} ({b.year}) - from {b.source}",
                'value': b
            }
            for b in all_results
        ]
        choices.append({'name': 'Skip this book', 'value': None})
        
        questions = [
            inquirer.List('book',
                         message=f"Choose the correct book for '{book_name}'",
                         choices=choices)
        ]
        
        answers = inquirer.prompt(questions)
        return answers['book'] if answers else None

    async def process_books(self, in_path: Path, out_path: Path) -> None:
        """Process all books from input file."""
        try:
            df_in = FileHandler.read_file(in_path)
            df_out = (FileHandler.read_file(out_path) 
                     if out_path.exists() 
                     else pd.DataFrame())
        except Exception as e:
            print(f"Error reading files: {e}")
            return

        new_books = df_in[~df_in['isbn'].astype(str).isin(df_out['isbn'].astype(str))]
        if new_books.empty:
            print("No new books to process")
            return

        results = []
        total = len(new_books)
        for idx, row in new_books.iterrows():
            print(f"\nProcessing book {idx + 1}/{total}")
            book = await self.get_book_data(row['book_name'], str(row['isbn']))
            if book:
                results.append(asdict(book))
            await asyncio.sleep(CONFIG['RATE_LIMIT_DELAY'])
        
        if results:
            try:
                FileHandler.write_file(
                    pd.concat([df_out, pd.DataFrame(results)]),
                    out_path
                )
                print(f"\nAdded {len(results)} new books")
            except Exception as e:
                print(f"Error writing output file: {e}")

# =============================================================================
# Main Execution
# =============================================================================

async def main() -> None:
    """Main entry point for the script."""
    print("Book Metadata Enrichment Tool")
    print("=" * 30 + "\n")
    
    # Get file format preferences
    try:
        format_type, in_file, out_file = FileHandler.get_file_preferences()
    except Exception as e:
        sys.exit(f"Error setting up files: {e}")
    
    # Get API key
    questions = [
        inquirer.Text('api_key',
                     message="Enter your Google Books API key:",
                     validate=lambda _, x: bool(x.strip()))
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        sys.exit("API key input cancelled")
    
    print(f"\nConfiguration:")
    print(f"- Format: {format_type.upper()}")
    print(f"- Input: {in_file}")
    print(f"- Output: {out_file}\n")
    
    try:
        async with BookEnricher(answers['api_key']) as enricher:
            await enricher.process_books(Path(in_file), Path(out_file))
    except Exception as e:
        sys.exit(f"Error during enrichment: {e}")

if __name__ == "__main__":
    """
    Example usage:
    1. Prepare input file (e.g., books.csv):
       book_name,isbn
       "The Great Gatsby","9780743273565"
       "1984","9780451524935"
       
    2. Install dependencies:
       pip install pandas aiohttp beautifulsoup4 inquirer openpyxl
       
    3. Run the script:
       python book_enricher.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")