# import argparse
from pathlib import Path
import typer
# from langchain.vectorstores.chroma import Chroma
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
# from langchain_community.llms.ollama import Ollama
from langchain_ollama import OllamaLLM

from get_embedding_function import get_embedding_function
import ollamamanager as om
import tracelogger

logger = tracelogger.getLogger(__name__)
app = typer.Typer(add_completion=False)
CHROMA_PATH = ".chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

@app.command()
def main(
    query_text: str,
    model:str='mistral'
):
    with om.OllamaServerCtx():
        query_rag(query_text, model)


def query_rag(
    query_text: str,
    model:str='mistral'
):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)
    # [print(type(doc.page_content)) for doc, _score in results]
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    documents = [d.name for d in Path('data').glob('*.pdf')]
    logger.trace(f'{documents = }')
    context_text += '\n\n\n\nsource pdf documents: ' + ', '.join(documents)
    print(f'{context_text = !s}')
    
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = OllamaLLM(model=model)
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    logger.info(f'{query_text = }')
    logger.info(f'{formatted_response = !s}')
    return response_text


if __name__ == "__main__":
    app()