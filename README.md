# BEYOND SPACE RAG API

AI-powered RAG backend for *A Guide Beyond Space*, an interactive museum experience combining voice input, retrieval-augmented generation, and spoken answers for artwork-related questions.

## Overview

`beyond-space-rag-api` is a FastAPI backend that powers the conversational AI layer of *A Guide Beyond Space*. It processes spoken visitor questions, retrieves relevant context from a curated knowledge base of artists and artworks, generates grounded answers, and returns both text and audio output.

The system is designed for museum-style interactions, where answers should remain concise, context-based, and suitable for spoken playback.

## Project Context

This backend is part of the Unity-based interactive museum experience A Guide Beyond Space.
It supports a conversational guide character that can answer visitor questions about artworks, artists, and exhibition context.

## Features
- speech-to-text via ElevenLabs
- retrieval-augmented generation over curated museum content
- answer generation via OpenAI
- text-to-speech via ElevenLabs
- FastAPI-based `/ask` endpoint for Unity integration

## Tech Stack
- Python 3.11
- FastAPI
- Uvicorn
- ChromaDB
- sentence-transformers
- OpenAI API
- ElevenLabs API
- Fly.io for deployment
- Docker

## API Endpoints
### `GET /health`
Returns service health and collection size.
Example response: 
{
  "status": "ok",
  "collection_count": 425
}

### `POST /ask`
Accepts an audio file and returns:
- transcript
- answer_text
- audio_base64

## Environment Variables

- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `OPENAI_MODEL=gpt-5.4-mini`
- `ELEVENLABS_MODEL_ID=eleven_flash_v2_5`
- `ELEVENLABS_STT_MODEL_ID=scribe_v2`
- `ELEVENLABS_STT_LANGUAGE_CODE=deu`
- `CHROMA_PATH=data/chroma`
- `DOCS_PATH=data/docs`

## Local Development

```bash
pip install -r requirements.txt
python scripts/build_index.py
uvicorn app.main:app --host 0.0.0.0 --port 8000

## Health check
http://localhost:8000/health

## Fly.io Deployment
This project is deployed on Fly.io with Docker.

### Deploy
fly deploy
Set secrets
fly secrets set OPENAI_API_KEY=your_openai_key
fly secrets set ELEVENLABS_API_KEY=your_elevenlabs_key
Check secrets
fly secrets list

### Check logs
fly logs

### Health endpoint
https://beyond-space-rag-api.fly.dev/health
```

## Docker
The application is containerized with Docker and runs with Uvicorn on port 10000.

## Notes
The embedding model is cached during the Docker build to reduce cold-start overhead at runtime.
The knowledge base is based on curated markdown files covering artworks, artists, and exhibition context.
The API is designed for integration into a Unity-based application, including Windows development builds.

## Status
This repository contains the production backend used for the conversational museum guide prototype.

## License
MIT License
