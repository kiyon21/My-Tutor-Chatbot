import argparse
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.openai import OpenAIChat
import openai
from dotenv import load_dotenv 
import os

load_dotenv()

CHROMA_PATH = 'chroma'
PROMPT_TEMPLATE = """
    Answer the question based only on the following context:
    {context}
    
    ---
    Answer the question based on the above context: {question} 
    """
openai.api_key = os.getenv("OPENAI_API_KEY")


def query_rag(query_text: str):

    embedding_function = get_embedding_function()
    db = Chroma (
        persist_directory=CHROMA_PATH,
        embedding_function= embedding_function
    )

    # runs query text on database
    results = db.similarity_search_with_score(query_text, k=10)
    sources = [doc.metadata.get("id", None) for doc, _score in results]

    context_text = "\n\n---\n\n".join([doc.page_content for doc,_score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context =context_text, question = query_text)

    response = openai.chat.completions.create(
        model ="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = response["choices"][0]["message"]["content"]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

def main():
    
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

if __name__ == "__main__":
    main()

