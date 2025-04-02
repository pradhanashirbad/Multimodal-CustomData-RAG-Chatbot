import os
import sys
import time
from pathlib import Path
import argparse
import numpy as np
from PIL import Image

# Add the src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from db_manager import DatabaseManager
from chatbot import ELectronicsChatbot

def main():
    parser = argparse.ArgumentParser(description='Image-based chatbot query')
    parser.add_argument('--image_path', type=str, required=True, help='path to query image')
    args = parser.parse_args()

    # Initialize database manager
    db_manager = DatabaseManager()
    
    print("\n------ Perform image query using chatbot ------")
    start_time = time.time()
    
    chatbot = ELectronicsChatbot(db_manager.text_collection, db_manager.image_collection)
    
    # Load and process image
    image_npy = np.array(Image.open(args.image_path))
    response = chatbot.query_image(image_npy)
    
    print("\nAnswer:")
    print(response["answer"])
    print("\nSources:")
    for i, metadata in enumerate(response["image_metadatas"][:5], 1):
        print(f"\nSource {i}:")
        print(f"Product ID: {metadata.get('product_id', 'N/A')}")
        print(f"Name: {metadata.get('name', 'N/A')}")
        print(f"Price: ${metadata.get('discount_price', 'N/A')}")
        print(f"Rating: {metadata.get('ratings', 'N/A')}")
    
    print(f"Query execution time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main() 