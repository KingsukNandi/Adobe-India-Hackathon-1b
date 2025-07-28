# Approach Explanation: Persona-Driven PDF Summarizer Web App

## 1. Problem Statement & Motivation

Traditional PDF summarization tools often produce generic outputs, failing to adapt to the specific needs of different users. Our solution aims to generate structured, persona-driven summaries tailored to the user's role (e.g., student, analyst) and their intended task ("job to be done"). This enables more actionable, relevant insights from complex documents.

## 2. System Architecture Overview

The project is a full-stack web application with a React frontend and a Flask backend. Users upload up to 10 PDFs, specify their persona and task, and receive a JSON summary. The backend orchestrates PDF parsing, semantic chunking, embedding, and section retrieval, while the frontend provides an intuitive UI for upload, analysis, and download.

### Key Components

- **Frontend (React, Vite, TailwindCSS, DaisyUI):** Handles file upload, persona/job input, and displays results.
- **Backend (Flask, Gunicorn):** Manages API endpoints, PDF processing, and ML pipeline.
- **ML Pipeline:** Uses SentenceTransformer for semantic chunking and embedding, enabling context-aware section extraction.

## 3. PDF Processing Pipeline

### a. Line Extraction & Feature Engineering

PDFs are parsed using `pymupdf`, extracting lines and metadata (font size, style, position). This enables robust feature engineering for downstream tasks.

### b. Heuristic Heading Labelling

A custom module (`heuristic_labeller.py`) applies rules to label headings (title, h1, h2, etc.) based on font and layout features. This improves section segmentation and relevance ranking.

### c. Semantic Chunking & Embedding

Text is chunked into logical sections and embedded using the multilingual SentenceTransformer model. Embeddings capture semantic meaning, allowing for persona/job-specific retrieval.

### d. Top-K Section Retrieval

Given the persona and job prompt, the system retrieves the most relevant sections and subsections using similarity search over embeddings. This ensures summaries are tailored to user intent.

## 4. Output Generation

The final output is a structured JSON containing:

- Metadata (input docs, persona, job)
- Extracted sections (title, rank, page)
- Subsection analysis (refined text, page)

This format supports downstream consumption, analytics, and easy integration with other tools.

## 5. Deployment & Constraints

- **Local:** Python and Node.js required; run backend and frontend separately.
- **Docker:** Multi-stage build serves React as static files via Flask. No network access required for inference; model is downloaded at build time. CPU-only operation for broad compatibility.

## 6. Extensibility & Future Work

The modular design allows for easy upgrades:

- Swap out summarization logic for LLMs or custom models
- Enhance heuristics for complex layouts
- Add authentication, batch processing, and new export formats
- Integrate CI/CD and automated testing

## 7. Design Philosophy

- **Persona-driven:** Summaries adapt to user context
- **Modular:** Each processing step is a separate module
- **Scalable:** Handles multiple PDFs and large documents
- **User-centric:** Modern UI and downloadable outputs

This approach ensures the system is robust, extensible, and delivers high-value, context-aware summaries for diverse users.
