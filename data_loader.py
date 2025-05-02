import os
import pickle
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm.auto import tqdm
import torch


def load_pdfs(main_script_path, literature_dir):
    documents = []
    print("Lade PDFs...")

    # Lade Hauptskript
    loader = PyPDFLoader(main_script_path)
    main_docs = loader.load()

    # Füge Metadaten hinzu
    for doc in main_docs:
        doc.metadata['source_type'] = 'Hauptskript'
        doc.metadata['file_name'] = os.path.basename(main_script_path)

    documents.extend(main_docs)
    print(f"Hauptskript geladen: {len(main_docs)} Seiten")

    # Lade Literatur
    if os.path.exists(literature_dir):
        pdf_files = [
            os.path.join(root, file)
            for root, _, files in os.walk(literature_dir)
            for file in files if file.lower().endswith('.pdf')
        ]

        for pdf_file in tqdm(pdf_files, desc="Lade Literatur"):
            try:
                loader = PyPDFLoader(pdf_file)
                lit_docs = loader.load()

                # Füge Metadaten hinzu
                for doc in lit_docs:
                    doc.metadata['source_type'] = 'Literatur'
                    doc.metadata['file_name'] = os.path.basename(pdf_file)

                documents.extend(lit_docs)
                print(f"Geladen: {os.path.basename(pdf_file)} - {len(lit_docs)} Seiten")
            except Exception as e:
                print(f"Fehler bei {pdf_file}: {e}")

    return documents


def create_chunks(documents):
    print("Erstelle Chunks...")
    # Optimierte Chunk-Größe für bge-m3
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

    # Prüfe GPU-Verfügbarkeit
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Nutze Device: {device}")

    # Optimierte Embedding-Konfiguration für bge-m3
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

    # Erstelle Vektorspeicher mit Batch-Processing
    print("Erstelle Embeddings und Vektorspeicher...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=vectorstore_path,
        collection_metadata={"hnsw:space": "cosine"}
    )

    # Speichere Metadaten
    metadata = {
        'main_script_count': sum(1 for doc in chunks if doc.metadata.get('source_type') == 'Hauptskript'),
        'literature_count': sum(1 for doc in chunks if doc.metadata.get('source_type') == 'Literatur'),
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
    print(f"  - Literatur: {metadata['literature_count']} Chunks")
    print(f"  - Gesamt: {metadata['total_count']} Chunks")
    print(f"  - Modell: {metadata['model_name']}")
    print(f"  - Device: {metadata['device']}")

    return vectorstore, metadata


def load_vectorstore(vectorstore_path, metadata_path, chunks=None):
    try:
        print("Lade Vektorspeicher...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Optimierte Embedding-Konfiguration für bge-m3
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
        print(f"  - Literatur: {metadata['literature_count']} Chunks")
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