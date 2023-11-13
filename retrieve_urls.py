from promptflow import tool
from serpapi import GoogleSearch
import requests
import math
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def retrieve_serp_urls(question: str, num_search_results: int) -> str:

  '''
  params = {
          "engine": "google",
          "q": question,
          "location_requested": "Belgium",
          "location_used": "Belgium",
          "google_domain": "google.be",
          "hl": "nl",
          "gl": "be",
          "num": "10",
          "device": "desktop",
          "lr": "lang_be|lang_en",
          "api_key": os.getenv("SERP_API_KEY")
      }
  
  params2 = {
          "engine": "google",
          "q": question,
          "location_requested": "Belgium",
          "location_used": "Belgium",
          "google_domain": "google.be",
          "hl": "nl",
          "gl": "be",
          "num": "10",
          "device": "desktop",
          "lr": "lang_be|lang_en",
          "api_key": os.getenv("SERP_API_KEY"),
          "tbm": "nws"
      }

  search = GoogleSearch(params)
  results = search.get_dict()
  url_list = [result['link'] for result in results["organic_results"]]

  nws_search = GoogleSearch(params2)
  nws_results = nws_search.get_dict()
  nws_url_list = [result['link'] for result in nws_results["news_results"]]

  return url_list + nws_url_list

  

  subscription_key = os.getenv("BING_SEARCH_KEY")

  search_url = "https://api.bing.microsoft.com/v7.0/search"

  headers = {"Ocp-Apim-Subscription-Key": subscription_key}
  params = {"q": question, "textDecorations": True, "textFormat": "HTML"}
  response = requests.get(search_url, headers=headers, params=params)
  response.raise_for_status()
  search_results = response.json()

  pages = search_results['webPages']
  results = pages['value']

  for result in results:
    print(result['url'])

  # Convert to json string
  return [result['url'] for result in results]

  '''
  def get_urls(start_item: int, num: int):

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": f"{question} -filetype:pdf -filetype:xml",
        "hl": "nl",
        "gl": "be",
        "num": num,
        "cr": "Belgium",
        "lr": "lang_be|lang_en",
        "key": os.getenv("GOOGLE_SEARCH_ENGINE_KEY"),
        "start": start_item
    }

    response = requests.get(url, params=params)
    results = response.json()['items']

    #for item in results:
    #   print(item['link'])

    return [item['link'] for item in results]


  if num_search_results > 100:
      raise NotImplementedError('Google Custom Search API supports a max of 100 results')
  elif num_search_results > 10:
      num = 10  # this cannot be > 10 in the API call
      calls_to_make = math.ceil(num_search_results / 10)
  else:
      calls_to_make = 1
      num = num_search_results

  start_item = 1
  items_to_return = []

  while calls_to_make > 0:
      items = get_urls(start_item, num)
      items_to_return.extend(items)
      calls_to_make -= 1
      start_item += num
      leftover = num_search_results - start_item + 1
      if 0 < leftover < 10:
          num = leftover

  for item in items_to_return:
      print(item)

  return items_to_return
