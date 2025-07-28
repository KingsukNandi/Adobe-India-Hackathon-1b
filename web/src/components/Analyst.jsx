import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import PdfTabs from "./analyst/PdfTabs";
// Function to open a specific PDF and page

import AsidePanel from "./analyst/AsidePanel";
import JsonViewer from "./analyst/JsonViewer";

export default function Analyst() {
  const location = useLocation();
  const pdfFiles = location.state?.pdfFiles || [];
  const [activeIdx, setActiveIdx] = useState(0);
  const [persona, setPersona] = useState("");
  const [job, setJob] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleAnalyze = async () => {
    if (!persona || !job) {
      alert("Please enter persona and job before analyzing.");
      return;
    }
    if (pdfFiles.length === 0) {
      alert("Please upload PDFs first.");
      return;
    }

    try {
      setLoading(true);
      setAnalysisResult(null); // clear previous results

      const formData = new FormData();
      formData.append("persona", persona);
      formData.append("job", job);

      pdfFiles.forEach((pdf) => {
        formData.append("pdfs", pdf.file);
      });

      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Server error:", errorData);
        alert(errorData.error || "Upload failed");
        return;
      }

      const data = await response.json();
      console.log("Analysis result:", data);
      setAnalysisResult(data);
    } catch (err) {
      console.error("Error analyzing PDFs:", err);
      alert("Error analyzing PDFs. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-dvh p-8 gap-8">
      {/* If analysisResult is present, show split view with JSON viewer */}
      {analysisResult?.summary ? (
        <>
          <div className="flex-1 flex flex-col overflow-y-auto border-r border-base-300 pr-6">
            <h2 className="text-2xl font-bold mb-4">Analyst</h2>
            {pdfFiles.length > 0 ? (
              <PdfTabs
                pdfFiles={pdfFiles}
                activeIdx={activeIdx}
                setActiveIdx={setActiveIdx}
              />
            ) : (
              <div className="text-base-content/70 text-center mt-16">
                No PDFs uploaded. Please upload PDFs first.
              </div>
            )}
            {loading && (
              <div className="text-primary text-center mt-4">
                Analyzing PDFs...
              </div>
            )}
          </div>
          <div className="w-1/2 max-w-2xl min-w-[350px] pl-6 flex flex-col">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              Analysis Result (JSON)
            </h3>
            <div className="flex-1 overflow-y-auto">
              {/* Show the JSON viewer for the result */}
              <div className="shadow-lg border border-base-300 bg-base-200 rounded-lg p-2">
                {/*<pre className="text-xs text-base-content/80 mb-2">
                  Raw JSON:
                </pre>*/}
                <div className="overflow-y-auto">
                  {/* Only show the full result, not just summary */}
                  <JsonViewer data={analysisResult.summary} />
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="flex-1 flex flex-col overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Analyst</h2>
            {pdfFiles.length > 0 ? (
              <PdfTabs
                pdfFiles={pdfFiles}
                activeIdx={activeIdx}
                setActiveIdx={setActiveIdx}
              />
            ) : (
              <div className="text-base-content/70 text-center mt-16">
                No PDFs uploaded. Please upload PDFs first.
              </div>
            )}
            {loading && (
              <div className="text-primary text-center mt-4">
                Analyzing PDFs...
              </div>
            )}
          </div>
          <AsidePanel
            persona={persona}
            setPersona={setPersona}
            job={job}
            setJob={setJob}
            onAnalyze={handleAnalyze}
            analysisResult={analysisResult}
          />
        </>
      )}
    </div>
  );
}
