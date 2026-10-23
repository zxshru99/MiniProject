"use client";

import React, { useState, useEffect } from "react";
import { X, Download, Copy, Check, ZoomIn, ZoomOut, RotateCcw } from "lucide-react";

interface ImageViewerModalProps {
  isOpen: boolean;
  imageUrl: string | null;
  prompt: string;
  modelName: string;
  aspectRatio: string;
  onClose: () => void;
}

export function ImageViewerModal({
  isOpen,
  imageUrl,
  prompt,
  modelName,
  aspectRatio,
  onClose,
}: ImageViewerModalProps) {
  const [copied, setCopied] = useState(false);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !imageUrl) return null;

  const handleDownload = async () => {
    try {
      if (imageUrl.startsWith("data:")) {
        const a = document.createElement("a");
        a.href = imageUrl;
        a.download = `agripredict-soil-${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      } else {
        const res = await fetch(imageUrl, { mode: "cors" });
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `agripredict-soil-${Date.now()}.jpg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch {
      window.open(imageUrl, "_blank");
    }
  };

  const handleCopy = async () => {
    try {
      if (imageUrl.startsWith("data:")) {
        const res = await fetch(imageUrl);
        const blob = await res.blob();
        await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
      } else {
        await navigator.clipboard.writeText(imageUrl);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      await navigator.clipboard.writeText(imageUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-6 bg-black/95 backdrop-blur-xl animate-in fade-in-0 duration-200"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full h-full max-w-6xl max-h-[90vh] flex flex-col items-center justify-between font-mono">
        {/* Top bar */}
        <div className="w-full flex items-center justify-between px-3 py-2 bg-black/60 border border-white/10 text-white z-10 backdrop-blur-md">
          <div className="flex items-center gap-2 truncate max-w-[60%]">
            <span className="text-xs font-bold text-gray-300">{modelName}</span>
            <span className="text-[10px] text-gray-500">•</span>
            <span className="text-[10px] text-gray-400 font-mono">{aspectRatio}</span>
            <span className="text-[10px] text-gray-500 hidden sm:inline">•</span>
            <span className="text-xs text-gray-300 truncate hidden sm:inline" title={prompt}>
              {prompt}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setZoom((z) => Math.min(z + 0.25, 2.5))}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setZoom((z) => Math.max(z - 0.25, 0.75))}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            {zoom !== 1 && (
              <button
                type="button"
                onClick={() => setZoom(1)}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                title="Reset Zoom (100%)"
              >
                <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
              </button>
            )}
            <button
              type="button"
              onClick={handleCopy}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1 text-xs"
              title="Copy to Clipboard"
            >
              {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
            </button>
            <button
              type="button"
              onClick={handleDownload}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1 text-xs"
              title="Download Image"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors ml-2"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Center image container */}
        <div className="flex-1 w-full flex items-center justify-center overflow-auto p-4 select-none">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageUrl}
            alt={prompt}
            style={{ transform: `scale(${zoom})`, transition: "transform 0.15s ease-out" }}
            className="max-h-[75vh] max-w-full object-contain shadow-2xl border border-white/10 rounded-sm"
          />
        </div>

        {/* Bottom prompt caption */}
        <div className="w-full text-center py-2 px-4 text-xs text-gray-400 bg-black/60 border-t border-white/10 truncate">
          {prompt}
        </div>
      </div>
    </div>
  );
}
