import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from collections import defaultdict
import re
import json
import time
import os
import sys
import nltk
from nltk.corpus import stopwords

def download_stopwords():
    try:
        import os 
        # Try finding the stopwords dataset
        nltk.data.find('corpora/stopwords')
    except LookupError:
        # If not found, download it
        print("Downloading NLTK stopwords package...")
        nltk.download('stopwords')
    else:
        pass

def load_stopwords():
    # Ensure stopwords are downloaded
    download_stopwords()
    
    # Now load the stopwords
    stop_words = set(stopwords.words('english'))
    return stop_words

def save_full_texts(full_texts, filename='full_texts.json'):
    with open(filename, 'w') as f:
        json.dump(full_texts, f)

def load_full_texts(filename='full_texts.json'):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        return json.load(f)

def extract_relevant_content(soup, stop_words):
    # Decompose specified classes
    for cls in ["tag-item", "next"]:
        for element in soup.find_all(class_=cls):
            element.decompose()

    # Extract and clean text
    text = soup.get_text(separator=' ', strip=True).lower()  # Convert to lowercase
    words = text.split()
    filtered_content = ' '.join([word for word in words if word.lower() not in stop_words])

    return filtered_content

def crawl_site(base_url="https://quotes.toscrape.com", stop_words=None):
    pages_content = {}
    full_texts = {}  # Dictionary to store full page content
    urls_to_visit = {base_url}
    visited_urls = set()

    while urls_to_visit:
        url = urls_to_visit.pop()
        if url in visited_urls:
            continue

        time.sleep(6)  # Proper politeness delay, consider increasing if needed
        response = requests.get(url)
        visited_urls.add(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            full_text = soup.get_text(separator=' ', strip=True).lower()  # Ensure it's lowercased
            full_texts[url] = full_text
            content = extract_relevant_content(soup, stop_words)
            pages_content[url] = content

            for link in soup.find_all('a', href=True):
                link_url = link['href']
                if re.match(r'^/[^/]', link_url):
                    full_link = base_url + link_url if link_url.startswith('/') else base_url + '/' + link_url
                    if full_link not in visited_urls:
                        urls_to_visit.add(full_link)

    return pages_content, full_texts

def build_index(pages_content):
    index = {}
    tokenizer = re.compile(r"[^\w\s]")
    
    for url, content in pages_content.items():
        cleaned_content = tokenizer.sub('', content)
        words = cleaned_content.split()
        for word in words:
            if word not in index:
                index[word] = {}
            if url not in index[word]:
                index[word][url] = 0
            index[word][url] += 1
    return index

def save_index(index, filename='index.json'):
    with open(filename, 'w') as f:
        json.dump(index, f)

def load_index(filename='index.json'):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        return json.load(f)

def print_index(index, word):
    if word in index:
        table = PrettyTable()
        table.field_names = ["URL", "Frequency"]
        # Collect data in a list for sorting
        data_list = [(url, frequency) for url, frequency in index[word].items()]
        # Sort the list by frequency in descending order
        sorted_data = sorted(data_list, key=lambda x: x[1], reverse=True)
        for url, frequency in sorted_data:
            table.add_row([url, frequency])
        
        table_string = table.get_string()
        line_length = len(table_string.splitlines()[0])  # Get the length of one line of the table

        # Print formatted output
        print('-' * line_length)
        print(f"Inverted index for '{word}':")
        print('-' * line_length)
        print(table)
    else:
        print(f"No entry found for '{word}'.")

def find_in_index(index, query):
    full_texts = load_full_texts()  # Load full texts

    if not full_texts:
        print("Failed to load full texts or they are empty.")
        return

    # Normalize the query to lowercase
    query = query.lower()
    words = re.sub(r"[^\w\s]", '', query).split()

    if not words:
        print("No search words provided.")
        return

    phrase = " ".join(words)
    phrase_hits = defaultdict(int)
    any_words_hits = defaultdict(int)

    for word in words:
        if word in index:
            for url in index[word]:
                any_words_hits[url] += 1
                page_content = full_texts.get(url, "")
                if page_content:
                    phrase_hits[url] += page_content.count(phrase)

    results = []
    for url in any_words_hits.keys():
        results.append({
            'url': url,
            'adjacent': phrase_hits[url],
            'any_words': any_words_hits[url],
            'words_found': ', '.join(words)
        })

    results.sort(key=lambda x: (-x['adjacent'], -x['any_words']))

    if results:
        table = PrettyTable()
        table.field_names = ["URL", "Adjacent", "Any Words", "Words Found"]
        for result in results:
            if result['adjacent'] > 0 or result['any_words'] > 0:
                table.add_row([result['url'], result['adjacent'], result['any_words'], result['words_found']])
        print(table)
    else:
        print("No pages found containing specified words or phrases.")

def main():
    # Load stopwords
    stop_words = load_stopwords()

    commands = {
        'build': lambda: [save_index(build_index(crawl_site(stop_words=stop_words)[0])),
                          save_full_texts(crawl_site(stop_words=stop_words)[1])],
        'load': lambda: load_index(),
        'print': lambda word: print_index(load_index(), word),
        'find': lambda *words: find_in_index(load_index(), ' '.join(words))
    }
    if len(sys.argv) < 2:
        print("Usage: python search.py [command] [arguments]")
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd in commands:
        commands[cmd](*args)
    else:
        print("Invalid command.")

if __name__ == "__main__":
    main()
