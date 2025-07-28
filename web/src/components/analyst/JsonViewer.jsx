import React, { useRef } from "react";

function syntaxHighlight(json) {
  // Always pretty-print the JSON with indentation
  let jsonString;
  if (typeof json === "string") {
    try {
      jsonString = JSON.stringify(JSON.parse(json), null, 2);
    } catch {
      // If not valid JSON string, fallback to original string
      jsonString = json;
    }
  } else {
    jsonString = JSON.stringify(json, null, 2);
  }
  jsonString = jsonString
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return jsonString.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g,
    function (match) {
      let cls = "text-base-content";
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = "text-info font-semibold";
        } else {
          cls = "text-neutral";
        }
      } else if (/true|false/.test(match)) {
        cls = "text-primary font-bold";
      } else if (/null/.test(match)) {
        cls = "text-error";
      } else if (/^-?\d+/.test(match)) {
        cls = "text-info";
      }
      return `<span class="${cls}">${match}</span>`;
    }
  );
}

export default function JsonViewer({ data }) {
  const downloadRef = useRef();

  // Always pretty-print for download
  let prettyJson;
  if (typeof data === "string") {
    try {
      prettyJson = JSON.stringify(JSON.parse(data), null, 2);
    } catch {
      prettyJson = data;
    }
  } else {
    prettyJson = JSON.stringify(data, null, 2);
  }

  const handleDownload = () => {
    const blob = new Blob([prettyJson], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "analysis_result.json";
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 0);
  };

  return (
    <div className="flex flex-col gap-2">
      <button
        className="btn btn-sm btn-outline self-end mb-1"
        onClick={handleDownload}
        ref={downloadRef}
        title="Download JSON"
      >
        Download JSON
      </button>
      <pre
        className="bg-base-100 rounded-lg p-4 overflow-x-auto text-xs font-mono border border-base-300"
        dangerouslySetInnerHTML={{ __html: syntaxHighlight(data) }}
      />
    </div>
  );
}
