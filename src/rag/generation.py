from transformers import AutoModelForCausalLM, AutoTokenizer

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
# response = generator.generate_response(query,context) 