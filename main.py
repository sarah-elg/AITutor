import os

MAIN_SCRIPT_PATH = "./BS2zsm.pdf"
CACHE_DIR = "./cache"
VECTORSTORE_PATH = os.path.join(CACHE_DIR, "chroma_db")
METADATA_PATH = os.path.join(CACHE_DIR, "metadata.pkl")

os.makedirs(CACHE_DIR, exist_ok=True)

from data_loader import load_pdfs, create_chunks, load_vectorstore, create_vectorstore
from tutor import OptimizedBS2Tutor
from gradio_interface import GradioInterface

def initialize_tutor():
    """Initialisiert den Tutor und gibt ihn zurück"""
    if os.path.exists(VECTORSTORE_PATH) and os.path.exists(METADATA_PATH):
        print("Lade existierenden Vektorspeicher...")
        vectorstore, metadata = load_vectorstore(VECTORSTORE_PATH, METADATA_PATH)
    else:
        print("Erstelle neuen Vektorspeicher...")
        documents = load_pdfs(MAIN_SCRIPT_PATH)
        chunks = create_chunks(documents)
        vectorstore, metadata = create_vectorstore(chunks, VECTORSTORE_PATH, METADATA_PATH)

    tutor = OptimizedBS2Tutor(vectorstore)
    return tutor, vectorstore

def create_demo():
    """Erstellt das Gradio-Interface"""
    tutor, vectorstore = initialize_tutor()
    interface = GradioInterface(tutor)
    demo = interface.create_interface()
    return demo, tutor, vectorstore

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    demo, _, _ = create_demo()
    demo.launch(share=True)

if __name__ == "__main__":
    main()