import os
import sys
import time
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from data_processor import DataProcessor
from db_manager import DatabaseManager

def main():
    # Initialize paths
    data_file = "data/raw/electronics_product.csv"
    image_folder = "data/images/images_electronics"
    raw_data_path = "data/raw"

    # Initialize components
    start_time = time.time()
    data_processor = DataProcessor(raw_data_path)
    db_manager = DatabaseManager()
    print(f"Step 1: Initialize components - {time.time() - start_time:.2f} seconds")

    # Load and validate data
    start_time = time.time()
    try:
        data_processor.validate_image_folder(image_folder)
        products_df = data_processor.load_data(data_file)
        print(f"Loaded {len(products_df)} products")
        print(f"Step 2: Load data - {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Add products to database
    start_time = time.time()
    try:
        db_manager.add_products_to_db(
            products_df=products_df,
            image_folder_path=image_folder,
            batch_size=3500
        )
        print(f"Step 3: Add products to DB - {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"Error adding products to database: {e}")
        return

if __name__ == "__main__":
    main() 