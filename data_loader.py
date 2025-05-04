import os
import pickle
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm.auto import tqdm
import torch


def load_pdfs(main_script_path):
    documents = []
    print("Lade Hauptskript...")
    loader = PyPDFLoader(main_script_path)
    main_docs = loader.load()

    for doc in main_docs:
        doc.metadata['source_type'] = 'Hauptskript'
        doc.metadata['file_name'] = os.path.basename(main_script_path)

    documents.extend(main_docs)
    print(f"Hauptskript geladen: {len(main_docs)} Seiten")

    return documents


def create_chunks(documents):
    print("Erstelle Chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=59,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Chunks erstellt: {len(chunks)} Chunks")
    return chunks


def create_vectorstore(chunks, vectorstore_path, metadata_path):
    print("Erstelle Vektorspeicher...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Nutze Device: {device}")

    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={
            'device': device,
            'trust_remote_code': True,
            'load_in_8bit': True
    },
    encode_kwargs={
            'normalize_embeddings': True,
            'batch_size': 128
    }
)

    print("Erstelle Embeddings und Vektorspeicher...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=vectorstore_path,
        collection_metadata={"hnsw:space": "cosine"}
    )

    metadata = {
        'main_script_count': len(chunks),
        'total_count': len(chunks),
        'model_name': 'BAAI/bge-m3',
        'chunk_size': 512,
        'chunk_overlap': 50,
        'device': device
    }

    print("Speichere Vektorspeicher...")
    vectorstore.persist()
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)

    print(f"Vektorspeicher erstellt und gespeichert:")
    print(f"  - Hauptskript: {metadata['main_script_count']} Chunks")
    print(f"  - Gesamt: {metadata['total_count']} Chunks")
    print(f"  - Modell: {metadata['model_name']}")
    print(f"  - Device: {metadata['device']}")

    return vectorstore, metadata


def load_vectorstore(vectorstore_path, metadata_path, chunks=None):
    try:
        print("Lade Vektorspeicher...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
            model_kwargs={
                'device': device,
                'trust_remote_code': True
            },
            encode_kwargs={
                'normalize_embeddings': True,
                'batch_size': 64
            }
        )

        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )

        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)

        collection_size = vectorstore._collection.count()
        print(f"Vektorspeicher geladen mit {collection_size} Dokumenten")
        print(f"  - Hauptskript: {metadata['main_script_count']} Chunks")
        print(f"  - Modell: {metadata.get('model_name', 'BAAI/bge-m3')}")
        print(f"  - Device: {metadata.get('device', device)}")

        return vectorstore, metadata
    except Exception as e:
        print(f"Fehler beim Laden: {e}")
        if chunks is not None:
            print("Erstelle neuen Vektorspeicher...")
            return create_vectorstore(chunks, vectorstore_path, metadata_path)
        else:
            raise e