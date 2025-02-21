# import argparse
import os
from pathlib import Path
import shutil
import typer
import logging
# from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
# from langchain.vectorstores.chroma import Chroma
from langchain_chroma import Chroma

import ollamamanager as om
import tracelogger


logger = tracelogger.getLogger(__name__)
app = typer.Typer(add_completion=False)
CHROMA_PATH = ".chroma"
DATA_PATH = "data"


@app.command()
def main(
    reset:bool=False,
    chroma_path:str=CHROMA_PATH,
    data_path:str=DATA_PATH
):

    # Check if the database should be cleared (using the --clear flag).
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--reset", action="store_true", help="Reset the database.")
    # args = parser.parse_args()
    # if args.reset:
    if reset:
        logger.info("✨ Clearing Database")
        clear_database(chroma_path)

    # Create (or update) the data store.
    documents = load_documents(data_path)
    chunks = split_documents(documents)
    with om.OllamaServerCtx():
        add_to_chroma(chunks, chroma_path)


def load_documents(data_path:str):
    document_loader = PyPDFDirectoryLoader(data_path)
    logger.trace(f'loading documents from {data_path}...')
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    logger.trace(f'splitting documents...')
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document], chroma_path:str):
    # Load the existing database.
    db = Chroma(
        persist_directory=chroma_path, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    logger.info(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        logger.info(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # db.persist()
    else:
        logger.info("✅ No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0


    for chunk in chunks:
        # logger.trace(f'{chunk.metadata = }')
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        title = chunk.metadata.get('title')
        current_page_id = f"{source}:{page}"
        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id
        
        name = Path(source).stem
        logger.trace(f'{name = }')
        
        title = name + ' ' + (title if title is not None else '')
        logger.trace(f'{title = }')
        # logger.trace(f'{current_page_id = }')
        # logger.trace(f'{source = }')
        # logger.trace(f'{chunk_id = }')

    return chunks


def clear_database(chroma_path:str):
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)


if __name__ == "__main__":
    app()
