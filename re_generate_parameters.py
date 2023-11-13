from promptflow import tool
import os
import sys
import openai
from promptflow.connections import AzureOpenAIConnection
from typing import List
import json
from dotenv import load_dotenv

load_dotenv()

@tool
def re_generate_parameters(question: str, azure_openai: AzureOpenAIConnection, documentation: List[dict], response_message: List[dict], feedback_message: str) -> str:

  openai.api_type = azure_openai.api_type
  openai.api_base = azure_openai.api_base
  openai.api_key = azure_openai.api_key
  openai.api_version = azure_openai.api_version

  function_name = response_message["function_call"]["name"]
  
  try:
      with open("available_functions.json", "r") as json_file:
          available_functions = json.load(json_file)

      if function_name not in available_functions:
          print("No such function")
          sys.exit()

      function_to_call = available_functions[function_name]

  except FileNotFoundError:
      print(f"Error: JSON file not found.")
      sys.exit()
  
  system_message = '''Je bent een chatbot die de gebruiker zal helpen bij het invullen van verschillende bedrijfsparameters. Je zal altijd moeten antwoorden in de vorm van een JSON formaat zoals aangegeven in de vraag. Voor het beantwoorden van de vragen, maak gebruik van de voorgaande context informatie. Als u het antwoord niet weet, geef dan aan dat u het niet weet zonder een speculatief antwoord te geven. Vermeld de bron van uw informatie alleen als u deze heeft gebruikt bij het opstellen van uw antwoord.'''
  
  messages = [
      {"role": "system", "content": system_message},
      {"role": "user","content": f"This is what you know:\n" + "\n".join([f"url: {item['url']}\ncontent: {item['content']}" for item in documentation])},
      {"role": "user","content": f"Also take this feedback into account: {feedback_message}"},
      {"role": "user", "content": question}
  ]
  #print(messages)
  function = function_to_call 

  response = openai.ChatCompletion.create(
      deployment_id=os.getenv("OPENAI_DEPLOYMENT_ID"),
      temperature=0,
      messages=messages,
      functions=function,
      function_call="auto"    
  )

  return response['choices'][0]['message']
