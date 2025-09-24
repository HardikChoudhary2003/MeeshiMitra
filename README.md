# MeeshoMitra: Intelli AI Assist

MeeshoMitra is an intelligent e-commerce search application featuring a modern React frontend and a powerful Python backend. The application provides a conversational search experience where users can enter queries in natural language.

## 🚀 Project Demo Video

[![Watch the video](https://github.com/user-attachments/assets/b1ea1f5a-a8db-4e94-b476-1cf4ad3ecb03)](https://youtu.be/FkXvNpIf9E4)

## Tech Stack

### Frontend

*   **Framework:** React
*   **Build Tool:** Vite
*   **Language:** TypeScript
*   **Styling:** Tailwind CSS & shadcn/ui
*   **UI Components:** Radix UI
*   **Routing:** React Router DOM
*   **API Communication:** TanStack Query (React Query)
*   **Form Management:** React Hook Form with Zod for validation

### Backend

*   **Framework:** Flask (Python)
*   **AI & Machine Learning:**
    *   **Natural Language Understanding (NLU):** Google Generative AI (Gemini) to parse user queries.
    *   **Semantic Search:** `sentence-transformers` to create vector embeddings and `faiss` for efficient similarity search.
*   **API:** RESTful API for search functionality.
*   **CORS:** Handled with `Flask-CORS`.

## Project Summary

The backend leverages Google's Gemini model to dissect user queries into structured data, identifying categories, product types, colors, and other attributes. This structured information is then used to perform a sophisticated semantic search using a FAISS vector index, ensuring highly relevant product results are returned. The system is capable of handling multi-intent queries (e.g., "sarees and shoes") in a single request.

## Getting Started

### Prerequisites

*   Node.js and npm (or pnpm/yarn)
*   Python 3.x and pip
*   A Google API key with access to the Gemini API.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/MeeshoMitra.git
    cd MeeshoMitra
    ```

2.  **Frontend Setup:**
    ```bash
    # Navigate to the frontend directory
    cd meeshomitra-frontend 

    # Install dependencies
    npm install

    # Start the development server
    npm run dev
    ```

3.  **Backend Setup:**
    ```bash
    # Navigate to the backend directory
    cd ../meeshomitra-backend

    # Create a virtual environment
    python -m venv venv
    source venv/bin/activate # on Windows use `venv\Scripts\activate`

    # Install dependencies
    pip install -r requirements.txt

    # Create a .env file and add your Google API key
    echo "GOOGLE_API_KEY=your_api_key_here" > .env

    # Run the Flask application
    python app.py


MeeshoMitra: Intelligent Conversational Search for India
Problem Definition

While Meesho has made online shopping accessible to millions, the current keyword-based search engine struggles with natural, multi-word, or slightly misspelled queries.
Some common failure cases include:

Works for simple queries like “smart phone”, but fails at “latest smart phone” or “smartphone” (typos, spacing issues).

Fails for intent-driven queries like “party wears for my husband” (needs category + gender + occasion understanding).

Breaks for multi-intent discovery like “different items for diwali” (requires parsing multiple categories).

Such limitations frustrate users and reduce seller visibility. A customer expecting quick discovery abandons the app when irrelevant or zero results appear. Sellers with relevant products lose sales simply because the system couldn’t interpret user intent.

Discovery Process

We analyzed Meesho’s discovery funnel, app reviews, and ran experiments with common user queries. We found:

High error rate in multi-word queries: More than 30% of casual search attempts in Tier-2/Tier-3 contexts are natural sentences instead of keywords.

Low tolerance for typos and variations: Simple spelling variations or combined words break search.

Missed contextual queries: Users increasingly express needs as sentences (“different sarees for office wear”), not as single keywords.

We built test cases, and the results clearly highlighted that search breakdown is one of the biggest user pain points.

Rationale

We chose this problem because:

Universal Impact: Search is the entry point for most Meesho journeys. A better search directly drives conversions.

Equity for Sellers: Small sellers without optimized keywords in their product listing get visibility through AI-powered semantic matching.

Strategic Edge: Meesho can lead the market by offering conversational shopping for India, appealing to first-time internet users who think in natural language rather than keywords.

Stakeholders Impacted

Customers: Reduced frustration, faster product discovery, better trust in platform.

Sellers: Higher exposure of products, especially long-tail inventory.

Delivery Partners: Indirectly benefit as better discovery = more orders.

Meesho Platform: Increased engagement, higher GMV, and stronger ecosystem credibility.

Proposed Solution: MeeshoMitra

MeeshoMitra introduces a conversational AI-powered search system with intent extraction and semantic understanding.

How It Works (Example):

User types: “party wears for my husband”

Gemini API parses → { "category": "menswear", "product_type": "shirt", "occasion": "party" }

Semantic search + filters applied → Returns men’s party wear shirts, blazers, etc.

User types: “different items for diwali”

AI identifies → { "occasion": "diwali", "multi_intent": true, categories: [decor, clothes, gifts] }

Multiple categories returned in a conversational, grouped format.

Architecture Design

Application Flow:

User query → Frontend React conversational UI.

Backend (Flask) → Sends to Gemini AI for intent extraction.

Structured intent → Converted into filters (category, product_type, attributes).

Embedding + FAISS semantic search → Retrieves top relevant results.

Response → Displayed in user-friendly conversational style.

High-Level Design:

Frontend: React + Tailwind + shadcn/ui (chat-style search box, smart filters).

Backend: Flask API with Gemini NLU + FAISS semantic retrieval.

Search Pipeline:

Input → Gemini parsing → Structured JSON → Semantic embedding → FAISS index → Ranked results.

Low-Level Design Optimizations:

Error Handling: Typos/variations corrected via embeddings.

Multi-intent parsing: Handles multiple product requests in one query.

Incremental indexing: New seller catalogs continuously embedded & indexed.

Future-ready: Extendable to voice + vernacular inputs for Tier-2/Tier-3 adoption.
