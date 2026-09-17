import React from 'react';
import { Sparkles, RotateCcw, Undo2, Zap, FileSpreadsheet, RefreshCw } from 'lucide-react';
import { DatasetSummary } from '../types';

interface NavbarProps {
  datasetName: string | null;
  healthScore: number | null;
  healthLabel: string | null;
  canUndo: boolean;
  onUndo: () => void;
  onReset: () => void;
  onAutoClean: () => void;
  onNewUpload: () => void;
  isLoading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  datasetName,
  healthScore,
  healthLabel,
  canUndo,
  onUndo,
  onReset,
  onAutoClean,
  onNewUpload,
  isLoading,
}) => {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={onNewUpload}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <span className="text-xl">🧹</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                CleanIQ
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                PRO 2.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400">AI Data Cleaning & Intelligence</p>
          </div>
        </div>

        {/* Dataset Status & Global Actions */}
        {datasetName && (
          <div className="flex items-center space-x-3">
            {/* Active File Badge */}
            <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <FileSpreadsheet className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-medium max-w-[160px] truncate">{datasetName}</span>
            </div>

            {/* Health Score Pill */}
            {healthScore !== null && (
              <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
                <span className="text-slate-400">Health:</span>
                <span className={`font-bold ${
                  healthScore >= 80 ? 'text-emerald-400' : healthScore >= 60 ? 'text-amber-400' : 'text-rose-400'
                }`}>
                  {healthScore}/100
                </span>
                <span className="text-slate-500 text-[10px]">({healthLabel})</span>
              </div>
            )}

            {/* Undo */}
            <button
              onClick={onUndo}
              disabled={!canUndo || isLoading}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                canUndo && !isLoading
                  ? 'bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800 hover:border-slate-600'
                  : 'bg-slate-950 border-slate-850 text-slate-600 cursor-not-allowed border-slate-800/50'
              }`}
              title="Undo last applied action"
            >
              <Undo2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Undo</span>
            </button>

            {/* Reset */}
            <button
              onClick={onReset}
              disabled={isLoading}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
              title="Reset to raw uploaded file"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Reset</span>
            </button>

            {/* 1-Click Auto Clean */}
            <button
              onClick={onAutoClean}
              disabled={isLoading}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20 hover:from-indigo-600 hover:to-purple-700 transition-all active:scale-95"
            >
              <Zap className="w-3.5 h-3.5 fill-white" />
              <span>Auto-Clean</span>
            </button>

            {/* New File */}
            <button
              onClick={onNewUpload}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Upload new dataset"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        )}

      </div>
    </header>
  );
};
