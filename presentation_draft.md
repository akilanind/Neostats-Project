# CitizenHelp Presentation Content

## Slide 1: Title Slide
CitizenHelp
A simple chatbot helping citizens navigate government schemes
[Your Name]

## Slide 2: Objective
Problem:
- Government schemes are scattered across many difficult-to-navigate websites.
- Complex official language makes eligibility hard to understand for average citizens.
Why this matters:
- Millions miss out on benefits simply because they don't know how to find them.
Objective:
- Build an accessible, single-point interface to discover schemes and check eligibility instantly in plain language.

## Slide 3: Approach
- Keep the UI as simple as possible  No complex nested menus, just a chat interface.
- Local first approach  Decided to use ChromaDB and Sentence-Transformers locally to keep it lightweight and fast without relying on paid embedding APIs.
- Fallback mechanism  If documents aren't uploaded, use live web search to pull the latest rules rather than trusting outdated LLM training data.

## Slide 4: Solution Architecture
- Frontend: Streamlit (clean, responsive chat layout)
- Brain: Groq API (Llama 3.3 70B for fast, accurate parsing of legal text)
- RAG Pipeline: PyPDF + ChromaDB for searching through user-uploaded scheme PDFs
- Live Data: DuckDuckGo search integration for breaking updates
Flow: User asks query -> RAG checks local PDF OR Web Search checks live data -> Context passed to Groq Llama -> Streamlit displays formatted answer.

## Slide 5: Features Implemented
Core Features:
- Conversational chat interface for Q&A
- Concise vs Detailed answer modes
- RAG (Upload any scheme PDF and chat directly with it)
Extra Features:
- Live Web Search integration to handle questions about brand-new schemes
- One-click quick question shortcuts for common topics (Farmers, Students, etc.)

## Slide 6: Challenges & Decisions
- Challenge: Chunking complex PDFs without losing context.
  - Decision: Implemented a sliding window approach with 50-character overlap.
- Challenge: Keeping the app cost-free.
  - Decision: Used free Groq tier for inference, free DuckDuckGo for search, and CPU-friendly all-MiniLM-L6-v2 for local embeddings.
- Challenge: Slow ChromaDB initialization on Streamlit Cloud.
  - Decision: Switched to an ephemeral in-memory client that builds the vector store only when a file is actively uploaded.

## Slide 7: Live Demo
Deployment Link: 
[Insert your Streamlit Cloud URL here]

Source Code: 
https://github.com/akilanind/Neostats-Project
