import React, { useState } from 'react';
import { ColumnPlan, IssueItem } from '../../types';
import { 
  Sparkles, 
  Search, 
  Replace, 
  Check, 
  Clock, 
  AlertCircle, 
  Sliders, 
  ChevronDown, 
  ChevronUp, 
  CornerDownRight, 
  CheckCircle2 
} from 'lucide-react';

interface SmartCleanViewProps {
  plan: ColumnPlan[];
  fixLog: any[];
  onApplyFix: (data: { column: string; issue_type: string; fix_action: string; custom_value?: string }) => void;
  onFindReplace: (data: { find_value: string; replace_value: string; columns?: string[]; is_regex?: boolean; match_case?: boolean }) => void;
  isLoading: boolean;
}

export const SmartCleanView: React.FC<SmartCleanViewProps> = ({
  plan,
  fixLog,
  onApplyFix,
  onFindReplace,
  isLoading,
}) => {
  // State for user fix selections: key -> fix_action
  const [selectedFixes, setSelectedFixes] = useState<Record<string, string>>({});
  // State for custom values: key -> string
  const [customValues, setCustomValues] = useState<Record<string, string>>({});
  
  // Find & Replace form state
  const [showFindReplace, setShowFindReplace] = useState(false);
  const [findVal, setFindVal] = useState('');
  const [replaceVal, setReplaceVal] = useState('');
  const [targetCol, setTargetCol] = useState('__ALL__');
  const [isRegex, setIsRegex] = useState(false);
  const [matchCase, setMatchCase] = useState(false);

  const columnsWithIssues = plan.filter((p) => p.has_issues);
  const cleanColumns = plan.filter((p) => !p.has_issues);

  const handleFixChange = (key: string, action: string) => {
    setSelectedFixes((prev) => ({ ...prev, [key]: action }));
  };

  const handleCustomValChange = (key: string, val: string) => {
    setCustomValues((prev) => ({ ...prev, [key]: val }));
  };

  const handleApplySingle = (col: string, issue: IssueItem) => {
    const key = `${col}_${issue.type}`;
    const action = selectedFixes[key] || issue.default_fix;
    const custom = customValues[key];

    onApplyFix({
      column: col,
      issue_type: issue.type,
      fix_action: action,
      custom_value: custom,
    });
  };

  const handleApplyAllDefaultFixes = () => {
    columnsWithIssues.forEach((colPlan) => {
      colPlan.issues.forEach((issue) => {
        const key = `${colPlan.column}_${issue.type}`;
        const action = selectedFixes[key] || issue.default_fix;
        if (action !== 'keep') {
          onApplyFix({
            column: colPlan.column,
            issue_type: issue.type,
            fix_action: action,
            custom_value: customValues[key],
          });
        }
      });
    });
  };

  const submitFindReplace = (e: React.FormEvent) => {
    e.preventDefault();
    if (!findVal) return;
    onFindReplace({
      find_value: findVal,
      replace_value: replaceVal,
      columns: targetCol === '__ALL__' ? undefined : [targetCol],
      is_regex: isRegex,
      match_case: matchCase,
    });
    setFindVal('');
    setReplaceVal('');
  };

  return (
    <div className="space-y-8 pb-12">

      {/* Header & Quick Action Toolbar */}
      <div className="glass-card rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <span>Interactive AI Remediation Engine</span>
          </h2>
          <p className="text-xs text-slate-400">
            Select remediation policies per column or accept the AI recommended default action.
          </p>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <button
            onClick={() => setShowFindReplace(!showFindReplace)}
            className="flex-1 sm:flex-none px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-700 text-slate-200 hover:bg-slate-800 transition-all flex items-center justify-center space-x-2"
          >
            <Replace className="w-3.5 h-3.5 text-indigo-400" />
            <span>Find & Replace</span>
          </button>

          {columnsWithIssues.length > 0 && (
            <button
              onClick={handleApplyAllDefaultFixes}
              disabled={isLoading}
              className="flex-1 sm:flex-none px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25 transition-all whitespace-nowrap"
            >
              Apply All Recommended Fixes
            </button>
          )}
        </div>
      </div>

      {/* Find & Replace Drawer */}
      {showFindReplace && (
        <form onSubmit={submitFindReplace} className="glass-card rounded-2xl p-6 border-indigo-500/30 bg-indigo-950/20 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Replace className="w-4 h-4 text-indigo-400" />
              <span>Global Find & Replace Utility</span>
            </h3>
            <span className="text-[11px] text-slate-400">Replace dirty placeholders like 'N/A', '?', or typos</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Find Value
              </label>
              <input
                type="text"
                value={findVal}
                onChange={(e) => setFindVal(e.target.value)}
                placeholder="e.g. N/A, -999, unknown"
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Replace With
              </label>
              <input
                type="text"
                value={replaceVal}
                onChange={(e) => setReplaceVal(e.target.value)}
                placeholder="e.g. null, 0, or new text"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Target Columns
              </label>
              <select
                value={targetCol}
                onChange={(e) => setTargetCol(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
              >
                <option value="__ALL__">All Columns</option>
                {plan.map((p) => (
                  <option key={p.column} value={p.column}>
                    {p.column}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center space-x-4 text-xs text-slate-400">
              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isRegex}
                  onChange={(e) => setIsRegex(e.target.checked)}
                  className="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-900"
                />
                <span>Regex pattern</span>
              </label>
              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={matchCase}
                  onChange={(e) => setMatchCase(e.target.checked)}
                  className="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-900"
                />
                <span>Match Case</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading || !findVal}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md transition-all"
            >
              Execute Replacement
            </button>
          </div>
        </form>
      )}

      {/* Columns with Issues Grid */}
      {columnsWithIssues.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center text-slate-300 space-y-3">
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
            <Check className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Zero Anomalies Remaining!</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            All detected issues have been resolved. You can inspect the Before vs After diff or proceed to Export.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Columns Requiring Remediation ({columnsWithIssues.length})
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {columnsWithIssues.map((colPlan) => {
              return (
                <div key={colPlan.column} className="glass-card rounded-2xl p-5 space-y-4 border-slate-800">
                  
                  {/* Column Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                    <div className="flex items-center space-x-3">
                      <span className="font-mono text-base font-bold text-white">{colPlan.column}</span>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                        {colPlan.semantic_label}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">({colPlan.dtype})</span>
                    </div>

                    <div className="flex items-center space-x-3 text-xs text-slate-400">
                      <span>Missing: <b>{colPlan.missing}</b></span>
                      <span>•</span>
                      <span>Unique: <b>{colPlan.unique}</b></span>
                    </div>
                  </div>

                  {/* Issues List for this column */}
                  <div className="space-y-3">
                    {colPlan.issues.map((issue) => {
                      const key = `${colPlan.column}_${issue.type}`;
                      const currentAction = selectedFixes[key] || issue.default_fix;
                      const isCustom = currentAction === 'fill_custom';

                      return (
                        <div key={issue.type} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                            <div>
                              <span className="text-xs font-bold text-amber-400 block mb-0.5">
                                ⚠️ {issue.description}
                              </span>
                              {issue.sample_bad && issue.sample_bad.length > 0 && (
                                <p className="text-[11px] text-slate-500 font-mono truncate max-w-md">
                                  Sample erroneous values: {issue.sample_bad.map((s) => String(s)).join(', ')}
                                </p>
                              )}
                            </div>

                            {/* Dropdown Action Selector */}
                            <div className="flex items-center space-x-2 w-full md:w-auto">
                              <select
                                value={currentAction}
                                onChange={(e) => handleFixChange(key, e.target.value)}
                                className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2 font-medium focus:outline-none focus:border-indigo-500 max-w-xs"
                              >
                                {issue.fix_options.map(([code, label]) => (
                                  <option key={code} value={code}>
                                    {label} {code === issue.default_fix ? '(AI Recommended)' : ''}
                                  </option>
                                ))}
                              </select>

                              <button
                                onClick={() => handleApplySingle(colPlan.column, issue)}
                                disabled={isLoading}
                                className="px-3 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow transition-all whitespace-nowrap"
                              >
                                Apply
                              </button>
                            </div>
                          </div>

                          {/* Custom Value Input */}
                          {isCustom && (
                            <div className="flex items-center space-x-2 pt-2 border-t border-slate-800">
                              <CornerDownRight className="w-3.5 h-3.5 text-indigo-400" />
                              <span className="text-xs text-slate-400">Specify Value:</span>
                              <input
                                type="text"
                                value={customValues[key] || ''}
                                onChange={(e) => handleCustomValChange(key, e.target.value)}
                                placeholder="Enter custom replacement..."
                                className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                              />
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Clean Columns Accordeon */}
      {cleanColumns.length > 0 && (
        <div className="glass-card rounded-2xl p-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center space-x-2 mb-3">
            <CheckCircle2 className="w-4 h-4" />
            <span>Healthy Columns ({cleanColumns.length})</span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {cleanColumns.map((col) => (
              <span key={col.column} className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 font-mono">
                {col.column} <span className="text-[10px] text-slate-500">({col.semantic_label})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Remediation Audit History */}
      {fixLog.length > 0 && (
        <div className="glass-card rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Clock className="w-4 h-4 text-indigo-400" />
            <span>Executed Actions & Remediation Log ({fixLog.length})</span>
          </h3>

          <div className="overflow-x-auto rounded-xl border border-slate-800/80">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4 w-12">#</th>
                  <th className="py-2.5 px-4">Column</th>
                  <th className="py-2.5 px-4">Issue Remediated</th>
                  <th className="py-2.5 px-4">Executed Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 font-mono">
                {fixLog.map((log, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40">
                    <td className="py-2.5 px-4 text-slate-500">{idx + 1}</td>
                    <td className="py-2.5 px-4 text-slate-200 font-semibold">{log.Column}</td>
                    <td className="py-2.5 px-4 text-amber-400">{log.Issue}</td>
                    <td className="py-2.5 px-4 text-slate-300">{log["Fix Applied"]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};
