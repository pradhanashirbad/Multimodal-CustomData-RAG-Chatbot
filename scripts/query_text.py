import os
import sys
import time
from pathlib import Path
import argparse

# Add the src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from db_manager import DatabaseManager
from chatbot import ELectronicsChatbot

def main():
    parser = argparse.ArgumentParser(description='Chatbot text query')
    parser.add_argument('--query', type=str, required=True, help='query to perform')
    args = parser.parse_args()

    # Initialize database manager
    db_manager = DatabaseManager()
    
    print("\n------ Perform query using chatbot ------")
    start_time = time.time()
    
    chatbot = ELectronicsChatbot(db_manager.text_collection, db_manager.image_collection)
    response = chatbot.query(args.query)
    
    print("\nAnswer:")
    print(response["answer"])
    
    print(f"Query execution time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main() 