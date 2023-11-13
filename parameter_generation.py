from promptflow import tool
import openai
from openai import OpenAI
from promptflow.connections import AzureOpenAIConnection
from typing import List, Dict
import time
import sys
import json


@tool
def parameter_generation(question: str, azure_openai: AzureOpenAIConnection, data: List[Dict], response_message: List[dict]) -> str:

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

  function = function_to_call
  
  system_message = '''Je bent een chatbot die de gebruiker zal helpen bij het invullen van verschillende bedrijfsparameters. Je zal altijd moeten antwoorden in de vorm van een JSON formaat zoals aangegeven in de vraag. Voor het beantwoorden van de vragen, maak gebruik van de voorgaande context informatie. Als u het antwoord niet weet, geef dan aan dat u het niet weet zonder een speculatief antwoord te geven. Vermeld de bron van uw informatie alleen als u deze heeft gebruikt bij het opstellen van uw antwoord.'''

  client = OpenAI()
  
  file = client.files.create(
    file=data,
    purpose='assistants'
  )

  assistant = client.beta.assistants.create(
    instructions=system_message,
    model="gpt-3.5-turbo",
    tools=[{"type": "retrieval"}, {"type": "function","function": function}],
    file_ids=[file.id]
  )

  thread = client.beta.threads.create()

  message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content=question
  )
  
  run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
      instructions=system_message
  )

  while run.status not in ["complete", "failed"]:
      run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        assistant_id=assistant.id
      )
      #print(run)
      print(run.status)
      time.sleep(10)

  messages = client.beta.threads.messages.list(
      thread_id=thread.id,
  )

  for message in messages:
      print(message.role + ": " + message.content[0].text.value)

