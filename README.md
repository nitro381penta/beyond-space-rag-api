# BEYOND SPACE RAG API

AI-powered RAG backend for *A Guide Beyond Space*, an interactive museum experience combining voice input, retrieval-augmented generation, and spoken answers for artwork-related questions.

## Overview

`beyond-space-rag-api` is a FastAPI backend that powers the conversational AI layer of *A Guide Beyond Space*. It processes spoken visitor questions, retrieves relevant context from a curated knowledge base of artists and artworks, generates grounded answers, and returns both text and audio output.

The system is designed for museum-style interactions, where answers should remain concise, context-based, and suitable for spoken playback.

## Features

- Speech-to-text pipeline for spoken visitor questions
- Retrieval-augmented generation based on local markdown knowledge files
- Context-grounded responses for artists, artworks, and exhibition topics
- Text-to-speech output for audio playback
- Query normalization for improved robustness with names, artwork titles, and speech recognition variations
- FastAPI-based API for local development and deployment
- Ready for integration with Unity applications

## Tech Stack

- **Python**
- **FastAPI**
- **Uvicorn**
- **ChromaDB**
- **Sentence Transformers**
- **Render** for deployment
- **Unity** as frontend/client integration

## Project Structure

```text
beyond-space-rag-api/
├── app/
│   ├── main.py
│   ├── retrieval.py
│   ├── rag_index.py
│   ├── query_normalizer.py
│   ├── prompt_builder.py
│   ├── llm_remote.py
│   ├── stt_elevenlabs.py
│   ├── tts_elevenlabs.py
│   ├── embeddings.py
│   ├── config.py
│   └── schemas.py
├── data/
│   └── docs/
│       ├── artists/
│       ├── artworks/
│       └── general/
├── scripts/
│   └── build_index.py
├── requirements.txt
├── Dockerfile
└── README.md
=======
# beyond-space-rag-api
AI-powered RAG backend for A Guide Beyond Space, an interactive museum experience combining voice input, retrieval-augmented generation, and spoken answers for artwork-related questions.

