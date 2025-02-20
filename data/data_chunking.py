from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

def chunk_text(documents, chunk_size=300, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunked_documents = []
    for doc in documents:
        size = len(doc)
        if size > chunk_size:
            chunks = text_splitter.split_text(doc)
            chunked_documents.extend(chunks)
        else:
            chunked_documents.append(doc)
    return chunked_documents

def chunk_and_save_to_json(Raw_data_csv, clean_text, chunk_size=300, chunk_overlap=100, output_file="chunks_with_metadata.json"):
    chunked_json = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    for article in Raw_data_csv:
        # Extract the article details and metadata
        article_details = clean_text(article['article_details'])
        article_metadata = {
            'article_number': int(article['article_number']),
            'book': str(article['book']),
            'chapter': str(article['chapter']),
            'section': str(article['section']),
            'linked_definitions': str(article['linked_definitions']),
            'linked_articles': article['linked_articles']
        }
        # Apply chunking to article_details
        size = len(article_details)
        if size > chunk_size:
            chunks = text_splitter.split_text(article_details)
        else:
            chunks = [article_details]

        # Generate metadata for each chunk and store it
        for i, chunk in enumerate(chunks):
            chunk_metadata = article_metadata.copy()
            chunk_metadata['chunk_index'] = f"{article_metadata['article_number']}_chunk_{i}"  # Add chunk index for traceability
            chunk_metadata['full_chunk'] = article['article_details']  # Add full article text
            chunked_json.append({
                "chunk": chunk,
                "metadata": chunk_metadata
            })

    # Write the chunks and metadata to a JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(chunked_json, json_file, indent=4, ensure_ascii=False)

    print(f"JSON file '{output_file}' has been created.")

def load_chunks_from_json(input_file="chunks_with_metadata.json"):
    # Read the JSON file
    with open(input_file, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # Create two lists: one for chunks and another for metadata
    chunked_documents = [entry["chunk"] for entry in data]
    chunked_metadata = [entry["metadata"] for entry in data]
    chunked_ids = [
        f"{entry['metadata']['article_number']}_chunk_{entry['metadata']['chunk_index']}"
        for entry in data
    ]

    # Print the lists to verify
    print("Chunks List:", chunked_documents[0])
    print("Metadata List:", chunked_metadata[0])
    print("chunk_ids List:", chunked_ids[0])

    return chunked_documents, chunked_metadata, chunked_ids