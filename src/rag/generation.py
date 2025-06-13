from transformers import AutoModelForCausalLM, AutoTokenizer
import re

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

    def handle_greetings_and_thanks_arabic(self, question: str) -> str | None:
        greetings = [
            "مرحبا", "مرحباً", "أهلاً","اهلاً","اهلا","أهلا", "السلام عليكم", "السّلام عليكم", "أهلاً وسهلاً", "أهلا وسهلا",
            "صباح الخير", "صَباحُ الخَيْر", "مساء الخير", "مَساءُ الخَيْر", "تحية طيبة", "تحيّة طيّبة", 
            "حيّاك الله", "حيّاكم الله", "سلام عليكم", "سلامٌ عليكم"
        ]

        thanks = [
            "شكرا", "شكرًا", "أشكرك", "أَشكُرُك","شكرا", "جزاك الله خيرا", "جزاكَ اللهُ خيرًا", "جزاكي الله خيرا",
            "جزاكم الله خيرا", "ممتن", "مُمتن", "ممتنة", "مُمتنّة", "شكرًا جزيلاً", "شكرا جزيلا", 
            "كل الشكر", "ألف شكر", "شكرًا لك", "بارك الله فيك", "بارك الله فيكم"
        ]

        stripped_question = question.strip().lower()
        if any(greet in stripped_question for greet in greetings):
            return "مرحبًا بك! كيف يمكنني مساعدتك اليوم؟"
        elif any(thank in stripped_question for thank in thanks):
            return "على الرحب والسعة! لا تتردد في طرح أي سؤال قانوني آخر."
        return None

    def is_arabic(self, text: str, threshold: float = 0.8) -> bool:
        arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
        total_chars = re.findall(r'\S', text)
        if not total_chars:
            return False
        return len(arabic_chars) / len(total_chars) >= threshold

    def generate_prompt(self, question, context):
        system_message = "\n".join([
            "أنت تعمل كمستشار قانوني مصري، ومهمتك هي تقديم إجابات قانونية دقيقة بناءً على السؤال والسياق المقدمين.",
            "تخصصك فقط في المجال القانوني المصري المتعلق بالعمل أو التعليم.",
            "إذا لم يكن السؤال مكتوبًا باللغة العربية الفصحى، لا تُجب عليه إطلاقًا، وقل للمستخدم فقط: 'يرجى إعادة صياغة السؤال باللغة العربية الفصحى حتى أتمكن من مساعدتك.'",
            "لا تجب على أي سؤال عام أو تاريخي أو غير قانوني، حتى لو تم تقديم سياق أو مقالات. يجب أن يكون السؤال قانونيًا وتحديدًا متعلقًا بقوانين العمل أو التعليم المصرية.",
            "إذا لم يكن السؤال متعلقًا بالقانون المصري، قل فقط: 'السؤال خارج نطاق التخصص.'",
            "إذا كان السؤال غير واضح أو غير مكتمل مثل: 'ما' أو 'هل' أو 'لماذا' دون تفاصيل كافية، فاطلب من المستخدم توضيح السؤال بشكل أكثر دقة.",
            "إذا كان السؤال قانونيًا لكنه لا يتطابق مع أي معلومة في السياق، أجب بـ: 'لا توجد إجابة متاحة في السياق المقدم.'",
            "يجب أن تكون إجابتك واضحة وموجزة، وتستخدم نفس لغة السؤال.",
            "استخرج التفاصيل القانونية من السياق وأشر إلى رقم المادة القانونية إن وجد.",
            "تجنب المقدمات أو الخواتيم وركز فقط على الإجابة القانونية.",
            "إذا كان السؤال غير واضح، اطلب من المستخدم توضيح السؤال بشكل أكثر دقة.",
            "استخرج التفاصيل القانونية من السياق وأشر إلى رقم المادة القانونية **الرئيسية** إن وُجدت، وليس رقم البند الفرعي فقط.",
            "إذا كانت الحالة مرتبطة ببند فرعي داخل مادة، اذكر رقم المادة الرئيسية ثم رقم البند داخلها. مثال: 'وفقًا للمادة 69 من قانون العمل المصري، وتحديدًا البند رقم 8...'.",
            "إذا كان المستخدم يرسل تحية فقط مثل: 'السلام عليكم' أو 'مرحبا' أو 'أهلاً'، فقم بالرد بتحية مناسبة مثل: 'وعليكم السلام' أو 'مرحبًا بك'، دون تقديم أي إجابة قانونية."
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
        # Step 1: Greetings / Thanks
        greeting_or_thanks = self.handle_greetings_and_thanks_arabic(question)
        if greeting_or_thanks:
            return greeting_or_thanks

        # Step 2: Arabic language check
        if not self.is_arabic(question):
            return "يرجى إعادة صياغة السؤال باللغة العربية الفصحى حتى أتمكن من مساعدتك."

        # Step 3: Proceed to generate answer via prompt + model
        messages = self.generate_prompt(question, context)
        return self.generate_resp(messages)

## Example usage:
# generator = LegalGenerator() 
# response = generator.generate_response(query,context) 