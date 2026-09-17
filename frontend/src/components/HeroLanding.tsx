import React, { useState, useRef } from 'react';
import { Upload, FileUp, Sparkles, Database, CheckCircle2, ShieldAlert, Cpu, ArrowRight, Table } from 'lucide-react';

interface HeroLandingProps {
  onFileSelected: (file: File) => void;
  onLoadDemo: () => void;
  isLoading: boolean;
}

export const HeroLanding: React.FC<HeroLandingProps> = ({
  onFileSelected,
  onLoadDemo,
  isLoading,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.csv') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        onFileSelected(file);
      } else {
        alert('Please upload a CSV or Excel file (.csv, .xlsx, .xls)');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-12 relative overflow-hidden">
      
      {/* Background Glows */}
      <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-indigo-600/20 via-purple-600/20 to-blue-500/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-4xl w-full text-center space-y-8 relative z-10">
        
        {/* Badge */}
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium backdrop-blur-md">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Generation Autonomous Data Remediation</span>
        </div>

        {/* Hero Title */}
        <div className="space-y-4">
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white">
            Clean, Standardize & Profile Data{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              with Autonomous AI
            </span>
          </h1>
          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-400 font-normal leading-relaxed">
            Fix malformed dates, negative ages, dirty phone numbers, outliers, casing anomalies,
            and missing values in seconds. Inspect distributions, correlation matrices, and deep insights.
          </p>
        </div>

        {/* Upload Card */}
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`p-10 rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-300 relative group glass-card ${
            isDragOver
              ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01]'
              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/60'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv, .xlsx, .xls"
            className="hidden"
          />

          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 group-hover:bg-indigo-500/20 transition-all duration-300 shadow-xl shadow-indigo-500/10">
              <Upload className="w-8 h-8" />
            </div>

            <div className="space-y-1">
              <p className="text-lg font-semibold text-white">
                Drop your CSV or Excel file here, or <span className="text-indigo-400 underline underline-offset-4">browse</span>
              </p>
              <p className="text-sm text-slate-400">
                Supports CSV, XLSX, and XLS with automated encoding & delimiter detection
              </p>
            </div>

            <div className="flex items-center space-x-6 text-xs text-slate-500 pt-2">
              <span className="flex items-center"><CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Automatic Type Inference</span>
              <span className="flex items-center"><CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Multi-Step Undo Stack</span>
              <span className="flex items-center"><CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Export to CSV, Excel, PDF</span>
            </div>
          </div>
        </div>

        {/* Demo Dataset CTA */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={onLoadDemo}
            disabled={isLoading}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-white font-medium text-sm flex items-center justify-center space-x-2.5 transition-all shadow-lg hover:border-slate-600 active:scale-95"
          >
            <Database className="w-4 h-4 text-purple-400" />
            <span>Load Sample Enterprise Dataset (250 Rows with Real Errors)</span>
            <ArrowRight className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Feature Highlights Grid */}
        <div className="pt-12 grid grid-cols-1 md:grid-cols-3 gap-5 text-left">
          <div className="p-5 rounded-xl glass-card">
            <div className="w-9 h-9 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-3">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white mb-1">Semantic Intelligence</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detects domain semantics (Age, Salary, Price, Email, Phone, Gender) and prevents non-sensical values like negative ages or invalid email structures.
            </p>
          </div>

          <div className="p-5 rounded-xl glass-card">
            <div className="w-9 h-9 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 mb-3">
              <Table className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white mb-1">Visual Diff & Audit Trail</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Side-by-side Before vs After view highlights modified cells with instant undo capability. Export comprehensive executive PDF audit reports.
            </p>
          </div>

          <div className="p-5 rounded-xl glass-card">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-3">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white mb-1">Interactive User Decision</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Choose your exact remediation policy per column: Winsorize outliers, flip negative signs, convert casing, or supply custom default values.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};
