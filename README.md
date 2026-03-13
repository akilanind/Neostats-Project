# CitizenHelp
A simple streamlit chatbot to help users find and understand indian government schemes. Built for the neostats case study.

## Setup
1. Clone this repository
2. Install the requirements
   `pip install -r requirements.txt`
3. Add your Groq API key to a `.env` file like this:
   `GROQ_API_KEY=your_key_here`
4. Run the app
   `streamlit run app.py`

## Features
- Ask questions about any government scheme
- Upload a scheme PDF or text file to chat directly with that document (RAG)
- Tick the web search checkbox to get the latest updates from the internet

## Tech stack
- Python 3
- Streamlit (UI)
- Groq API (llama 3.3 70b model)
- ChromaDB (local vector database)
- Sentence Transformers (embeddings)
- DuckDuckGo Search (web scraping)
