import pandas as pd
import os

class DataProcessor:
    def __init__(self, raw_data_path):
        self.raw_data_path = raw_data_path

    def load_data(self, file_path):
        """Load and perform initial processing of the data"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
            
        print(f"Loading data from {file_path}")
        products_df = pd.read_csv(file_path)
        products_df = products_df.rename(columns={products_df.columns[0]: 'product_id'})
        
        # Basic data validation
        required_columns = ['product_id', 'name', 'sub_category', 'ratings', 
                          'no_of_ratings', 'discount_price', 'actual_price']
        missing_columns = [col for col in required_columns if col not in products_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        return products_df

    def validate_image_folder(self, image_folder_path):
        """Validate that the image folder exists and is accessible"""
        if not os.path.exists(image_folder_path):
            raise FileNotFoundError(f"Image folder {image_folder_path} not found")
        if not os.path.isdir(image_folder_path):
            raise NotADirectoryError(f"{image_folder_path} is not a directory")

    def create_product_document(self, product, image_folder_path):
        product_id = str(product.get('product_id', ''))
        name = product.get('name', '')
        sub_category = product.get('sub_category', '')
        ratings = str(product.get('ratings', ''))
        no_of_ratings = str(product.get('no_of_ratings', ''))
        discount_price = str(product.get('discount_price', ''))
        actual_price = str(product.get('actual_price', ''))

        image_uris = os.listdir(image_folder_path)
        image_file_name = f"{product_id}.jpg"
        
        if image_file_name not in image_uris:
            return None, None, None, None

        product_text = f"""
        Product: {name}
        Category: {sub_category}
        Rating: {ratings} ({no_of_ratings} ratings)
        Price: ${discount_price} (Original: ${actual_price})
        """
        
        image_uri = os.path.join(image_folder_path, image_file_name)
        metadata = {
            "product_id": product_id,
            "name": name,
            "sub_category": sub_category,
            "ratings": ratings,
            "discount_price": discount_price,
            "uri": image_uri
        }    
        return product_text, metadata, product_id, image_uri 