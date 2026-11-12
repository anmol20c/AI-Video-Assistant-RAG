
# AI Video Assistant with RAG 🎥

An AI-powered application that converts YouTube videos and audio into searchable knowledge through transcription, summarization, action item extraction, and Retrieval-Augmented Generation (RAG).

## Features
- YouTube and audio input
- Speech-to-text using Whisper
- AI-powered summarization
- Automatic action item extraction
- RAG-based question answering
- Chat with video content
- Export summaries and insights

## Tech Stack
- Python
- LangChain
- Whisper
- Mistral AI
- ChromaDB
- Streamlit

## How It Works
1. Upload audio or provide a YouTube link.
2. Transcribe content using Whisper.
3. Generate summaries and action items.
4. Store content as embeddings in ChromaDB.
5. Retrieve relevant context using RAG.
6. Ask questions and get AI-generated answers.

## Installation

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI-Video-Assistant-RAG
pip install -r requirements.txt
streamlit run app.py
```

## Author
Anmol Choudhary

[GitHub](https://github.com/anmol20c) |
[LinkedIn](https://www.linkedin.com/in/anmol-choudhary-08002528a/)
