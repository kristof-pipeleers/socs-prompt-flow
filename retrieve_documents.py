from typing import List
from promptflow import tool
from typing import List, Dict
from promptflow.connections import AzureOpenAIConnection
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def retrieve_documents(question: str, azure_openai: AzureOpenAIConnection, data: List[Dict]) -> str:

    # connect with openAI
    openai.api_type = azure_openai.api_type
    openai.api_base = azure_openai.api_base
    openai.api_key = azure_openai.api_key
    openai.api_version = azure_openai.api_version

    # generate embedding for certain text
    def get_embedding(text, model, deployment_id):
        text = text.replace("\n", " ")
        return openai.Embedding.create(input = [text], model=model, deployment_id=deployment_id)['data'][0]['embedding']
    
    # search through the documents for a specific product
    def search_relevant_documents(docs_df, question, n=3):
        question_embedding = get_embedding(
            question,
            model="text-embedding-ada-002",
            deployment_id=os.getenv("EMBEDDINGS_DEPLOYMENT_ID")
        )
        docs_df["similarity"] = docs_df.contentVector.apply(lambda x: cosine_similarity(x, question_embedding))

        results = (
            docs_df.sort_values("similarity", ascending=False)
            .head(n)
        )

        return results

    # chunk the documents with max 'chunck_size' tokens
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=350, chunk_overlap=20
    )
    chunks = text_splitter.split_documents(data)
    
    
    # put the chunks in a dataframe
    DOCUMENTS = []

    for chunk in chunks:
        DOCUMENTS.append({
            "id": str(uuid.uuid4()),
            "url": chunk.metadata['url'],
            "content": chunk.page_content, 
            "contentVector": get_embedding(chunk.page_content, model="text-embedding-ada-002", deployment_id=os.getenv("EMBEDDINGS_DEPLOYMENT_ID"))
        })
    
    docs_df = pd.DataFrame(DOCUMENTS)
    
    # search for the relevant documents using vector search
    results = search_relevant_documents(docs_df, question, n=7)

    # return the searched results as a List
    docs = []
    
    for result in results.itertuples(index=False):
        doc = {
            "url": result.url,
            "content": result.content
        }
        docs.append(doc)
        print(f"score: {result.similarity}")
        print(f"url: {result.url}")
        #print(f"content: {result.content}")

    return docs
