import pandas as pd
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

print("Starting the index generation process...")

# --- Step 1: Load and Prepare the Data ---
print("\n--- Step 1: Loading and Preparing Data ---")
try:
    # Load the product data from your JSON file
    with open('product_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
except FileNotFoundError:
    print("Error: 'product_data.json' not found. Please ensure the file is in the same directory.")
    exit()

# It's crucial to remove duplicates so that each vector in the index corresponds to a unique item.
df.drop_duplicates(subset='id', inplace=True, keep='first')
df.reset_index(drop=True, inplace=True) # Reset index after dropping duplicates

# Define the text columns to be used for the embedding
text_columns = ['title', 'description', 'category', 'subcategory', 'color', 'product_type']

# Fill any missing values (NaN) in these columns with an empty string
for col in text_columns:
    if col in df.columns:
        df[col] = df[col].fillna('')

# Combine the relevant text fields into a single, rich string for each product
df['combined_features'] = df.apply(
    lambda row: " ".join([str(row[col]) for col in text_columns if col in row]),
    axis=1
)

print(f"Successfully loaded and prepared {len(df)} unique products.")
print("Example of a combined feature string for embedding:")
print(df['combined_features'].iloc[0])


# --- Step 2: Generate Vector Embeddings ---
print("\n--- Step 2: Generating Vector Embeddings ---")
# Initialize a pre-trained model. 'all-MiniLM-L6-v2' is efficient and effective.
print("Loading the Sentence Transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for the combined text. This may take a moment.
print("Encoding product features into vectors...")
embeddings = model.encode(df['combined_features'].tolist(), show_progress_bar=True)

# FAISS requires the embeddings to be in float32 format
embeddings = np.array(embeddings).astype('float32')

print(f"Embeddings generated with shape: {embeddings.shape}")


# --- Step 3: Build and Train the FAISS Index ---
print("\n--- Step 3: Building the FAISS Index ---")
# Get the dimension of the embeddings (e.g., 384 for 'all-MiniLM-L6-v2')
embedding_dimension = embeddings.shape[1]

# We will use IndexFlatL2, a basic index for exact search using L2 (Euclidean) distance.
# It's a great starting point.
index = faiss.IndexFlatL2(embedding_dimension)

# Add the generated embeddings to the index
index.add(embeddings)

print(f"FAISS index built successfully. Total vectors in index: {index.ntotal}")


# --- Step 4: Save the Index and DataFrame ---
print("\n--- Step 4: Saving the Index and DataFrame for later use ---")

# Save the FAISS index to a file
faiss.write_index(index, "index.faiss")

# Save the DataFrame (with unique IDs) so we can map search results back to product info
df.to_csv("products_dataframe.csv", index=False)

print("\nProcess Complete!")
print("-> FAISS index saved to 'index.faiss'")
print("-> Product data saved to 'products_dataframe.csv'")