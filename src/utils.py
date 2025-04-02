import os
import logging

def setup_logging():
    """Configure logging settings"""
    logging.basicConfig(level=logging.ERROR)

def create_product_document(product, image_folder_path):
    """
    Create a document from product metadata.
    
    Args:
        product: Dictionary or Series containing product information
        image_folder_path: Path to the folder containing product images
        
    Returns:
        Tuple of (product_text, metadata, product_id, image_uri)
    """
    # Extract product fields
    product_id = str(product.get('product_id', ''))
    name = product.get('name', '')
    sub_category = product.get('sub_category', '')
    ratings = str(product.get('ratings', ''))
    no_of_ratings = str(product.get('no_of_ratings', ''))
    discount_price = str(product.get('discount_price', ''))
    actual_price = str(product.get('actual_price', ''))
    
    # Check if image exists
    image_uris = os.listdir(image_folder_path)
    image_file_name = f"{product_id}.jpg"
    if not image_file_name in image_uris:
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