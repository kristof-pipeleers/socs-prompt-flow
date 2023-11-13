from promptflow import tool
from typing import List
from apify_client import ApifyClient
import requests
from langchain.document_loaders.base import Document
import warnings
import requests
from bs4 import BeautifulSoup
import re
import cloudscraper
from dotenv import load_dotenv

load_dotenv()

@tool
def crawl_urls(urls: List[str]) -> str:

    '''
    try:
        # Initialize the ApifyClient with your API token
        client = ApifyClient(os.getenv("APIFY_API_KEY"))

        # Prepare the Actor input
        run_input = {
            "startUrls": [
                {"url": url} for url in urls
            ],
            "crawlerType": "playwright:firefox",
            "includeUrlGlobs": [],
            "excludeUrlGlobs": [],
            "maxCrawlDepth": 0,
            "maxCrawlPages": 9999999,
            "initialConcurrency": 0,
            "maxConcurrency": 200,
            "initialCookies": [],
            "proxyConfiguration": { "useApifyProxy": True },
            "requestTimeoutSecs": 60,
            "dynamicContentWaitSecs": 10,
            "maxScrollHeightPixels": 5000,
            "removeElementsCssSelector": """nav, footer, script, style, noscript, svg,
        [role=\"alert\"],
        [role=\"banner\"],
        [role=\"dialog\"],
        [role=\"alertdialog\"],
        [role=\"region\"][aria-label*=\"skip\" i],
        [aria-modal=\"true\"]""",
            "removeCookieWarnings": True,
            "clickElementsCssSelector": "[aria-expanded=\"false\"]",
            "htmlTransformer": "readableText",
            "readableTextCharThreshold": 100,
            "aggressivePrune": False,
            "debugMode": False,
            "debugLog": False,
            "saveHtml": False,
            "saveMarkdown": True,
            "saveFiles": False,
            "saveScreenshots": False,
            "maxResults": 9999999,
        }

        # Run the Actor and wait for it to finish
        run = client.actor("aYG0l9s7dbB7j3gbS").call(run_input=run_input)

        # Check if the run has finished
        if run.get('status') == "SUCCEEDED": 
            
            loader = ApifyDatasetLoader(
                dataset_id=run['defaultDatasetId'],
                dataset_mapping_function=lambda dataset_item: Document(
                    page_content=dataset_item["text"], metadata={"url": dataset_item["url"]}
                ),
            )
            return loader.load()
        else:
            raise Exception("Actor run did not succeed. Status: " + run.get('status'))

    except Warning as w:

        print(f"Caught a warning: scraping is taking 60s extra") 

     

    loader = ApifyDatasetLoader(
        dataset_id="zWMuetbL0YT3OQ95k", #MOAzJ8ZldZxObKghB
        dataset_mapping_function=lambda dataset_item: Document(
            page_content=dataset_item["text"], metadata={"url": dataset_item["url"]}
        ),
    )

    return loader.load()

    '''

    def get_static_content(url, timeout):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            print("static scraper used")
            return response.content
        except requests.RequestException as e:
            print(f"Request to {url} failed: {e}")
            return None

    def get_dynamic_content(url, timeout):
        try:
            scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'windows', 'mobile': False})
            response = scraper.get(url, timeout=timeout)
            print("dynamic scraper used")
            return response.content
        except Exception as e:
            print(f"Request to {url} failed: {e}")
            return None

    def extract_text_from_html(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Use more specific tags for main content, or find the main container of the content
        content_tags = ['p', 'article', 'section']
        
        # Tags to be excluded by class or id
        excluded_classes = ['header', 'footer', 'nav', 'sidebar', 'menu', 'breadcrumb', 'pagination', 'legal', 'advertisement']
        excluded_ids = ['header', 'footer', 'navigation', 'sidebar', 'menu', 'breadcrumbs', 'pagination', 'legal', 'ads']
        
        # Use a set to store unique blocks of text
        unique_texts = set()

        for tag in content_tags:
            for element in soup.find_all(tag):
                class_list = element.get('class', [])
                id_name = element.get('id', '')
                if not any(excluded in class_list for excluded in excluded_classes) and id_name not in excluded_ids:
                    text_block = re.sub(r'\s+', ' ', element.get_text()).strip()
                    if text_block not in unique_texts:
                        unique_texts.add(text_block)
                        

        text = ' '.join(unique_texts)
        
        return text
    
    docs = []
    for url in urls:
        static_content = get_static_content(url, 10)
        
        if static_content and len(static_content) > 100:
            text = extract_text_from_html(static_content)
        else:
            dynamic_content = get_dynamic_content(url, 10)
            if dynamic_content is None:
                print("None returned")
            elif dynamic_content:
                text = extract_text_from_html(dynamic_content)
            else:
                print("Failed to retrieve content from the website.")
                continue

        print(url)
        #print(text)

        docs.append(Document(page_content=text, metadata={"url": url}))

    return docs

    