from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import DATA_PATH


def load_text_documents() -> list[Document]:
    data_folder = Path(DATA_PATH)
    documents = []

    for file_path in data_folder.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        document = Document(
            page_content=text,
            metadata={"source": file_path.name}
        )

        documents.append(document)

    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)
    return chunks