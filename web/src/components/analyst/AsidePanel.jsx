import React from "react";

export default function AsidePanel({
  persona,
  setPersona,
  job,
  setJob,
  onAnalyze,
  analysisResult,
}) {
  return (
    <aside className="w-80 bg-base-100 p-6 rounded-lg flex flex-col gap-4 border border-base-300">
      {/*<h3 className="text-lg font-semibold">Controls</h3>*/}

      <div className="flex flex-col gap-2">
        <label className="label text-sm font-medium">Persona:</label>
        <input
          type="text"
          value={persona}
          onChange={(e) => setPersona(e.target.value)}
          className="input input-bordered w-full"
          placeholder="Enter persona"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="label text-sm font-medium">Job:</label>
        <input
          type="text"
          value={job}
          onChange={(e) => setJob(e.target.value)}
          className="input input-bordered w-full"
          placeholder="Enter job role"
        />
      </div>

      <button className="btn btn-primary mt-2" onClick={onAnalyze}>
        Analyze PDFs
      </button>

      {analysisResult?.summary && (
        <div className="mt-4 p-3 border rounded bg-base-100 max-h-60 overflow-y-auto">
          <h4 className="text-sm font-semibold mb-1">📄 Summary:</h4>
          <p className="text-xs whitespace-pre-line">
            {analysisResult.summary}
          </p>
        </div>
      )}
    </aside>
  );
}
