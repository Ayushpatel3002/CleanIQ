import React, { useState } from 'react';
import { 
  DatasetSummary, 
  DatasetPreview, 
  ColumnIntelligence 
} from '../../types';
import { 
  Layers, 
  Hash, 
  AlertTriangle, 
  Copy, 
  HardDrive, 
  Binary, 
  Type, 
  Calendar, 
  Search, 
  CheckCircle2, 
  HelpCircle 
} from 'lucide-react';

interface OverviewViewProps {
  summary: DatasetSummary;
  healthScore: number;
  healthLabel: string;
  preview: DatasetPreview;
  columnsAnalysis: ColumnIntelligence[];
  onGoToSmartClean: () => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  summary,
  healthScore,
  healthLabel,
  preview,
  columnsAnalysis,
  onGoToSmartClean,
}) => {
  const [searchFilter, setSearchFilter] = useState('');

  const filteredColumns = columnsAnalysis.filter((c) =>
    c.Column.toLowerCase().includes(searchFilter.toLowerCase()) ||
    c.Recommendation.toLowerCase().includes(searchFilter.toLowerCase())
  );

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'from-emerald-500 to-teal-600 border-emerald-500/30 text-emerald-400';
    if (score >= 60) return 'from-amber-500 to-orange-600 border-amber-500/30 text-amber-400';
    return 'from-rose-500 to-red-600 border-rose-500/30 text-rose-400';
  };

  return (
    <div className="space-y-8 pb-12">

      {/* Health Score Hero Banner */}
      <div className="glass-card rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
        <div className="space-y-2 text-center md:text-left z-10">
          <div className="flex items-center justify-center md:justify-start space-x-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Dataset Health Index</span>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-800 text-slate-300">
              {healthLabel}
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Overall Quality Score: <span className={healthScore >= 80 ? 'text-emerald-400' : healthScore >= 60 ? 'text-amber-400' : 'text-rose-400'}>{healthScore}/100</span>
          </h2>
          <p className="text-sm text-slate-400 max-w-xl">
            {healthScore >= 80
              ? 'Your dataset is in great shape with minimal nulls, healthy distributions, and clean values.'
              : healthScore >= 60
              ? 'Moderate data quality issues identified. Automated or user-directed remediation is recommended.'
              : 'Severe anomalies detected (negatives in non-negative domains, extreme outliers, or heavy missingness). Use Smart Clean to fix.'}
          </p>
        </div>

        <div className="flex items-center gap-4 z-10">
          {/* Circular Score Visual */}
          <div className="relative w-24 h-24 flex items-center justify-center">
            <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-slate-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={healthScore >= 80 ? 'text-emerald-500' : healthScore >= 60 ? 'text-amber-500' : 'text-rose-500'}
                strokeDasharray={`${healthScore}, 100`}
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute text-center">
              <span className="text-xl font-black text-white">{Math.round(healthScore)}%</span>
            </div>
          </div>

          <button
            onClick={onGoToSmartClean}
            className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition-all hover:scale-105"
          >
            Launch Smart Clean
          </button>
        </div>
      </div>

      {/* Key Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Rows</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white">{summary.Rows?.toLocaleString()}</p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Columns</span>
            <Hash className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-white">{summary.Columns}</p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Missing Values</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-white">
            {summary["Missing Values"]?.toLocaleString()}
            <span className="text-xs font-normal text-slate-400 ml-1.5">({summary["Missing %"] ?? 0}%)</span>
          </p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Duplicate Rows</span>
            <Copy className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-white">{summary["Duplicate Rows"]?.toLocaleString()}</p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Memory Footprint</span>
            <HardDrive className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-bold text-white">{summary["Memory Usage (MB)"]} <span className="text-xs font-normal text-slate-400">MB</span></p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Numeric Columns</span>
            <Binary className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-white">{summary["Numeric Columns"]}</p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Categorical</span>
            <Type className="w-4 h-4 text-pink-400" />
          </div>
          <p className="text-2xl font-bold text-white">{summary["Categorical Columns"]}</p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Datetime Fields</span>
            <Calendar className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white">{summary["Datetime Columns"]}</p>
        </div>
      </div>

      {/* Column Intelligence Table */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-white">AI Column Intelligence & Audit</h3>
            <p className="text-xs text-slate-400">
              Automated detection of Primary Keys, Phone numbers, Dates, Emails, and severe missingness.
            </p>
          </div>
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search columns or recommendation..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800/80">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Column Name</th>
                <th className="py-3 px-4">Data Type</th>
                <th className="py-3 px-4">Missing Values</th>
                <th className="py-3 px-4">Missing %</th>
                <th className="py-3 px-4">Unique Values</th>
                <th className="py-3 px-4">AI Audit Recommendation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredColumns.map((col, idx) => {
                const isHealthy = col.Recommendation.includes('Healthy');
                return (
                  <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">{col.Column}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 font-mono text-[11px]">
                        {col["Data Type"]}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{col["Missing Values"]}</td>
                    <td className="py-3 px-4">
                      <span className={`font-medium ${col["Missing Values"] > 0 ? 'text-amber-400' : 'text-slate-400'}`}>
                        {col["Missing %"]}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{col["Unique Values"]}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-[11px] font-medium border ${
                        isHealthy
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                        {col.Recommendation}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dataset Preview Grid */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">Live Data Preview</h3>
            <p className="text-xs text-slate-400">
              Showing sample of first {preview.rows.length} records out of {preview.total_rows.toLocaleString()} rows.
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-400">
            {preview.total_columns} Columns
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800/80 max-h-96">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead className="bg-slate-900/90 text-slate-300 font-semibold sticky top-0 border-b border-slate-800 z-10">
              <tr>
                <th className="py-2.5 px-3 w-12 text-slate-500">#</th>
                {preview.columns.map((col) => (
                  <th key={col} className="py-2.5 px-4 font-mono">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {preview.rows.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-slate-900/40">
                  <td className="py-2 px-3 text-slate-500 font-mono text-[11px]">{rIdx + 1}</td>
                  {preview.columns.map((col) => {
                    const val = row[col];
                    const isNull = val === null || val === undefined;
                    return (
                      <td key={col} className="py-2 px-4">
                        {isNull ? (
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-300 font-mono">
                            null
                          </span>
                        ) : (
                          <span className="text-slate-300">{String(val)}</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
