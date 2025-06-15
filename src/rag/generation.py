from transformers import AutoModelForCausalLM, AutoTokenizer
import re

OUT_OF_SCOPE_LAWS = [
    "الدستور المصري",
    "قانون العقوبات",
    "قانون الإجراءات الجنائية",
    "القانون المدني",
    "قانون الإجراءات المدنية والتجارية",
    "قانون المرافعات",
    "قانون التجارة",
    "قانون الشركات",
    "قانون التأمينات الاجتماعية والمعاشات",
    "قانون الطفل",
    "قانون الأحوال الشخصية",
    "قانون الإثبات",
    "قانون المرافعات الإدارية",
    "قانون مجلس الدولة",
    "قانون القضاء العسكري",
    "قانون مكافحة الإرهاب",
    "قانون مكافحة غسل الأموال",
    "قانون تنظيم الإعلام والصحافة",
    "قانون حماية المستهلك",
    "قانون حماية المنافسة ومنع الممارسات الاحتكارية",
    "قانون حماية البيانات الشخصية",
    "قانون تنظيم الجامعات",
    "قانون البيئة",
    "قانون المرور",
    "قانون البناء الموحد",
    "قانون تنظيم السجون",
    "قانون الأحزاب السياسية",
    "قانون الطوارئ",
    "قانون تنظيم الجمعيات الأهلية",
    "قانون الضريبة على الدخل",
    "قانون الضريبة على القيمة المضافة"
]
OUT_OF_CONTEXT_RESPONSES = [
    "يرجى توضيح السؤال",
    "وفقًا للسياق المقدم، لا يوجد",
    "لا يوجد نص قانوني مباشر",
    "السؤال خارج نطاق التخصص",
    "لا يوجد أي علاقة بين المواد المقدمة"
]
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

    def is_question_possibly_meaningful(self, question: str) -> bool:
        words = question.strip().split()
        # reject empty or one-word questions
        if len(words) < 3:
            return False

        # reject if all words are interrogative or filler
        filler_words = ["هل", "ما", "لماذا", "متى", "أين", "آه", "اه", "يعني", "هو", "هي", "؟", "?"]
        filler_count = sum(1 for w in words if w in filler_words)
        if filler_count >= len(words) - 1:
            return False

        return True

    def generate_prompt(self, question, context):
        system_message = "\n".join([
            "اتبع الخطوات التالية بدقة عند الإجابة على أي سؤال:",
            "1. اقرأ السؤال أولاً وحدد إذا كان متعلقًا فقط بقانون العمل المصري أو قانون التعليم المصري.",
            "2. إذا لم يكن السؤال متعلقًا بقانون العمل أو التعليم، تجاهل السياق تمامًا ولا تستخدمه في الإجابة، ورد فقط بـ: 'السؤال خارج نطاق التخصص' دون أي شرح إضافي.",
            "3. إذا كان السؤال مكتوبًا بغير اللغة العربية الفصحى، لا تُجب عليه وقل فقط: 'يرجى إعادة صياغة السؤال باللغة العربية الفصحى حتى أتمكن من مساعدتك.'",
            "4. إذا كان السؤال غير واضح أو غير مكتمل أو عام جدًا — مثل الأسئلة من نوع: 'ما'، 'هل'، أو 'لماذا' — دون تفاصيل كافية أو سياق قانوني دقيق، لا تُجب عليه وقل فقط: 'يرجى توضيح السؤال بشكل أكثر دقة حتى أتمكن من مساعدتك.'",
            "5. إذا كان المستخدم يرسل تحية فقط مثل: 'السلام عليكم' أو 'مرحبا' أو 'أهلاً'، فقم بالرد بتحية مناسبة مثل: 'وعليكم السلام' أو 'مرحبًا بك'، دون تقديم أي إجابة قانونية.",
            "6. إذا كان السؤال قانونيًا ويتعلق بقانون العمل أو التعليم، استخدم السياق المقدم للإجابة فقط إذا كان يحتوي على معلومة قانونية مرتبطة بالسؤال.",
            "7. إذا لم تجد في السياق إجابة مناسبة، أو إذا كان السياق المسترجع غير مرتبط بالسؤال، أجب فقط بـ: 'لا توجد إجابة متاحة في السياق المقدم.' دون أي شرح إضافي.",
            "8. إذا وجدت الإجابة في السياق، يجب أن تبدأ إجابتك بصيغة: 'وفقًا للمادة ... من قانون العمل المصري' أو 'وفقًا للمادة ... من قانون التعليم المصري' مع ذكر رقم المادة المناسبة فقط، ولا تذكر أو تستخدم أي قانون آخر في الإجابة.",
            "9. إذا كانت الحالة مرتبطة ببند فرعي داخل مادة، اذكر رقم المادة الرئيسية ثم رقم البند داخلها. مثال: 'وفقًا للمادة 69 من قانون العمل المصري، وتحديدًا البند رقم 8...'.",
            "10. يجب أن تكون جميع الإجابات باللغة العربية الفصحى فقط، وتكون واضحة وموجزة، وتجنب المقدمات أو الخواتيم، ويُسمح باستخدام الأرقام (مثل أرقام المواد القانونية أو التواريخ) عند الحاجة.",
            "11. استخرج التفاصيل القانونية من السياق وأشر إلى رقم المادة القانونية *الرئيسية* إن وُجدت، وليس رقم البند الفرعي فقط.",
            "12. لا تجب على أي سؤال عام أو تاريخي أو غير قانوني، حتى لو تم تقديم سياق أو مقالات. يجب أن يكون السؤال قانونيًا وتحديدًا متعلقًا بقوانين العمل أو التعليم المصرية.",
            "13. التزم بهذه الخطوات بدقة ولا تتجاوزها."
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
        if not self.is_arabic(question):
            context.clear()
            return "يرجى إعادة صياغة السؤال باللغة العربية الفصحى حتى أتمكن من مساعدتك."
            
        greeting_or_thanks = self.handle_greetings_and_thanks_arabic(question)
        if greeting_or_thanks:
            context.clear()
            return greeting_or_thanks

        if not self.is_question_possibly_meaningful(question):
            context.clear()
            return "يرجى توضيح السؤال بشكل أكثر دقة حتى أتمكن من مساعدتك."

        # Check for out-of-scope laws
        for law in OUT_OF_SCOPE_LAWS:
            if law in question:
                context.clear()
                return "السؤال خارج نطاق التخصص"

        # Step 3: Proceed to generate answer via prompt + model
        messages = self.generate_prompt(question, context)
        response = self.generate_resp(messages)

        # Clear context if response contains specific phrases
        for phrase in OUT_OF_CONTEXT_RESPONSES:
            if phrase in response:
                context.clear()
                break

        return response

## Example usage:
# generator = LegalGenerator() 
# response = generator.generate_response(query,context) 