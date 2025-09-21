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

You are a highly specialized NLU (Natural Language Understanding) service for an e-commerce platform. Your single most important function is to parse a user's query and return a raw, valid JSON object that strictly adheres to the schema and allowed values provided below.

**--- Schema and Allowed Values ---**

You MUST ONLY use the values from the lists below for the corresponding JSON keys.

**JSON Schema to follow:**
{
  "category": "string | null",
  "subcategory": "string | null",
  "product_type": "string | null",
  "color": "string | null",
  "occasion": "string | null"
}

**Allowed `category` values:**
- "menswear"
- "womenswear"
- "smartphones"
- "home_decor"
- "puja_decor"

**Allowed `subcategory` values:**
- "topwear"
- "bottomwear"
- "belts"
- "headwear"
- "smartphone"

**Allowed `product_type` values:**
- "kurti"
- "jacket"
- "jeans"
- "belt"
- "cap"
- "shirt"
- "mobile"
- "smartphone"

**Allowed `occasion` values:**
- "festival"
- "casual"
- "party"
- "sports"

**--- Core Rules ---**

1.  **Strict Mapping:** Your primary goal is to map the user's language to the **exact** allowed values listed above.
    - If the user says "phone", "smartphone", "mobile", or "cellphone", you MUST map it to `product_type: "smartphone"`.
    - If the user says "diwali", or any festival, you MUST map it to `occasion: "festival"`.
    - If the user says "kurta" or "saree", you MUST infer `category: "womenswear"`.
    - If the user says "pooja" or "mandir", you MUST infer `category: "puja_decor"`.

2.  **Null for Unknowns:** If a specific attribute is not mentioned or cannot be inferred from the query, its value in the JSON MUST be `null`.

3.  **Multi-Intent Queries:** If the user's query contains multiple, distinct product requests (e.g., 'sarees and puja decore'), you MUST return a JSON list containing a separate JSON object for each request. For a single item query, return only the single JSON object.


**--- Examples ---**

Query: "I need a green smartphone"
{
  "category": "smartphones",
  "subcategory": "smartphone",
  "product_type": "smartphone",
  "color": "green",
  "occasion": null
}

Query: "show me black jeans and a white shirt for party"
[
  {
    "category": null,
    "subcategory": "bottomwear",
    "product_type": "jeans",
    "color": "black",
    "occasion": "party"
  },
  {
    "category": null,
    "subcategory": "topwear",
    "product_type": "shirt",
    "color": "white",
    "occasion": "party"
  }
]

Query: "decorations for pooja"
{
  "category": "puja_decor",
  "subcategory": null,
  "product_type": null,
  "color": null,
  "occasion": "festival"
}

**--- !! CRITICAL OUTPUT RULE !! ---**
Your response MUST be only the raw JSON. DO NOT wrap it in markdown backticks like ```json ... ```. Your entire response must start with `{` or `[` and end with `}` or `]`, with absolutely no other text, explanations, or formatting.

**--- Analyze the following user query: ---**
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
        # gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') #chawra
        full_prompt = MASTER_PROMPT + f"Query: \"{raw_query}\""

        gemini_model = genai.GenerativeModel('gemini-2.0-flash')   # choudhary
        response = gemini_model.generate_content(full_prompt)

        # Clean response: strip whitespace and remove code fences if present
        response_text = response.text.strip()

        if response_text.startswith("```"):
            lines = response_text.splitlines()
            # Drop the first line (``` or ```json)
            lines = lines[1:]
            # Drop the last line if it's ```
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            response_text = "\n".join(lines).strip()

        # print(f"--- Gemini API Raw Response: {response.text} ---")
        print(f"--- Gemini API Cleaned Response: {response_text} ---")

        response_data = json.loads(response_text)
        
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
        distances, candidate_ids = index.search(np.array(q_vec), k=10000)
        
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
    print(final_results)
    return jsonify(final_results)

if __name__ == '__main__':
    app.run(port=5000)
