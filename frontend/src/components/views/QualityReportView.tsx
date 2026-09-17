import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';

interface QualityReportViewProps {
  qualityReport: Record<string, Record<string, any>> | null;
}

export const QualityReportView: React.FC<QualityReportViewProps> = ({ qualityReport }) => {
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    "Outliers Remaining": true,
    "Invalid Emails": true,
    "Invalid Phone Numbers": true,
    "Category Inconsistencies": true,
    "Constant Columns": true,
  });

  if (!qualityReport) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400">
        <ShieldCheck className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No quality validation report generated yet.</p>
      </div>
    );
  }

  const toggleSection = (name: string) => {
    setOpenSections((prev) => ({ ...prev, [name]: !prev[name] }));
  };

  // Calculate total issues
  let totalIssuesCount = 0;
  Object.values(qualityReport).forEach((findingsMap) => {
    if (typeof findingsMap === 'object' && findingsMap !== null) {
      Object.values(findingsMap).forEach((val) => {
        if (typeof val === 'number') {
          totalIssuesCount += val;
        } else if (val && typeof val === 'string') {
          totalIssuesCount += 1;
        }
      });
    }
  });

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header Banner */}
      <div className="glass-card rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
            <span>Comprehensive Data Quality & Validation Audit</span>
          </h2>
          <p className="text-xs text-slate-400">
            Post-cleaning sanity checks on outlier fences, regex format conformance, and category standardizations.
          </p>
        </div>

        <div className={`px-4 py-2 rounded-xl text-xs font-bold border flex items-center space-x-2 ${
          totalIssuesCount === 0
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
        }`}>
          {totalIssuesCount === 0 ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
          <span>{totalIssuesCount} Total Findings Detected</span>
        </div>
      </div>

      {/* Accordions */}
      <div className="space-y-4">
        {Object.entries(qualityReport).map(([checkName, findingsMap]) => {
          const isOpen = openSections[checkName];
          const entries = Object.entries(findingsMap || {});
          
          let checkTotal = 0;
          entries.forEach(([_, val]) => {
            if (typeof val === 'number') checkTotal += val;
            else if (val) checkTotal += 1;
          });

          return (
            <div key={checkName} className="glass-card rounded-2xl overflow-hidden border border-slate-800">
              <div
                onClick={() => toggleSection(checkName)}
                className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-900/40 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className={`w-2.5 h-2.5 rounded-full ${checkTotal === 0 ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                  <h3 className="text-sm font-bold text-white">{checkName}</h3>
                  <span className="text-xs text-slate-400">({entries.length} columns inspected)</span>
                </div>

                <div className="flex items-center space-x-3">
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                    checkTotal === 0
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>
                    {checkTotal === 0 ? 'Passed ✅' : `${checkTotal} Issues ⚠️`}
                  </span>
                  {isOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                </div>
              </div>

              {isOpen && (
                <div className="p-5 border-t border-slate-800/80 bg-slate-950/40">
                  {entries.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">No applicable columns found for this check.</p>
                  ) : (
                    <div className="overflow-x-auto rounded-xl border border-slate-800">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900 text-slate-400 font-semibold border-b border-slate-800">
                          <tr>
                            <th className="py-2.5 px-4">Column</th>
                            <th className="py-2.5 px-4">Detected Findings</th>
                            <th className="py-2.5 px-4 text-right">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                          {entries.map(([col, findings]) => {
                            const isZero = findings === 0 || findings === '0';
                            return (
                              <tr key={col} className="hover:bg-slate-900/30">
                                <td className="py-2.5 px-4 font-mono font-medium text-slate-200">{col}</td>
                                <td className="py-2.5 px-4 font-mono text-slate-300">
                                  {typeof findings === 'number' ? `${findings} anomaly rows` : String(findings)}
                                </td>
                                <td className="py-2.5 px-4 text-right">
                                  <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                                    isZero ? 'text-emerald-400 bg-emerald-500/10' : 'text-amber-400 bg-amber-500/10'
                                  }`}>
                                    {isZero ? 'Verified OK' : 'Remediation Needed'}
                                  </span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
};
