import React, { useEffect, useRef } from "react";
import ViewSDKClient from "../../ViewSDKClient";

export default function PdfTabs({ pdfFiles, activeIdx, setActiveIdx }) {
  const pdfUrl = pdfFiles[activeIdx]?.url;
  const pdfDivRef = useRef();
  const viewSDKClientRef = useRef();
  const previewPromiseRef = useRef();

  // Load PDF when pdfUrl changes
  useEffect(() => {
    if (pdfUrl && pdfDivRef.current) {
      const viewSDKClient = new ViewSDKClient();
      viewSDKClientRef.current = viewSDKClient;
      viewSDKClient.ready().then(() => {
        const promise = viewSDKClient.previewFile(
          pdfDivRef.current.id,
          {
            showAnnotationTools: true,
            showLeftHandPanel: true,
            showPageControls: true,
            showDownloadPDF: true,
            showPrintPDF: true,
            //embedMode: "SIZED_CONTAINER", // Enable getAPIs
          },
          pdfUrl,
        );
        previewPromiseRef.current = promise;
      });
    }
  }, [pdfUrl]);

  // Listen for "pdf-goto-page" event to jump to a page
  useEffect(() => {
    const handler = (e) => {
      const pageNum = e.detail?.pageNum;
      if (
        pageNum &&
        viewSDKClientRef.current &&
        viewSDKClientRef.current.adobeDCView
      ) {
        // Wait for previewFile to resolve, then get APIs
        const previewPromise = previewPromiseRef.current;
        if (previewPromise && typeof previewPromise.then === "function") {
          previewPromise.then(() => {
            viewSDKClientRef.current.adobeDCView.getAPIs().then((apis) => {
              apis.gotoLocation({ pageNumber: pageNum });
            });
          });
        }
      }
    };
    window.addEventListener("pdf-goto-page", handler);
    return () => window.removeEventListener("pdf-goto-page", handler);
  }, []);

  return (
    <div className="flex flex-col h-full max-w-[70vw] w-full m-auto">
      <div
        role="tablist"
        className="tabs tabs-lift mb-2 overflow-x-auto whitespace-nowrap flex-nowrap scrollbar-thin scrollbar-thumb-base-300 scrollbar-track-base-100"
        style={{ WebkitOverflowScrolling: "touch" }}
      >
        {pdfFiles.map((file, idx) => (
          <a
            role="tab"
            key={file.name}
            className={`text-wrap tab ${activeIdx === idx ? "tab-active" : ""}`}
            onClick={() => setActiveIdx(idx)}
            style={{
              textOverflow: "ellipsis",
            }}
            title={file.name}
          >
            <div className="line-clamp-1">{file.name}</div>
          </a>
        ))}
      </div>
      <div className="flex-1 bg-base-200 rounded-lg p-2">
        <div id="pdf-div" ref={pdfDivRef} className="w-full h-full" />
      </div>
    </div>
  );
}
