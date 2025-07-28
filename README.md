# Persona-Driven Document Intelligence (1b)

## Deliverables

- `approach_explanation.md`: Explains the methodology and design decisions (see that file for details).
- `Dockerfile`: Multi-stage build for React frontend and Flask backend (see below).
- **Execution instructions**: How to build and run the app using Docker.
- **Sample input/output**: Example usage for testing the app.

---

## Project Overview

This project is a full-stack web application for uploading PDF files and generating structured summaries. It consists of:

- **Frontend**: React (Vite, TailwindCSS, DaisyUI)
- **Backend**: Python Flask API (with CORS, Gunicorn for production)
- **PDF Parsing & Summarization**: Placeholder logic for demo/testing

---

## Dockerfile & Execution Instructions

### 1. Build the Docker Image

```sh
docker build -t pdf-summarizer-app .
```

### 2. Run the Docker Container

```sh
docker run -p 5000:5000 pdf-summarizer-app
```

- The app will be available at [http://localhost:5000](http://localhost:5000)

---

## Sample Input/Output for Testing

### Sample Input

- Upload up to 10 PDF files using the web interface.
- Enter a persona (e.g., "student") and job (e.g., "summarize key points").
- Click "Analyze PDFs".

### Sample Output

```
👤 Role: student
📝 Prompt: summarize key points

Summary of uploaded PDFs:

📄 File: example.pdf
- [TITLE] Title extracted from uploads/example.pdf
- [H1] Section 1: Introduction
- [H2] Background
- [H2] Motivation
- [H1] Section 2: Methodology
- [H3] Data Collection
- [H4] Survey Details

✅ This is a placeholder summary. Replace with your LLM or custom summarization logic.
```

---

## Notes

- The backend serves the React build as static files for all routes.
- The PDF parsing and summarization are placeholders; replace with your own logic as needed.
- For more details, see `approach_explanation.md`.
