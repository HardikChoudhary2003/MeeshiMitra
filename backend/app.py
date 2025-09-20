import os
from dotenv import load_dotenv
import json
import faiss
import numpy as np
import google.generativeai as genai
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- 1. CONFIGURATI    ON ---
load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env file.")
    exit()

genai.configure(api_key=api_key)

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('index.faiss')
with open('product_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)


# --- 2. GEMINI PROMPT (Paste the updated version from above here) ---
MASTER_PROMPT = """
You are a highly specialized NLU service for Meesho, an Indian e-commerce company. Your SOLE function is to parse a user's query and return a raw, valid JSON object.

**Rules:**
1. Analyze the query for both explicit and implicit meaning. For example, "for my son" implies the category is "menswear" or "kids". "Kurti" or "saree" implies the category is "womenswear".
2. If a specific attribute is not mentioned in the query, its value in the JSON must be `null`.
3. If the user's query contains multiple, distinct product requests (e.g., 'sarees and shoes'), you MUST return a JSON list containing a separate JSON object for each request. If the query is for a single item, return a single JSON object as before (not inside a list).

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

**CRITICAL OUTPUT RULE:** Your response MUST be only the raw JSON object or list. DO NOT wrap it in markdown backticks like ```json ... ```. Your entire response must start with `{` or `[` and end with `}` or `]`, with absolutely no other text, explanations, or formatting.

**Analyze the following user query:**
"""

# --- 3. THE API ROUTE (Corrected Version) ---
@app.route('/search', methods=['GET'])
def search():
    raw_query = request.args.get('q')
    if not raw_query:
        return jsonify({"error": "Query parameter 'q' is missing."}), 400

    print(f"--- User Query Received: {raw_query} ---")

    search_tasks = []
    try:
        full_prompt = MASTER_PROMPT + f"Query: \"{raw_query}\""
        # CORRECTED MODEL NAME
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') #chawra
        # gemini_model = genai.GenerativeModel('gemini-2.0-flash')   #choudhary
        response = gemini_model.generate_content(full_prompt)
        print(f"--- Gemini API Response: {response.text} ---")
        
        response_data = json.loads(response.text)
        
        # --- CORRECTED LOGIC FOR NULL CHECK AND MULTI-INTENT ---
        if isinstance(response_data, dict):
            # It's a single search intent, let's check if it's empty
            extracted_values = [
                response_data.get('category'),
                response_data.get('product_type'),
                response_data.get('color'),
                response_data.get('occasion'),
                response_data.get('attributes')
            ]
            if not any(extracted_values):
                print("--- Gemini found no relevant entities. Returning empty result. ---")
                return jsonify([])
            
            # If it's valid, treat it as a list with one task
            search_tasks = [response_data]
        
        elif isinstance(response_data, list):
            # It's a multi-intent query, just use the list directly
            search_tasks = response_data

    except Exception as e:
        print(f"--- Gemini call failed or returned invalid data: {e} ---")
        search_tasks = [] # If anything fails, just result in an empty search

    # If, after all checks, there are no tasks, return empty
    if not search_tasks:
        return jsonify([])

    final_results = []
    seen_ids = set()

    # The rest of your loop logic is already correct
    for task in search_tasks:
        if len(final_results) >= 5:
            break

        filters = {}
        for key in ["category", "product_type", "color", "occasion"]:
            if task.get(key):
                filters[key] = task.get(key)
        
        query_parts = (task.get('attributes') or [])
        built_query = " ".join([part for part in query_parts if part])
        semantic_query = raw_query + " " + built_query if built_query else raw_query

        print(f"--- Running search for task with filters: {filters} ---")

        q_vec = model.encode([semantic_query])
        distances, candidate_ids = index.search(np.array(q_vec), k=1000)
        
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
                if len(final_results) % 2 == 0 and len(search_tasks) > 1:
                     break
            
            if len(final_results) >= 5:
                break
    
    return jsonify(final_results)

if __name__ == '__main__':
    app.run(port=5000)
