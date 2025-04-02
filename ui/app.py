import gradio as gr
import pandas as pd
import os
from PIL import Image
from dotenv import load_dotenv
import numpy as np
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv()

# Now the imports should work
from src.chatbot import ELectronicsChatbot
from src.db_manager import DatabaseManager
from ui.components import create_image_sources, create_text_sources, create_results_table

def initialize_chatbot():
    """Initialize the chatbot with database connections"""
    db_manager = DatabaseManager()
    return ELectronicsChatbot(db_manager.text_collection, db_manager.image_collection)

def process_query(message, history, image=None):
    """Process the user query and return the chatbot response"""
    chatbot_instance = initialize_chatbot()
    
    if image is not None:
        os.makedirs("data/images/user_uploads", exist_ok=True)
        image_path = os.path.join("data/images/user_uploads", "user_uploaded.jpg")
        image.save(image_path)
        if not message:
            message = "Find products similar to this image"
    
    response = chatbot_instance.query(message)
    answer_text = response["answer"]
    
    # Get image URIs and metadata
    image_uris = response.get("image_uris", [])[:5]
    image_metadatas = response.get("image_metadatas", [])[:5]
    text_uris = response.get("text_uris", [])[:5]
    text_content = response.get("text_content", [])[:5]
    text_metadatas = response.get("text_metadatas", [])[:5]

    # Process images and prepare outputs
    product_images, captions = process_images(image_uris, image_metadatas)
    text_product_images, text_captions = process_images(text_uris, text_metadatas, size=(200, 200))
    
    # Create results table
    results_df = create_results_dataframe(text_metadatas, image_metadatas)
    
    # Update chat history
    history.append((message, answer_text))
    
    return prepare_outputs(history, text_product_images, text_captions, 
                         product_images, captions, results_df)

def process_image_search(image, history):
    """Process image search request"""
    if image is None:
        return create_empty_outputs()
    
    chatbot_instance = initialize_chatbot()
    image_npy = np.array(image)
    response = chatbot_instance.query_image(image_npy)
    answer_text = response["answer"]
    
    image_uris = response.get("image_uris", [])[:5]
    image_metadatas = response.get("image_metadatas", [])[:5]
    
    product_images, captions = process_images(image_uris, image_metadatas)
    results_df = create_results_dataframe([], image_metadatas)
    
    history.append(("Find products similar to this image", answer_text))
    
    return prepare_outputs(history, 
                         [None]*5, [""]*5,  # Empty text outputs
                         product_images, captions, results_df)

def process_images(uris, metadatas, size=(300, 300)):
    """Process images and create captions"""
    images = []
    captions = []
    for uri, metadata in zip(uris, metadatas):
        try:
            img = Image.open(uri)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            new_img = Image.new('RGB', size, (255, 255, 255))
            offset = ((size[0] - img.size[0]) // 2,
                     (size[1] - img.size[1]) // 2)
            new_img.paste(img, offset)
            
            images.append(new_img)
            
            product_id = metadata.get('product_id', os.path.basename(uri).split('.')[0])
            name = metadata.get('name', 'N/A')
            price = metadata.get('discount_price', 'N/A')
            rating = metadata.get('ratings', 'N/A')
            captions.append(f"ID: {product_id}\nName: {name}\nPrice: ${price}\nRating: {rating}")
        except Exception as e:
            print(f"Could not load image {uri}: {e}")
            images.append(None)
            captions.append("Image not available")
    
    while len(images) < 5:
        images.append(None)
        captions.append("")
    
    return images, captions

def create_results_dataframe(text_metadatas, image_metadatas):
    """Create a DataFrame for the results table"""
    table_data = []
    
    for metadata in text_metadatas:
        table_data.append({
            'Source': 'Text',
            'Product ID': metadata.get('product_id', 'N/A'),
            'Name': metadata.get('name', 'N/A'),
            'Rating': metadata.get('ratings', 'N/A'),
            'Price': metadata.get('discount_price', 'N/A')
        })
    
    for metadata in image_metadatas:
        table_data.append({
            'Source': 'Image',
            'Product ID': metadata.get('product_id', 'N/A'),
            'Name': metadata.get('name', 'N/A'),
            'Rating': metadata.get('ratings', 'N/A'),
            'Price': metadata.get('discount_price', 'N/A')
        })
    
    return pd.DataFrame(table_data)

def create_empty_outputs():
    """Create empty outputs for clearing or error states"""
    return [[], 
            None, None, None, None, None,
            "", "", "", "", "",
            None, None, None, None, None,
            "", "", "", "", "",
            None]

def prepare_outputs(history, text_images, text_captions, 
                   product_images, product_captions, results_df):
    """Prepare all outputs in the correct order"""
    return [history, 
            text_images[0], text_images[1], text_images[2], text_images[3], text_images[4],
            text_captions[0], text_captions[1], text_captions[2], text_captions[3], text_captions[4],
            product_images[0], product_images[1], product_images[2], product_images[3], product_images[4],
            product_captions[0], product_captions[1], product_captions[2], product_captions[3], product_captions[4],
            results_df]

def create_gradio_app(chatbot_instance):
    """Create the Gradio interface with a pre-initialized chatbot"""
    with gr.Blocks(css="""
        .image-container img {
            width: 200px !important;
            height: 200px !important;
            object-fit: contain !important;
        }
        .source-images {
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }
        .source-caption {
            margin-top: 10px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .results-table {
            margin: 20px 0;
        }
        footer {display: none}
    """) as demo:
        gr.Markdown("# 🛍️ Electronics Product Assistant")
        gr.Markdown("Ask questions about electronics products or upload an image to find similar items")
        
        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.Image(type="pil", label="Upload Image (Optional)")
                with gr.Row():
                    send_image = gr.Button("🔍 Search Similar", size="lg", variant="primary")
            
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Chat History",
                    type="tuples",
                    height=400
                )
                with gr.Row():
                    msg = gr.Textbox(
                        label="Type your message",
                        placeholder="Ask about electronics products...",
                        scale=8
                    )
                    clear = gr.Button("Clear", size="lg", scale=1)
        
        gr.Markdown("### Search Results")
        results_table = create_results_table()
        
        gr.Markdown("### Image Sources")
        image_sources = create_image_sources()
        
        gr.Markdown("### Text Sources")
        text_sources = create_text_sources()
        
        # Extract components for event handling
        image_outputs = [img for img, _ in image_sources]
        image_captions = [caption for _, caption in image_sources]
        text_outputs = [img for img, _ in text_sources]
        text_captions = [caption for _, caption in text_sources]
        
        # Update event handlers to use the passed chatbot_instance
        def process_query_with_chatbot(message, history, image=None):
            if image is not None:
                os.makedirs("data/images/user_uploads", exist_ok=True)
                image_path = os.path.join("data/images/user_uploads", "user_uploaded.jpg")
                image.save(image_path)
                if not message:
                    message = "Find products similar to this image"
            
            response = chatbot_instance.query(message)
            answer_text = response["answer"]
            
            # Rest of the processing remains the same
            image_uris = response.get("image_uris", [])[:5]
            image_metadatas = response.get("image_metadatas", [])[:5]
            text_uris = response.get("text_uris", [])[:5]
            text_content = response.get("text_content", [])[:5]
            text_metadatas = response.get("text_metadatas", [])[:5]

            product_images, captions = process_images(image_uris, image_metadatas)
            text_product_images, text_captions = process_images(text_uris, text_metadatas, size=(200, 200))
            
            results_df = create_results_dataframe(text_metadatas, image_metadatas)
            
            history.append((message, answer_text))
            
            return prepare_outputs(history, text_product_images, text_captions, 
                                product_images, captions, results_df)

        def process_image_search_with_chatbot(image, history):
            if image is None:
                return create_empty_outputs()
            
            image_npy = np.array(image)
            response = chatbot_instance.query_image(image_npy)
            answer_text = response["answer"]
            
            image_uris = response.get("image_uris", [])[:5]
            image_metadatas = response.get("image_metadatas", [])[:5]
            
            product_images, captions = process_images(image_uris, image_metadatas)
            results_df = create_results_dataframe([], image_metadatas)
            
            history.append(("Find products similar to this image", answer_text))
            
            return prepare_outputs(history, 
                                [None]*5, [""]*5,
                                product_images, captions, results_df)

        # Update event handlers to use the new functions
        msg.submit(
            process_query_with_chatbot,
            inputs=[msg, chatbot, image_input],
            outputs=[chatbot] + text_outputs + text_captions + image_outputs + image_captions + [results_table]
        )
        
        clear.click(
            lambda: create_empty_outputs(),
            outputs=[chatbot] + text_outputs + text_captions + image_outputs + image_captions + [results_table]
        )
        
        send_image.click(
            process_image_search_with_chatbot,
            inputs=[image_input, chatbot],
            outputs=[chatbot] + text_outputs + text_captions + image_outputs + image_captions + [results_table]
        )
        
        # Example queries
        gr.Examples(
            examples=[
                ["What are the best wireless headphones?"],
                ["Find me a good laptop under $1000"],
                ["What's the highest rated smartphone?"],
            ],
            inputs=msg
        )
        
        gr.Markdown("## How to use")
        gr.Markdown("""
        - Type your question about electronics products in the chat
        - Optionally upload an image to find similar products
        - The assistant will provide answers with relevant sources below
        """)
    
    return demo

def main():
    """Main function to run the application"""
    try:
        print("Initializing chatbot and databases...")
        chatbot_instance = initialize_chatbot()
        
        print("Creating Gradio interface...")
        demo = create_gradio_app(chatbot_instance)
        
        print("Starting server...")
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=True,
            debug=True
        )
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure all required packages are installed")
        print("2. Check if port 7860 is available")
        print("3. Verify that the database files exist in database_chroma/")
        print("4. Check your .env file contains a valid OPENAI_API_KEY")

if __name__ == "__main__":
    main() 