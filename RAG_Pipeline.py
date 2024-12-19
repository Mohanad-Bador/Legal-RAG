from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from langchain import PromptTemplate
import chromadb
import torch


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
    Generates a response to a user query by retrieving relevant context from a vector database 
    and utilizing a language model to generate an answer.

    Args:
    - question (str): The user query for which a response is required.
    - llm_model: The loaded large language model used for generating responses.
    - tokenizer: The tokenizer corresponding to the LLM model.
    - embed_model: The embedding model used to encode the question into vector representation.
    - collection: The vector database collection used to retrieve relevant documents.
    - n_results (int, optional): Number of top matching documents to retrieve from the database. Default is 3.

    Returns:
    - str: The generated response from the language model. If no relevant context is found, 
           returns "NO ANSWER IS AVAILABLE". In case of an error, returns an error message.
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
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    collection = chroma_client.get_collection(name=collection_name)

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
