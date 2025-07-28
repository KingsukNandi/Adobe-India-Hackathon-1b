import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import PdfDropzone from "./upload/PdfDropzone";

export default function Upload() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleFilesSelected = (files) => {
    // Generate object URLs for each PDF file
    const filesWithUrl = files.map((file) => ({
      file,
      name: file.name,
      url: URL.createObjectURL(file),
    }));
    setPdfFiles(filesWithUrl);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    // Simulate upload delay
    setTimeout(() => {
      setSubmitting(false);
      // Pass pdfFiles to analyst page via location state
      navigate("/analyst", { state: { pdfFiles } });
    }, 1000);
  };

  return (
    <div className="max-w-xl mx-auto p-8 flex flex-col gap-6">
      <h2 className="text-2xl font-bold mb-2">Upload PDF Files</h2>
      <PdfDropzone onFilesSelected={handleFilesSelected} />
      {pdfFiles.length > 0 && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2 text-base">Selected PDFs:</h3>
          <ul className="list-disc ml-6 text-sm">
            {pdfFiles.map((pdf, idx) => (
              <li key={idx}>{pdf.name}</li>
            ))}
          </ul>
        </div>
      )}
      <button
        className="btn btn-primary mt-6"
        disabled={pdfFiles.length === 0 || submitting}
        onClick={handleSubmit}
      >
        {submitting ? "Uploading..." : "Submit PDFs"}
      </button>
    </div>
  );
}
