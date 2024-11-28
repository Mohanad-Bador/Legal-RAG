from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from chromadb.api import Collection
from chromadb.config import Settings
from chromadb import Client
from langchain import PromptTemplate
import streamlit as st
import torch
import chromadb

# @st.cache_resource
def load_resources(
    device_map,
    embedding_model_id="intfloat/multilingual-e5-large",
    llm_model_id="silma-ai/SILMA-9B-Instruct-v1.0",
    persist_directory="chromadb-ar-docs6",
    collection_name="laww",
    torch_dtype=torch.bfloat16,
):
    """
    Loads and caches the embedding model, LLM model, tokenizer, and vector database collection.

    Args:
    - embedding_model_id (str): The ID of the embedding model to load.
    - llm_model_id (str): The ID of the LLM model to load.
    - persist_directory (str): Path to the ChromaDB persistent directory.
    - collection_name (str): Name of the vector database collection.
    - device_map (str): Device mapping for the LLM model (e.g., 'auto').
    - torch_dtype (torch.dtype): Data type for the LLM model (e.g., torch.bfloat16).

    Returns:
    - embed_model: Loaded embedding model.
    - llm_model: Loaded LLM model.
    - tokenizer: Tokenizer for the LLM model.
    - collection: ChromaDB collection object.
    """
    # Load embedding model
    embed_model = SentenceTransformer(embedding_model_id)

    # Load LLM model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
    llm_model = AutoModelForCausalLM.from_pretrained(
        llm_model_id,
        device_map=device_map,
        torch_dtype=torch_dtype,
    )

    # Initialize ChromaDB client and collection
    # client = Client(Settings(persist_directory=persist_directory, chroma_db_impl="sqlite"))
    client = chromadb.PersistentClient(path=persist_directory) 
    collection = client.get_or_create_collection(name=persist_directory)

    return embed_model, llm_model, tokenizer, collection





def generate_response(question, llm_model, tokenizer, embed_model, collection, n_results=3):
    """
    Generates a response to a given question by querying a vector database for context and using an LLM model.
    """
    # Define the prompt template
    qna_template = "\n".join([
        "Answer the next question using the provided context.",
        "If the answer is not contained in the context, say 'NO ANSWER IS AVAILABLE'",
        "### Context:",
        "{context}",
        "",
        "### Question:",
        "{question}",
        "",
        "### Answer:",
    ])
    
    qna_prompt = PromptTemplate(
        template=qna_template,
        input_variables=['context', 'question'],
        verbose=True
    )

    try:
        # Encode the question to generate embeddings
        question_embed = embed_model.encode(question)

        # Query the vector database for context
        results = collection.query(
            query_embeddings=question_embed.tolist(),
            n_results=n_results
        )
        if not results["documents"] or not results["documents"][0]:
            return "NO ANSWER IS AVAILABLE"

        # Retrieve the top n_results and join them as the context
        contexts = [doc[0] for doc in results["documents"][:n_results]]  # Extract the first element from each document
        context = "\n\n".join(contexts)  # Join them with double newlines for readability

        # Format the prompt with the retrieved context and the question
        prompt = qna_prompt.format(context=context, question=question)

        # Prepare the messages for LLM generation
        messages = [
            {"role": "system", "content": "أنت مساعد ذكي للإجابة عن أسئلة المستخدمين."},
            {"role": "user", "content": prompt},
        ]

        # Tokenize the input for the LLM
        input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True).to("cuda")

        # Generate the response using the LLM
        outputs = llm_model.generate(**input_ids, max_new_tokens=256)

        # Decode the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return response

    except Exception as e:
        return f"An error occurred while generating the response: {str(e)}"
