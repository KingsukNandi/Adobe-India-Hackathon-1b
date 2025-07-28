import React, { useRef, useState } from "react";

export default function PdfDropzone({ onFilesSelected }) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef();

  const handleFiles = (files) => {
    const pdfFiles = Array.from(files).filter(
      (file) => file.type === "application/pdf"
    );
    if (pdfFiles.length !== files.length) {
      setError("Only PDF files are allowed.");
    } else {
      setError("");
      onFilesSelected(pdfFiles);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleBrowse = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-colors ${
        dragActive
          ? "border-primary bg-base-200"
          : "border-base-300 bg-base-100"
      }`}
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        multiple
        accept="application/pdf"
        ref={inputRef}
        className="hidden"
        onChange={handleBrowse}
      />
      <button
        type="button"
        className="btn btn-outline btn-sm mb-2"
        onClick={() => inputRef.current.click()}
      >
        Browse PDF Files
      </button>
      <span className="text-sm text-base-content mb-2">
        or drag and drop here
      </span>
      {error && <span className="text-error text-xs mt-2">{error}</span>}
    </div>
  );
}
