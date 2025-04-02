import os
import csv
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import shutil

# Constants
DATA_CSV = 'data/raw/electronics_product.csv'
IMAGE_FOLDER = 'data/images/images_electronics'
NUM_IMAGES = 10000

def setup_directories():
    if os.path.exists(IMAGE_FOLDER):
        shutil.rmtree(IMAGE_FOLDER)
    os.makedirs(IMAGE_FOLDER, exist_ok=True)

def download_images(df):
    for index, row in df.iterrows():
        id = row.iloc[0]
        image_url = row['image']

        try:
            response = requests.get(image_url, timeout=5)
            if response.status_code == 200:
                image_path = os.path.join(IMAGE_FOLDER, f"{id}.jpg")
                with open(image_path, 'wb') as img_file:
                    img_file.write(response.content)
        except Exception as e:
            print(f"Failed to download {image_url}: {e}")

def main():
    setup_directories()
    df = pd.read_csv(DATA_CSV, sep=',')
    download_images(df)

if __name__ == "__main__":
    main() 