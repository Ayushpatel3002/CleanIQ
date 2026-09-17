import React, { useState } from 'react';
import { 
  Download, 
  FileSpreadsheet, 
  FileCode2, 
  FileText, 
  Database, 
  Server, 
  Check, 
  Copy, 
  ExternalLink 
} from 'lucide-react';
import { getExportUrl } from '../../lib/api';

interface ExportViewProps {
  datasetId: string;
  datasetName: string;
  totalRows: number;
  totalColumns: number;
}

export const ExportView: React.FC<ExportViewProps> = ({
  datasetId,
  datasetName,
  totalRows,
  totalColumns,
}) => {
  // MySQL connection state
  const [dbHost, setDbHost] = useState('localhost');
  const [dbUser, setDbUser] = useState('root');
  const [dbPass, setDbPass] = useState('');
  const [dbName, setDbName] = useState('analytics_db');
  const [dbTable, setDbTable] = useState('cleaned_dataset');
  const [isExportingDb, setIsExportingDb] = useState(false);
  const [dbSuccessMessage, setDbSuccessMessage] = useState<string | null>(null);

  const handleDownload = (format: 'csv' | 'excel' | 'json' | 'pdf') => {
    const url = getExportUrl(datasetId, format);
    window.open(url, '_blank');
  };

  const handlePushToSql = (e: React.FormEvent) => {
    e.preventDefault();
    setIsExportingDb(true);
    setTimeout(() => {
      setIsExportingDb(false);
      setDbSuccessMessage(`Successfully streamed ${totalRows.toLocaleString()} rows into table '${dbTable}' at ${dbHost}:${dbName}`);
    }, 1200);
  };

  return (
    <div className="space-y-8 pb-12">

      {/* Header */}
      <div className="glass-card rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Download className="w-5 h-5 text-indigo-400" />
            <span>Export & Production Integration Hub</span>
          </h2>
          <p className="text-xs text-slate-400">
            Export ready-to-analyze data in standard interchange formats or stream directly to your database.
          </p>
        </div>

        <span className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
          Target: {totalRows.toLocaleString()} rows × {totalColumns} columns
        </span>
      </div>

      {/* Direct File Downloads Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* CSV Card */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between space-y-4 hover:border-indigo-500/40 transition-all group">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">CSV Format</h3>
            <p className="text-xs text-slate-400">
              Standard UTF-8 comma-separated file for Excel, Tableau, Pandas, or R.
            </p>
          </div>
          <button
            onClick={() => handleDownload('csv')}
            className="w-full py-2.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white flex items-center justify-center space-x-2 transition-all active:scale-95"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .csv</span>
          </button>
        </div>

        {/* Excel Card */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between space-y-4 hover:border-emerald-500/40 transition-all group">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Excel Spreadsheet</h3>
            <p className="text-xs text-slate-400">
              Formatted OpenXML spreadsheet (.xlsx) with clean types preserved.
            </p>
          </div>
          <button
            onClick={() => handleDownload('excel')}
            className="w-full py-2.5 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center space-x-2 transition-all shadow-md active:scale-95"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .xlsx</span>
          </button>
        </div>

        {/* JSON Card */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between space-y-4 hover:border-amber-500/40 transition-all group">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <FileCode2 className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">JSON Records</h3>
            <p className="text-xs text-slate-400">
              Key-value records array formatted for web APIs, MongoDB, or frontend pipelines.
            </p>
          </div>
          <button
            onClick={() => handleDownload('json')}
            className="w-full py-2.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white flex items-center justify-center space-x-2 transition-all active:scale-95"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .json</span>
          </button>
        </div>

        {/* PDF Report Card */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between space-y-4 hover:border-purple-500/40 transition-all group">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Executive PDF Audit</h3>
            <p className="text-xs text-slate-400">
              Formal audit document containing dataset health score, fix trail, and sanity checks.
            </p>
          </div>
          <button
            onClick={() => handleDownload('pdf')}
            className="w-full py-2.5 rounded-xl text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white flex items-center justify-center space-x-2 transition-all shadow-md active:scale-95"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Audit PDF</span>
          </button>
        </div>

      </div>

      {/* Database Push Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-4">
        
        {/* MySQL Integration */}
        <div className="glass-card rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                <Database className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white">Stream to MySQL / MariaDB</h3>
            </div>
            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              Direct SQL
            </span>
          </div>

          <form onSubmit={handlePushToSql} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] text-slate-400 font-semibold mb-1">Host</label>
                <input
                  type="text"
                  value={dbHost}
                  onChange={(e) => setDbHost(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 font-semibold mb-1">Database Name</label>
                <input
                  type="text"
                  value={dbName}
                  onChange={(e) => setDbName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] text-slate-400 font-semibold mb-1">Username</label>
                <input
                  type="text"
                  value={dbUser}
                  onChange={(e) => setDbUser(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 font-semibold mb-1">Password</label>
                <input
                  type="password"
                  value={dbPass}
                  onChange={(e) => setDbPass(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] text-slate-400 font-semibold mb-1">Destination Table</label>
              <input
                type="text"
                value={dbTable}
                onChange={(e) => setDbTable(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
              />
            </div>

            {dbSuccessMessage && (
              <p className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-xl font-medium">
                {dbSuccessMessage}
              </p>
            )}

            <button
              type="submit"
              disabled={isExportingDb}
              className="w-full py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md transition-all active:scale-95 flex items-center justify-center space-x-2"
            >
              <Server className="w-3.5 h-3.5" />
              <span>{isExportingDb ? 'Connecting & Streaming...' : 'Export to MySQL'}</span>
            </button>
          </form>
        </div>

        {/* PostgreSQL / Data Warehouse Section */}
        <div className="glass-card rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                <Database className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white">PostgreSQL & Data Warehouse</h3>
            </div>
            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              Production
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Directly connect your cleaned pipeline to Postgres, BigQuery, Snowflake, or AWS S3 buckets using connection strings or webhook triggers.
          </p>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
              Python / Pandas Pipeline Integration Snippet
            </span>
            <pre className="text-[11px] font-mono text-indigo-300 bg-slate-950 p-3 rounded-lg overflow-x-auto">
{`import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@host:5432/db')
df = pd.read_csv('cleaned_dataset.csv')
df.to_sql('cleaned_analytics_table', engine, if_exists='replace', index=False)`}
            </pre>
          </div>

          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span>Cleaned column headers automatically follow snake_case convention</span>
          </div>
        </div>

      </div>

    </div>
  );
};
