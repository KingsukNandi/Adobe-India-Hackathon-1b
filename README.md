# **Persona-Driven PDF Summarizer Web App**

## 🧠 Overview

A full-stack web app for uploading PDF files and generating structured, persona-driven summaries using semantic chunking and ML embeddings.

**Input format:**

- Up to 10 PDF files (via web UI)
- Persona (string, e.g. "student")
- Job to be done (string, e.g. "summarize key points")

**Output format:**

- JSON summary per PDF, e.g.:

```json
{
  "metadata": {
    "input_documents": ["list"],
    "persona": "User Persona",
    "job_to_be_done": "Task description"
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Title",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf",
      "refined_text": "Content",
      "page_number": 1
    }
  ]
}
```

---

## 📁 Folder Structure

```
├── Dockerfile
├── README.md
├── api/
│   ├── __init__.py
│   ├── app.py              # Flask backend (main entry)
│   ├── heuristic_labeller.py # Heuristic line/heading labeller
│   ├── line_parser.py      # PDF line extraction & feature engineering
│   ├── main.py             # ML pipeline: chunking, embedding, retrieval
│   ├── model.py            # SentenceTransformer model loader
│   ├── requirements.txt    # Python dependencies
├── web/
│   ├── index.html
│   ├── package.json        # React frontend dependencies
│   ├── src/
│   │   ├── App.jsx         # Main React app
│   │   ├── components/     # UI components (Upload, Analyst, etc.)
│   │   ├── analyst/        # Analyst view (AsidePanel, JsonViewer, PdfTabs)
│   │   ├── upload/         # PDF dropzone
│   │   └── ...
│   └── ...
```

- **Input PDFs:** Uploaded via web UI, processed in backend (`uploads/` folder, created at runtime)
- **Output summaries:** Returned as JSON via API, downloadable in frontend
- **Key files:** `api/app.py` (Flask API), `api/main.py` (ML pipeline), `Dockerfile` (multi-stage build)

---

## 🚀 How to Run (Locally)

**Prerequisites:**

- Python 3.8+
- Node.js 18+
- pip

**Backend setup:**

```sh
cd api
pip install -r requirements.txt
python app.py
```

**Frontend setup:**

```sh
cd web
npm install
npm run dev
```

**Sample run:**

- Open [http://localhost:5173](http://localhost:5173) for frontend
- Backend runs at [http://localhost:5000](http://localhost:5000)
- Upload PDFs, enter persona/job, click "Analyze PDFs"

**Output:**

- Downloadable JSON summary in Analyst view

---

## 🐳 How to Run (via Docker)

**Build image:**

```sh
docker build -t pdf-summarizer-app .
```

**Run container:**

```sh
docker run -p 5000:5000 pdf-summarizer-app
```

- App available at [http://localhost:5000](http://localhost:5000)
- React build served as static files by Flask backend
- **Input:** Upload PDFs via web UI
- **Output:** Download JSON summary

**Constraints:**

- No network access required for inference (model downloaded at build)
- Container runs with CPU only

---

## ✅ Current Features

- Upload up to 10 PDF files via drag-and-drop or browse
- Persona/job prompt for custom summarization
- PDF line extraction and feature engineering
- Heuristic labelling of headings (title, h1, h2, etc.)
- ML-based chunking and semantic embedding (SentenceTransformer)
- Top-K retrieval of relevant sections/subsections
- JSON summary output, downloadable from UI
- Modern React UI (Vite, TailwindCSS, DaisyUI)
- Dockerized full-stack deployment

---

## 📦 Model and Libraries Used

- **SentenceTransformer (intfloat/multilingual-e5-small):** Semantic chunk embedding (~500MB, CPU)
- **pymupdf:** PDF parsing and text extraction
- **pandas, numpy:** Data manipulation
- **Flask, flask-cors, gunicorn:** Backend API and serving
- **React, Vite, TailwindCSS, DaisyUI:** Frontend UI

**Constraints:**

- Model size ~500MB, loaded at build time
- No GPU required
- All dependencies listed in `api/requirements.txt` and `web/package.json`

---

## 📌 TODO (for future improvements)

- Replace placeholder summarization with LLM or custom logic
- Add support for more PDF layouts and edge cases
- Improve heading/section detection heuristics
- Add authentication/user management
- Enable batch processing and async jobs
- Enhance UI/UX for large document sets
- Add export formats (CSV, TXT)
- Optimize Docker image size and build speed
- Add tests and CI/CD pipeline

---

## Notes

- Backend serves React build as static files for all routes
- PDF parsing and summarization logic is modular and extensible
- See `approach_explanation.md` for methodology and design decisions
