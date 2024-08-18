# Web Content Crawler and Search Tool

This project contains a Python script that converts a decimal string into its binary equivalent. The script also includes input validation to ensure that the input is a valid number.

## Features

- **Website Crawling**: Crawls through a specified website, extracting and processing content from multiple pages.
- **Content Extraction**: Filters out unnecessary content by removing elements with specified classes and stop words.
- **Inverted Index**: Builds an index that allows for efficient searching of terms and phrases across the crawled content.
- **Search Functionality**: Provides case-insensitive search capabilities to find occurrences of specific words or phrases within the indexed content.
- **Customizable Exclusions**: Allows users to specify which HTML elements (by class) should be excluded during content extraction.

## Getting Started

### Prerequisites

- Python 3.x installed on your system.
- Requests, BeautifulSoup, NLTK and PrettyTable installed on your system or within your environment. They can be installed using this command:
    ```bash
    pip install requests beautifulsoup4 prettytable nltk
    ```

### Running the Script

1. Clone the repository or download the script file.
2. Open a terminal or command prompt.
3. Navigate to the directory containing the script.
4. **Run the script**: Use the following command to execute the script with the desired command:

   ```bash
   python3 search.py [command] [arguments]
   ```

5. Available commands:
    - **build**: Crawl the website, extract content, build the index, and save the full texts.
    - **load**: Load a previously saved index from a file.
    - **print [word]**: Print the inverted index for a specific word.
    - **find [query]**: Search for specific words or phrases across the indexed content.

### Example

1. Build the Index:
    ```bash
        python3 search.py build
    ```
2. Load the Index:
    ```bash
    python3 search.py load
    ```
3. Search for a term or multiple terms:
    ```bash
    
    python3 search.py find Albert Einstein

    +------------------------------------------+----------+------------+------------------+
    | URL                                      | Adjacent | Any Words  | Words Found      |
    +------------------------------------------+----------+------------+------------------+
    | https://quotes.toscrape.com/page/1/      | 2        | 5          | albert, einstein |
    +------------------------------------------+----------+------------+------------------+

    ```

