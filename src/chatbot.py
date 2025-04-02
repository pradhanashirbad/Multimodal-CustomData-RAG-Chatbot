import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate


load_dotenv()

class ELectronicsChatbot:
    def __init__(self, text_collection, image_collection):
        self.text_collection = text_collection
        self.image_collection = image_collection
        self.qa_chain = self.setup_qa_chain()

    def query(self, question):
        # Query text collection
        text_content, text_metadatas, text_uris = self.query_db_uris(question, db_type="text")
        
        # Query image collection
        image_uris, image_metadatas, image_uris = self.query_db_uris(question, db_type="image")
        
        # Format inputs for the prompt
        inputs = self.format_prompt_inputs(question, texts=text_content, images=image_uris, 
                                         text_metadatas=text_metadatas, image_metadatas=image_metadatas)
        
        # Get response from QA chain
        answer = self.qa_chain.invoke(inputs)
        
        return {
            "answer": answer,
            "text_content": text_content,
            "text_metadatas": text_metadatas,
            "text_uris": text_uris,
            "image_uris": image_uris,
            "image_metadatas": image_metadatas
        }
    
    def query_image(self, image_npy):
        # Query image collection
        image_uris, image_metadatas, image_uris = self.query_image_db_uris(image_npy)
        
        # Format inputs for the prompt
        inputs = self.format_prompt_inputs(image_npy, images=image_uris, image_metadatas=image_metadatas)
        
        # Get response from QA chain
        answer = self.qa_chain.invoke(inputs)
        
        return {
            "answer": answer,
            "text_content": ['No text content found'],
            "text_metadatas": ['No text metadata found'],
            "text_uris": ['No text uri found'],
            "image_uris": image_uris,
            "image_metadatas": image_metadatas
        }

    def query_db_uris(self, query_text, db_type="text", max_results=5):
        if not isinstance(query_text, list):
            query_text = [query_text]
        collection = self.text_collection if db_type == "text" else self.image_collection
        results = collection.query(
            query_texts=query_text, 
            include=['data', 'documents', 'distances', 'metadatas', 'uris'], 
            n_results=max_results
        )
        filtered_content = []
        text_uris = []
        if db_type == "text":
            for content in enumerate(results['documents'][0]):
                filtered_content.append(content)
            for metadata in results['metadatas'][0]:
                text_uris.append(metadata['uri'])
            return filtered_content, results['metadatas'][0], text_uris
        elif db_type == "image":
            for uri in results['uris'][0]:
                filtered_content.append(uri)
            return filtered_content, results['metadatas'][0], results['uris'][0]
        else:
            return None, None, None

    def query_image_db_uris(self, query_image, max_results=5):
        """
        Query the image collection using an image.
        
        Args:
            query_image: numpy array of the image
            max_results: maximum number of results to return
            
        Returns:
            Tuple of (filtered_content, metadatas, uris)
        """
        if not isinstance(query_image, list):
            query_image = [query_image]

        collection = self.image_collection
        results = collection.query(
            query_images=query_image, 
            include=['data', 'documents', 'distances', 'metadatas', 'uris'], 
            n_results=max_results
        )
        filtered_content = []
        for uri in results['uris'][0]:
            filtered_content.append(uri)
        return filtered_content, results['metadatas'][0], results['uris'][0]

    def format_prompt_inputs(self, user_query, texts=None, images=None, text_metadatas=None, image_metadatas=None):
        """
        Format inputs for the QA prompt.
        
        Args:
            user_query: User's query text or image
            texts: List of text documents
            images: List of image URIs
            text_metadatas: List of text metadata
            image_metadatas: List of image metadata
            
        Returns:
            dict: Formatted inputs for prompt
        """
        inputs = {}
        
        # Save the user query
        inputs['query'] = user_query
        inputs['texts'] = texts
        inputs['text_metadatas'] = text_metadatas
        
        # Encode the images
        if images and len(images) >= 2:
            with open(images[0], 'rb') as image_file:
                image_data_1 = image_file.read()
            inputs['image_data_1'] = base64.b64encode(image_data_1).decode('utf-8')

            with open(images[1], 'rb') as image_file:
                image_data_2 = image_file.read()
            inputs['image_data_2'] = base64.b64encode(image_data_2).decode('utf-8')

            if image_metadatas and len(image_metadatas) >= 2:
                inputs['image1_metadatas'] = image_metadatas[0]
                inputs['image2_metadatas'] = image_metadatas[1]
            else:
                inputs['image1_metadatas'] = {}
                inputs['image2_metadatas'] = {}
        else:
            # Provide empty data if images are not available
            inputs['image_data_1'] = ""
            inputs['image_data_2'] = ""
            inputs['image1_metadatas'] = {}
            inputs['image2_metadatas'] = {}
        
        return inputs

    def setup_qa_chain(self):
        template = """
        You are a helpful shopping assistant. Use the following product information to answer the question, while answering the question use metadata to supplement your answer. Provide one main answer and one alternative answers
        If the query includes anything about the appearance (color size shape etc), then any other information such as rating, discount and price description becomes secondary. Prioritize the image query results, use image metadata to answer the question, and use secondary query on the image metadatas. If the anwser is not in the image, say that you are sorry, you cant find from the image and provide answers from the text query instead.
        If the query is about the product/brand name,rating and discount, prioritize the text query results. Remeber the query results are sorted by relevance using cosine similarity (first in list is most relevant).
        Give the answer in statements, not bullet points. make sure to include the product_id in the answer.
        Question: {query}
        
        Answer:
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("user", 
             [
                {
                    "type": "text",
                    "text": "{texts}"
                },
                {
                    "type": "image_url",
                    "image_url": {'url': "data:image/jpeg;base64,{image_data_1}"}
                },
                {
                    "type": "image_url",
                    "image_url": {'url': "data:image/jpeg;base64,{image_data_2}"}
                },
                {
                    "type": "text",
                    "text": "Text Metadata: {text_metadatas}"
                },
                {
                    "type": "text",
                    "text": "Image 1 Metadata: {image1_metadatas}"
                },
                {
                    "type": "text",
                    "text": "Image 2 Metadata: {image2_metadatas}"
                }
             ]
             ),
        ])
        
        llm = ChatOpenAI(temperature=0.3, model="gpt-4o")
        parser = StrOutputParser()
        return prompt | llm | parser 