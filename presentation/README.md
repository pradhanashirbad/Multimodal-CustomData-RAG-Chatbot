# Electronics Product Chatbot

A chatbot application for searching and querying an electronics product database using natural language and images. This application uses ChromaDB for vector storage, CLIP embeddings for image search, and LangChain with OpenAI for natural language processing.

## Sample Interface

![Sample Interface](sample@SamplePic1.png)

The interface allows users to:
- Upload product images for visual search
- Enter natural language queries
- View similar products with details like price and ratings
- See both text and image search results in an organized table

## Features

- Text-based product search with natural language queries
- Image-based product search
- Multi-modal responses (text + images)
- Gradio web interface

## Project Structure

- `electronics-search/` - Root directory of the project
- `README.md` - This file
- `app.py` - Streamlit UI implementation
- `app_gradio.py` - Gradio UI implementation
- `chroma_text_basic_electronic_add_to_db.py` - Script to populate the vector database
- `chroma_text_basic_electronic_query_llm.py` - Core chatbot functionality
- `utils.py` - Utility functions for database operations
- `requirements.txt` - Required Python packages

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

4. Make sure you have the data files in the correct locations:
   - `electronics_product.csv` - CSV file with product information
   - `images/images_electronics/` - Directory containing product images (named by product_id.jpg)

## Database Setup

Before running the chat application, you need to populate the vector database:

```
python chroma_text_basic_electronic_add_to_db.py
```

This will create two ChromaDB collections:
- `electronics_text_dataset` - Text embeddings of product descriptions
- `electronics_image_dataset` - CLIP embeddings of product images

## Running the Application

### Option 1: Streamlit Interface

```
streamlit run app.py
```

This will start a Streamlit server, typically at http://localhost:8501

### Option 2: Gradio Interface

```
python app_gradio.py
```

This will start a Gradio server at http://localhost:7860

## Usage

1. Type a natural language query about electronics products in the chat interface
   - Example: "What are the best wireless headphones with noise cancellation?"
   - Example: "Show me laptops with good ratings under $1000"

2. Alternatively, upload an image to find similar products

3. View the chatbot's response with relevant product information and images

## Technologies Used

- ChromaDB - Vector database for storing embeddings
- OpenAI CLIP - Image embeddings
- SentenceTransformers - Text embeddings
- LangChain - Framework for LLM application development
- OpenAI GPT - Natural language processing
- Streamlit/Gradio - Web interfaces 