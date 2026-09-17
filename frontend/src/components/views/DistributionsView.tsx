import React, { useState } from 'react';
import { ColumnDistribution, NumericDistribution, CategoricalDistribution } from '../../types';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid, 
  Cell 
} from 'recharts';
import { TrendingUp, AlertCircle, BarChart2, PieChart } from 'lucide-react';

interface DistributionsViewProps {
  distributions: Record<string, ColumnDistribution>;
}

export const DistributionsView: React.FC<DistributionsViewProps> = ({ distributions }) => {
  const columnNames = Object.keys(distributions);
  const [selectedColumn, setSelectedColumn] = useState<string>(columnNames[0] || '');

  if (columnNames.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400">
        <BarChart2 className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No distribution metrics available for this dataset.</p>
      </div>
    );
  }

  const currentDist = distributions[selectedColumn] || distributions[columnNames[0]];

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header & Column Selector */}
      <div className="glass-card rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <BarChart2 className="w-5 h-5 text-indigo-400" />
            <span>Interactive Data Distributions & Skewness</span>
          </h2>
          <p className="text-xs text-slate-400">
            Inspect statistical spreads, histogram frequency bins, outlier tails, and category balances.
          </p>
        </div>

        {/* Column Selector */}
        <div className="w-full sm:w-72">
          <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Select Column
          </label>
          <select
            value={selectedColumn}
            onChange={(e) => setSelectedColumn(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2 font-mono focus:outline-none focus:border-indigo-500"
          >
            {columnNames.map((col) => (
              <option key={col} value={col}>
                {col} ({distributions[col].kind === 'numeric' ? 'Numeric' : 'Categorical'})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Distribution Content */}
      {currentDist && currentDist.kind === 'numeric' && (
        <NumericDistCard column={selectedColumn} data={currentDist as NumericDistribution} />
      )}

      {currentDist && currentDist.kind === 'categorical' && (
        <CategoricalDistCard column={selectedColumn} data={currentDist as CategoricalDistribution} />
      )}

      {/* Grid of all distributions preview */}
      <div className="pt-4 space-y-4">
        <h3 className="text-base font-bold text-white">All Columns Distribution Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {columnNames.map((col) => {
            const dist = distributions[col];
            return (
              <div
                key={col}
                onClick={() => setSelectedColumn(col)}
                className={`p-4 rounded-xl glass-card cursor-pointer transition-all border ${
                  selectedColumn === col
                    ? 'border-indigo-500 bg-indigo-500/10'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-semibold text-slate-200 truncate max-w-[180px]">
                    {col}
                  </span>
                  <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {dist.kind}
                  </span>
                </div>

                {dist.kind === 'numeric' ? (
                  <div className="h-24 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dist.bins}>
                        <Bar dataKey="count" fill="#6366f1" radius={[2, 2, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-24 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dist.categories} layout="vertical">
                        <Bar dataKey="count" fill="#ec4899" radius={[0, 2, 2, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};

const NumericDistCard: React.FC<{ column: string; data: NumericDistribution }> = ({ column, data }) => {
  const { stats, bins } = data;
  const isSkewed = Math.abs(stats.skew) > 1.0;

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider">Numeric Column</span>
          <h3 className="text-xl font-bold font-mono text-white">{column}</h3>
        </div>

        {/* Skewness Badge */}
        <div className={`px-3 py-1.5 rounded-xl border flex items-center space-x-2 text-xs ${
          isSkewed 
            ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' 
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
        }`}>
          <TrendingUp className="w-3.5 h-3.5" />
          <span>
            Skewness: <b>{stats.skew}</b> ({isSkewed ? (stats.skew > 0 ? 'Right-Skewed Tail' : 'Left-Skewed Tail') : 'Normal Distribution'})
          </span>
        </div>
      </div>

      {/* Main Chart */}
      <div className="h-72 w-full bg-slate-900/40 rounded-xl p-4 border border-slate-800/80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={bins}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="range" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#94a3b8' }}
              itemStyle={{ color: '#818cf8' }}
            />
            <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Quick Summary Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block uppercase font-semibold">Min</span>
          <span className="text-sm font-bold text-slate-200 font-mono">{stats.min}</span>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block uppercase font-semibold">Mean</span>
          <span className="text-sm font-bold text-slate-200 font-mono">{stats.mean}</span>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block uppercase font-semibold">Median</span>
          <span className="text-sm font-bold text-indigo-400 font-mono">{stats.median}</span>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block uppercase font-semibold">Max</span>
          <span className="text-sm font-bold text-slate-200 font-mono">{stats.max}</span>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block uppercase font-semibold">Std Dev</span>
          <span className="text-sm font-bold text-slate-200 font-mono">{stats.std}</span>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-[10px] text-slate-500 block uppercase font-semibold">Imputation Advice</span>
          <span className="text-xs font-semibold text-slate-300">
            {isSkewed ? 'Use Median' : 'Use Mean'}
          </span>
        </div>
      </div>
    </div>
  );
};

const CategoricalDistCard: React.FC<{ column: string; data: CategoricalDistribution }> = ({ column, data }) => {
  const { categories, total_unique } = data;
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#10b981', '#06b6d4'];

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[11px] font-semibold text-pink-400 uppercase tracking-wider">Categorical Column</span>
          <h3 className="text-xl font-bold font-mono text-white">{column}</h3>
        </div>
        <span className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
          {total_unique} Unique Categories
        </span>
      </div>

      <div className="h-72 w-full bg-slate-900/40 rounded-xl p-4 border border-slate-800/80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={categories} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis type="number" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis type="category" dataKey="label" stroke="#94a3b8" fontSize={11} tickLine={false} width={100} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {categories.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex flex-wrap gap-2">
        {categories.map((cat, idx) => (
          <div key={cat.label} className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs flex items-center space-x-2">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: colors[idx % colors.length] }} />
            <span className="text-slate-300 font-mono">{cat.label}:</span>
            <span className="font-bold text-white">{cat.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
