import pandas as pd
import json
import pickle
import numpy as np
import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from joblib import Parallel, delayed
from math import ceil
import time

### CONFIGURATION ###
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"  # ~500MB model
TOP_K = 5  # number of top results for section and subsection

### STEP 1: CSV to JSON Chunk Aggregation ###
def build_chunks_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    
    # Ensure these columns exist
    assert {'text', 'label', 'page', 'source_pdf'}.issubset(df.columns), "Missing required columns"

    chunks = []
    current_chunk = ""
    current_label = None
    current_page = None
    current_doc = None
    current_section = None

    for idx, row in df.iterrows():
        label = row['label']
        text = str(row['text']).strip()
        page = row['page']
        doc = row['source_pdf']

        # Save the previous chunk before updating section title
        if label in ['title', 'H1', 'H2']:
            if current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'label': current_label,
                    'page': current_page,
                    'document': current_doc,
                    'section_title': current_section
                })
                current_chunk = ""
                current_label = None
                current_page = None
                current_doc = None
            current_section = text

        if label == current_label and doc == current_doc and page == current_page:
            current_chunk += " " + text
        else:
            if current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'label': current_label,
                    'page': current_page,
                    'document': current_doc,
                    'section_title': current_section
                })
            current_chunk = text
            current_label = label
            current_page = page
            current_doc = doc

    # append last chunk
    if current_chunk:
        chunks.append({
            'text': current_chunk.strip(),
            'label': current_label,
            'page': current_page,
            'document': current_doc,
            'section_title': current_section
        })

    return chunks


### STEP 2: Create and Save Embeddings ###
def embed_chunks_and_save(chunks, out_path):
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [chunk['text'] for chunk in chunks]
    #best = benchmark_batch_sizes(texts=texts)
    embeddings = model.encode(texts, show_progress_bar=True)

    # Split into N batches (N = CPU cores)
    #num_cores = 8
    #batch_size = ceil(len(texts) / num_cores)
    #batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]

    #results = Parallel(n_jobs=num_cores)(
    #    delayed(embed_in_batch)(batch, model) for batch in batches
    #)

    #embeddings = np.concatenate(results, axis=0)

    for i, emb in enumerate(embeddings):
        chunks[i]['embedding'] = emb.tolist()

    with open(out_path, 'wb') as f:
        pickle.dump(chunks, f)


def embed_in_batch(texts, model):
    return model.encode(texts, show_progress_bar=False)


### STEP 3: Retrieval ###
def retrieve_top_chunks(pkl_path, persona, job_to_be_done, top_k=TOP_K):
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_text = f"Persona: {persona}. Task: {job_to_be_done}"
    query_embedding = model.encode([query_text], show_progress_bar=True)[0]

    with open(pkl_path, 'rb') as f:
        chunks = pickle.load(f)

    all_embeddings = np.array([chunk['embedding'] for chunk in chunks])
    scores = cosine_similarity([query_embedding], all_embeddings)[0]

    for i, score in enumerate(scores):
        chunks[i]['similarity'] = score

    # Sort by similarity
    sorted_chunks = sorted(chunks, key=lambda x: x['similarity'], reverse=True)

    # Separate top headings and body chunks
    top_sections = []
    top_subsections = []
    used_sections = set()
    
    for chunk in sorted_chunks:
        if len(top_sections) < top_k and chunk['label'] in ['title', 'H1', 'H2'] and chunk['text'] not in used_sections:
            top_sections.append({
                "document": chunk['document'],
                "section_title": chunk['text'],
                "importance_rank": len(top_sections)+1,
                "page_number": int(chunk['page'])
            })
            used_sections.add(chunk['text'])

        elif len(top_subsections) < top_k and chunk['label'] not in ['title', 'H1', 'H2']:
            top_subsections.append({
                "document": chunk['document'],
                "refined_text": chunk['text'],
                "page_number": int(chunk['page'])
            })

        if len(top_sections) >= top_k and len(top_subsections) >= top_k:
            break

    return top_sections, top_subsections


### STEP 4: Output Final JSON ###
def generate_final_output(input_docs, persona, job, sections, subsections, output_path):
    output = {
        "metadata": {
            "input_documents": input_docs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_sections": sections,
        "subsection_analysis": subsections
    }
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=4)


### PIPELINE WRAPPER ###
def run_pipeline(csv_path, persona, job, output_json_path, embedding_pkl_path='embeddings.pkl'):
    st = time.time()
    chunks = build_chunks_from_csv(csv_path)
    print(len(chunks))
    print(f"chunks built in : {(time.time() - st):0.2f}")
    st = time.time()
    input_docs = sorted(set([chunk['document'] for chunk in chunks]))
    print(f"input docs built in : {(time.time() - st):0.2f}")
    st = time.time()
    embed_chunks_and_save(chunks, embedding_pkl_path)
    print(f"embeddings built in : {(time.time() - st):0.2f}")
    st = time.time()
    sections, subsections = retrieve_top_chunks(embedding_pkl_path, persona, job)
    print(f"sections and subsections built in : {(time.time() - st):0.2f}")
    st = time.time()
    generate_final_output(input_docs, persona, job, sections, subsections, output_json_path)
    print(f"output generated in : {(time.time() - st):0.2f}")


import time
from sentence_transformers import SentenceTransformer

def benchmark_batch_sizes(texts, model_path=EMBEDDING_MODEL):
    model = SentenceTransformer(model_path, local_files_only=True)
    batch_sizes = [8, 16, 32, 64, 128]
    results = {}

    for bs in batch_sizes:
        start = time.time()
        model.encode(texts, batch_size=bs, show_progress_bar=False)
        elapsed = time.time() - start
        results[bs] = elapsed
        print(f"Batch size {bs}: {elapsed:.2f} seconds")

    best = min(results, key=results.get)
    print(f"\n✅ Fastest batch size: {best} (in {results[best]:.2f} seconds)")
    return best

### Example call (replace with your paths) ###
# persona = input("Enter Persona : ")
# job = input("Enter job : ")
# csv_path = input("Enter path to labelled csv : ")
# output_json_path = input("Enter path to output json : ")

# start_time = time.time()
# run_pipeline(
#     csv_path=csv_path,
#     persona=persona,
#     job=job,
#     output_json_path=output_json_path
# )
# end_time = time.time()
# elapsed = end_time - start_time
# print(f"\n✅ Execution completed in {elapsed:.2f} seconds.")
