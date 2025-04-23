from transformers import AutoModelForCausalLM, AutoTokenizer
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


class LegalGenerator:
    def __init__(self, base_model_id="Qwen/Qwen2.5-3B-Instruct", finetuned_model_id="/gdrive/MyDrive/GP//llm-finetuning2/qwen-models/Qwen2.5-3B/"):
        self.base_model_id = base_model_id
        self.finetuned_model_id = finetuned_model_id
        self.device = "cuda:0"
        self.torch_dtype = None
        
        # Initialize model and tokenizer
        self.model, self.tokenizer = self._load_model()
        
        # Load the finetuned adapter
        self.model.load_adapter(self.finetuned_model_id)

    def _load_model(self):
        model = AutoModelForCausalLM.from_pretrained(
            self.base_model_id,
            device_map="auto",
            torch_dtype=self.torch_dtype
        )
        tokenizer = AutoTokenizer.from_pretrained(self.base_model_id)
        return model, tokenizer

    def generate_resp(self, messages):
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=1024,
            do_sample=False, top_k=None, temperature=None, top_p=None,
        )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response

    def generate_prompt(self, question, context):
        system_message = "\n".join([
            "أنت تعمل كمستشار قانوني، ومهمتك هي تقديم إجابات قانونية دقيقة بناءً على السؤال والسياق المقدمين.",
            "يجب أن تكون إجابتك واضحة وموجزة، وتستخدم نفس لغة السؤال.",
            "عليك استخراج التفاصيل القانونية من السياق والإشارة إلى رقم المادة القانونية ذات الصلة كما هو مذكور في السياق.",
            "تأكد من أن إجابتك مدعومة بالمرجع القانوني المناسب.",
            "لا تقم بكتابة أي مقدمة أو خاتمة، وركز فقط على الإجابة القانونية."
        ])

        legal_instructions_messages = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": "\n".join([
                    "## السؤال:",
                    "{question}",
                    "",
                    "## السياق:",
                    "{context}",
                    "",
                    "## الإجابة القانونية:"
                ])
            }
        ]

        legal_instructions_messages[1]['content'] = legal_instructions_messages[1]['content'].format(
            question=question,
            context=context
        )

        return legal_instructions_messages

    def generate_response(self, question: str, context: str) -> str:
        legal_instructions_messages = self.generate_prompt(question, context)
        response = self.generate_resp(legal_instructions_messages)
        return response 

## Example usage:
# generator = LegalGenerator() 
# response = generator.(query,context) 