import React, { useState } from 'react';
import { CompareResponse } from '../../types';
import { GitCompare, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';

interface BeforeAfterViewProps {
  compareData: CompareResponse | null;
}

export const BeforeAfterView: React.FC<BeforeAfterViewProps> = ({ compareData }) => {
  const [onlyChanged, setOnlyChanged] = useState(true);

  if (!compareData) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400">
        <GitCompare className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>Comparison data unavailable. Run cleaning actions first.</p>
      </div>
    );
  }

  const { stats, diff_sample } = compareData;
  const filteredRows = onlyChanged ? diff_sample.filter((r) => r.has_diff) : diff_sample;

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header & Stats Cards */}
      <div className="glass-card rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <GitCompare className="w-5 h-5 text-indigo-400" />
            <span>Side-by-Side Visual Diff & Audit</span>
          </h2>
          <p className="text-xs text-slate-400">
            Compare raw original data vs cleaned dataset state. Modified cells are highlighted in yellow.
          </p>
        </div>

        <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-xl">
          <input
            type="checkbox"
            checked={onlyChanged}
            onChange={(e) => setOnlyChanged(e.target.checked)}
            className="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-950"
          />
          <span>Show Modified Rows Only</span>
        </label>
      </div>

      {/* Metric Delta Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Rows (Before → After)</span>
          <p className="text-xl font-bold text-white font-mono flex items-center space-x-1.5">
            <span>{stats.rows_before}</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
            <span className={stats.rows_delta < 0 ? 'text-rose-400' : 'text-emerald-400'}>{stats.rows_after}</span>
          </p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Columns (Before → After)</span>
          <p className="text-xl font-bold text-white font-mono flex items-center space-x-1.5">
            <span>{stats.columns_before}</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
            <span>{stats.columns_after}</span>
          </p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Modified Cells (Sample)</span>
          <p className="text-xl font-bold text-amber-400 font-mono">
            {stats.diff_cells_in_sample}
          </p>
        </div>

        <div className="glass-card p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Rows Modified in Sample</span>
          <p className="text-xl font-bold text-indigo-400 font-mono">
            {diff_sample.filter((r) => r.has_diff).length} / {diff_sample.length}
          </p>
        </div>
      </div>

      {/* Diff Table */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">
            Cell-Level Modifications ({filteredRows.length} Rows Displayed)
          </h3>
          <span className="text-[11px] text-slate-500">
            Yellow indicates values transformed or imputed during cleaning
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800 max-h-[500px]">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead className="bg-slate-900/90 text-slate-300 font-semibold sticky top-0 border-b border-slate-800 z-10">
              <tr>
                <th className="py-2.5 px-3 w-12 text-slate-500">Row</th>
                <th className="py-2.5 px-3 w-20 text-center">Status</th>
                {stats.common_columns.map((col) => (
                  <th key={col} className="py-2.5 px-4 font-mono">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filteredRows.map((row) => (
                <tr key={row.row_index} className="hover:bg-slate-900/30">
                  <td className="py-2 px-3 text-slate-500 font-mono text-[11px]">{row.row_index + 1}</td>
                  <td className="py-2 px-3 text-center">
                    {row.has_diff ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        Modified
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400">
                        Identical
                      </span>
                    )}
                  </td>
                  {stats.common_columns.map((col) => {
                    const field = row.fields[col];
                    if (!field) return <td key={col} className="py-2 px-4 text-slate-600">—</td>;

                    if (field.changed) {
                      return (
                        <td key={col} className="py-2 px-4 bg-amber-500/10 font-mono">
                          <div className="flex items-center space-x-1.5">
                            <span className="line-through text-slate-500 text-[11px]">{field.before}</span>
                            <span className="text-slate-400">→</span>
                            <span className="text-amber-300 font-bold">{field.after}</span>
                          </div>
                        </td>
                      );
                    }

                    return (
                      <td key={col} className="py-2 px-4 text-slate-300 font-mono">
                        {field.after}
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
