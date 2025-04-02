import os
from chromadb.config import Settings
import chromadb
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
import logging
from src.utils import create_product_document

logging.basicConfig(level=logging.ERROR)

class DatabaseManager:
    def __init__(self):
        self.text_collection = self.initialize_chroma_db("database_chroma/text", "electronics_text_dataset", is_image=False)
        self.image_collection = self.initialize_chroma_db("database_chroma/images", "electronics_image_dataset")

    def initialize_chroma_db(self, db_path, collection_name, is_image=True):
        if is_image:
            embedding_function = OpenCLIPEmbeddingFunction()
            image_loader = ImageLoader()
        else:
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            image_loader = None

        chroma_client = chromadb.PersistentClient(path=db_path)
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            data_loader=image_loader,
            metadata={"source": collection_name},
        )
        print(f"Current collection size: {collection.count()} items")
        return collection

    def check_existing_ids(self, collection, ids):
        existing_ids = set()
        if collection.count() > 0:
            all_results = collection.query(
                query_texts=[""], 
                n_results=collection.count(),
                include=[]
            )
            existing_ids = set(all_results['ids'][0])
        return [id for id in ids if id not in existing_ids]

    def add_products_to_db(self, products_df, image_folder_path=None, batch_size=5000):
        """
        Process products and add them to both text and image collections.
        """
        documents, metadata, ids, image_uris = [], [], [], []
        
        # Process each product
        for product in products_df.to_dict('records'):
            doc, meta, doc_id, uri = create_product_document(product, image_folder_path)
            if doc_id is not None:
                documents.append(doc)
                metadata.append(meta)
                ids.append(doc_id)
                image_uris.append(uri)

        # Add to text collection
        print("Processing text collection...")
        new_text_ids = self.check_existing_ids(self.text_collection, ids)
        self._batch_add_text(documents, metadata, ids, new_text_ids, batch_size)

        # Add to image collection
        print("Processing image collection...")
        new_image_ids = self.check_existing_ids(self.image_collection, ids)
        self._batch_add_images(image_uris, metadata, ids, new_image_ids, batch_size)

        print(f"Text Collection Size: {self.text_collection.count()}")
        print(f"Image Collection Size: {self.image_collection.count()}")

    def _batch_add_text(self, documents, metadata, ids, new_ids, batch_size):
        new_documents = [doc for doc, doc_id in zip(documents, ids) if doc_id in new_ids]
        new_metadata = [meta for meta, doc_id in zip(metadata, ids) if doc_id in new_ids]
        
        for i in range(0, len(new_ids), batch_size):
            batch_docs = new_documents[i:i + batch_size]
            batch_meta = new_metadata[i:i + batch_size]
            batch_ids = new_ids[i:i + batch_size]
            
            self.text_collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids,
            )
            print(f"Added batch #{i//batch_size + 1}: {len(batch_docs)} documents")

    def _batch_add_images(self, image_uris, metadata, ids, new_ids, batch_size):
        new_uris = [uri for uri, id in zip(image_uris, ids) if id in new_ids]
        new_metadata = [meta for meta, doc_id in zip(metadata, ids) if doc_id in new_ids]
        
        for i in range(0, len(new_ids), batch_size):
            batch_uris = new_uris[i:i + batch_size]
            batch_meta = new_metadata[i:i + batch_size]
            batch_ids = new_ids[i:i + batch_size]
            
            self.image_collection.add(
                ids=batch_ids,
                uris=batch_uris,
                metadatas=batch_meta
            )
            print(f"Added batch #{i//batch_size + 1}: {len(batch_uris)} images") 