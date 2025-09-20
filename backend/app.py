import os
import json
import faiss
import numpy as np
import google.generativeai as genai
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- 1. CONFIGURATION ---
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('index.faiss')
with open('product_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)


# --- 2. GEMINI PROMPT (Paste the updated version from above here) ---
MASTER_PROMPT = """
You are an expert NLU (Natural Language Understanding) model for Meesho, an Indian e-commerce company. Your single task is to analyze a user's search query and extract key product attributes into a structured JSON object.

**Rules:**
1. Analyze the query for both explicit and implicit meaning. For example, "for my son" implies the category is "menswear" or "kids". "Kurti" or "saree" implies the category is "womenswear".
2. If a specific attribute is not mentioned in the query, its value in the JSON must be `null`.
3. Your response MUST be a single, valid JSON object without any extra text or markdown.
4. **If the user's query contains multiple, distinct product requests (e.g., 'sarees and shoes'), you MUST return a JSON list containing a separate JSON object for each request. If the query is for a single item, return a single JSON object as before (not inside a list).**
5. give response as below and strictly follow the response format, donot add "```"at start and end position

**JSON Schema to follow:**
{
  "category": "string | null",
  "product_type": "string | null",
  "color": "string | null",
  "occasion": "string | null",
  "attributes": ["string"]
}

**Examples:**
Query: "red saree for wedding"
{
  "category": "womenswear",
  "product_type": "saree",
  "color": "red",
  "occasion": "wedding",
  "attributes": []
}

Query: "blue kurtis and home decor"
[
  {
    "category": "womenswear",
    "product_type": "kurti",
    "color": "blue",
    "occasion": null,
    "attributes": []
  },
  {
    "category": "home_decor",
    "product_type": null,
    "color": null,
    "occasion": null,
    "attributes": []
  }
]

**Analyze the following user query:**
"""

# --- 3. THE API ROUTE ---
@app.route('/search', methods=['GET'])
def search():
    raw_query = request.args.get('q')
    if not raw_query:
        return jsonify({"error": "Query parameter 'q' is missing."}), 400

    print(f"--- User Query Received: {raw_query} ---")

    search_tasks = []
    try:
        full_prompt = MASTER_PROMPT + f"Query: \"{raw_query}\""
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        response = gemini_model.generate_content(full_prompt)
        print(f"--- Gemini API Response: {response.text} ---")
        
        response_data = json.loads(response.text)
        
        # Check if Gemini returned a list (multi-intent) or a single object
        if isinstance(response_data, list):
            search_tasks = response_data
        else:
            search_tasks = [response_data] # Treat it as a list with one item

    except Exception as e:
        print(f"--- Gemini call failed or returned invalid data: {e} ---")
        # Fallback: create a single search task with no filters
        search_tasks = [{'category': None, 'product_type': None, 'color': None, 'occasion': None, 'attributes': []}]

    final_results = []
    seen_ids = set()

    for task in search_tasks:
        if len(final_results) >= 5:
            break

        filters = {}
        for key in ["category","product_type","color", "occasion"]:
            if task.get(key):
                filters[key] = task.get(key)
        
        query_parts = (task.get('attributes') or [])
        built_query = " ".join([part for part in query_parts if part])
        semantic_query = raw_query + " " + built_query if built_query else raw_query

        print(f"--- Running search for task with filters: {filters} ---")

        q_vec = model.encode([semantic_query])
        distances, candidate_ids = index.search(np.array(q_vec), k=10000)
        
        # Add results for this task until we find a few or run out of candidates
        for doc_id in candidate_ids[0]:
            product = products[int(doc_id)]
            product_id = product.get('id')

            if product_id in seen_ids:
                continue

            passes_all_filters = True
            for key, value in filters.items():
                if str(product.get(key, '')).lower().strip() != str(value).lower().strip():
                    passes_all_filters = False
                    break
            
            if passes_all_filters:
                final_results.append(product)
                seen_ids.add(product_id)
                # Simple logic to get a mix of results: stop after finding 2 for this task
                if len(final_results) % 2 == 0 and len(search_tasks) > 1:
                     break
            
            if len(final_results) >= 5:
                break
    print(f"---------------------------------{final_results}---------------------------")
    return jsonify(final_results)

if __name__ == '__main__':
    app.run(port=5000)
