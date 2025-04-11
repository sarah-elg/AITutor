
import os
import pickle
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def load_pdfs(main_script_path, literature_dir):
    documents = []
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
        pdf_files = [os.path.join(root, file)
                    for root, _, files in os.walk(literature_dir)
                    for file in files if file.lower().endswith('.pdf')]

        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(pdf_file)
                lit_docs = loader.load()

                # Füge Metadaten hinzu
                for doc in lit_docs:
                    doc.metadata['source_type'] = 'Literatur'
                    doc.metadata['file_name'] = os.path.basename(pdf_file)

                documents.extend(lit_docs)
                print(f"Literatur geladen: {os.path.basename(pdf_file)} - {len(lit_docs)} Seiten")
            except Exception as e:
                print(f"Fehler beim Laden von {pdf_file}: {e}")

    return documents

def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Chunks erstellt: {len(chunks)} Chunks")
    return chunks

def create_vectorstore(chunks, vectorstore_path, metadata_path):
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    # Erstelle Vektorspeicher
    vectorstore = Chroma.from_documents(chunks, embedding_model, persist_directory=vectorstore_path)

    # Speichere Metadaten
    metadata = {
        'main_script_count': sum(1 for doc in chunks if doc.metadata.get('source_type') == 'Hauptskript'),
        'literature_count': sum(1 for doc in chunks if doc.metadata.get('source_type') == 'Literatur'),
        'total_count': len(chunks)
    }

    # Speichere Vektorspeicher und Metadaten
    vectorstore.persist()
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)

    print(f"Vektorspeicher erstellt und gespeichert")
    print(f"  - Hauptskript: {metadata['main_script_count']} Chunks")
    print(f"  - Literatur: {metadata['literature_count']} Chunks")
    print(f"  - Gesamt: {metadata['total_count']} Chunks")

    return vectorstore, metadata

def load_vectorstore(vectorstore_path, metadata_path, chunks=None):
    try:
        # Lade Vektorspeicher
        embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embedding_model)

        # Lade Metadaten
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)

        # Bei ChromaDB können wir die Anzahl der Dokumente anders abrufen
        collection_size = vectorstore._collection.count()
        print(f"Vektorspeicher geladen mit {collection_size} Dokumenten")
        print(f"  - Hauptskript: {metadata['main_script_count']} Chunks")
        print(f"  - Literatur: {metadata['literature_count']} Chunks")

        return vectorstore, metadata
    except Exception as e:
        print(f"Fehler beim Laden des Vektorspeichers: {e}")
        if chunks is not None:
            print("Erstelle neuen Vektorspeicher...")
            return create_vectorstore(chunks, vectorstore_path, metadata_path)
        else:
            raise e
