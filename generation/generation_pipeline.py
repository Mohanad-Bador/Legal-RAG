from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain import PromptTemplate
import torch
import re

def generate_answer(question, embed_model, collection, llm_model, tokenizer):
    # Creating the prompt template
    qna_template = """
    أجب عن السؤال التالي باللغة العربية فقط باستخدام السياق المقدم.
    إذا لم تكن الإجابة موجودة في السياق، قل 'لا توجد إجابة متاحة'.
    قم بتقديم شرح مفصل وشامل، موضحًا السياق ومضمّنًا أي تفاصيل قانونية أو إجرائية ذات صلة إذا لزم الأمر.

    ### أمثلة:
    ### السؤال:
    ما معني العلاوة الدورية ؟
    ### الإجابة:
    العلاوة الدورية هي مبلغ نقدي ثابت يضاف الي أجر العامل في موعد دوري غالباً ما يكون أول يناير من كل عام ، ويتكرر صرفها بمرور سنة على صرف أخر علاوة ، وتحتسب أول علاوة بعد مرور عام على استلام العامل للعمل . وقد قرر المشرع في قانون العمل مبدأ عام ، حيث جعل العلاوة الدورية السنوية جزءاً من الأجر وتأخذ حكمه ( المادة رقم 1 فقرة ج بند 3 ) . وبهذا المعنى تعتبر العلاوة الدورية السنـوية زيادة سنـوية تعطى للعـامل زيـادة على أجره الأصلي ( أجر الالتحاق بالعمل ) . والعلاوة الدورية السنوية ، منشأها إرادة المشرع ، فهي مقررة بمقتضى حكم المادة الثانية من مواد إصدار قانون العمل الصادر بالقانون رقم 12 لسنه 2003 ، وهى لا تقل عن 7 % من الأجر الأساسي الذي تحسب على أساسه اشتراكات التأمينات الاجتماعية ( دون حد أدنى أو أقصى ) على خلاف ما كان مقرراً في قانون العمل السابق بمقتضى نص المادة 42 حين جعل المشرع حدها الأدنى جنيهان وحدها الأقصى سبعة جنيهات . ويلتزم أصحاب الأعمال – أيا كان عدد عمالهم – بصرف العلاوة الدورية السنوية في تاريخ استحقاقها ، وبنسبتها المقررة حسب التفصيل السابق و صدر الحكم التالي الذي جاء فيه للتاكيد علي ماسبق " وأن قرار رئيس مجلس الإدارة لا يعدو أن يكون قراراً كاشفاً وصدوره في تاريخ متأخر عن ميعاد استحقاق العلاوة لا يهدر حق العاملين في استحقاقها بأثر رجعى من تاريخ مرور سنه ( من تاريخ استلام العامل للعمل أو مرور سنة على صرف أخر علاوة ) " . و كذلك الحكم " هذا ومن المستقر عليه فقها وقضاء أن استمرار صاحب العمل بصفة دورية ومنظمة في منح علاوات دورية بمقدار ثابت يولد لديهم اعتقاداً بالتزام صاحب العمل بالاستمرار في منحها لهم وبحقهم في اقتضائها كما لا يصح له تعليق صرف هذه العلاوة في أحدى السنوات على موافقة مجلس الإدارة ( نقض مدني 139 لسنه 37 ق 28/3/1982 ) .'
    ### السؤال:
    ما هو الميعاد الخاص ببطلان أي مخالصة عن حق من حقوق العامل؟
    ### الإجابة:
    يقع باطلاً كل شرط أو اتفاق يخالف أحكام هذا القانون ولو كان سابقاً علي العمل به ، إذا كان يتضمن انتقاصاً من حقوق العامل المقررة فيه. ويستمر العمل بأية مزايا أو شروط تكون مقررة أو تقرر في عقود العمل الفردية أو الجماعية أو الأنظمة الأساسية أو غيرها من لوائح المنشأة ، أو بمقتضى العرف . وتقع باطلة كل مصالحة تتضمن انتقاصاً أو إبراء من حقوق العامل الناشئة عن عقد العمل خلال مدة سريانه أو خلال ثلاثة أشهر من تاريخ انتهائه متي كانت تخالف أحكام هذا القانون
    ### السؤال:
     ما هي حقوق العامل في حالة الفصل التعسفي؟
    ### الإجابة:
    وفقًا للمادة 122 في قانون العمل رقم 12 لسنة 2003
    للعامل الحق في المطالبة بتعويض عن الفصل التعسفي.
    يتم تحديد التعويض بناءً على الأجر وظروف الفصل.
    ### السياق:
    {context}

    ### السؤال:
    {question}

    ### الإجابة:

    """

    qna_prompt = PromptTemplate(
        template=qna_template,
        input_variables=['context', 'question'],
        verbose=True
    )

    # Preprocessing the question
    question_cleaned = clean_text(question)

    # Move embedding model to CPU before encoding
    embed_model_device = embed_model.device
    embed_model.to("cpu")

    torch.cuda.empty_cache() # Clear cache before embedding
    question_embed = embed_model.encode(question_cleaned)

    # Move embedding model back to its original device
    embed_model.to(embed_model_device)
    torch.cuda.empty_cache() # Clear cache after embedding

    # Retrieving context from the vector database
    results = collection.query(
        query_embeddings=question_embed.tolist(),
        n_results=5
    )

    context = results["documents"][0][0]

    extended_context = context
    article_number = results["ids"][0][0]
    linked_articles = results['metadatas'][0][0]['linked_articles'] # Corrected access to linked_articles
    linked_articles_content = []
    if linked_articles:  # Check if linked_articles exist
        linked_articles = re.sub(r'[\[\]]', '', linked_articles)
        linked_articles_ids = linked_articles.split(',')  # Split by comma to get individual article IDs
        linked_articles_ids = [id.strip() for id in linked_articles_ids if id.strip()]  # Remove leading/trailing spaces and empty strings
        for link in linked_articles_ids:
            linked_articles_data = collection.get(
                ids=link, # Use individual digits as IDs
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