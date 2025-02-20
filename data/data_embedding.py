from sentence_transformers import SentenceTransformer

def embed_documents(documents, model_id='intfloat/multilingual-e5-large'):
    model = SentenceTransformer(model_id)
    dim = 512
    device = "auto"
    embeddings = model.encode(documents, show_progress_bar=True)
    return embeddings