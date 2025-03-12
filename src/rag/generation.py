from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain import PromptTemplate
import torch
import re
from data import clean_text
from src.rag.prompt_template import qna_prompt

def generate_answer(question, embed_model, collection, llm_model, tokenizer):
    # Preprocessing the question
    question_cleaned = clean_text(question)

    # Move embedding model to CPU before encoding
    embed_model_device = embed_model.device
    embed_model.to("cpu")

    torch.cuda.empty_cache()  # Clear cache before embedding
    question_embed = embed_model.encode(question_cleaned)

    # Move embedding model back to its original device
    embed_model.to(embed_model_device)
    torch.cuda.empty_cache()  # Clear cache after embedding

    # Retrieving context from the vector database
    results = collection.query(
        query_embeddings=question_embed.tolist(),
        n_results=5
    )

    context = results["documents"][0][0]

    extended_context = context
    article_number = results["ids"][0][0]
    linked_articles = results['metadatas'][0][0]['linked_articles']  # Corrected access to linked_articles
    linked_articles_content = []
    if linked_articles:  # Check if linked_articles exist
        linked_articles = re.sub(r'[\[\]]', '', linked_articles)
        linked_articles_ids = linked_articles.split(',')  # Split by comma to get individual article IDs
        linked_articles_ids = [id.strip() for id in linked_articles_ids if id.strip()]  # Remove leading/trailing spaces and empty strings
        for link in linked_articles_ids:
            linked_articles_data = collection.get(
                ids=link,  # Use individual digits as IDs
                include=['documents', 'metadatas']
            )
            linked_articles_content.append(linked_articles_data['documents'])
            extended_context += "\n\n" + " ".join(linked_articles_data['documents'])

    # Formatting the prompt
    prompt = qna_prompt.format(context=extended_context, question=question_cleaned)

    # Generating response
    messages = [
        {"role": "system", "content": """أنت مساعد ذكي للإجابة عن أسئلة المستخدمين."""},
        {"role": "user", "content": prompt}
    ]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Apply the chat template and move the tensors to the appropriate device
    input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True).to(device)
    outputs = llm_model.generate(**input_ids, max_new_tokens=256)
    answer = tokenizer.decode(outputs[0])

    # Return the context and answer separately
    return {
        "context": context,
        "answer": answer,
        "extended_context": extended_context,
        "article_number": article_number,
        "linked_articles": linked_articles,
        "linked_articles_content": linked_articles_content
    }