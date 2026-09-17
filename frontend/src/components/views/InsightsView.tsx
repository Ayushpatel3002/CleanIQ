import React from 'react';
import { DataInsightsResponse } from '../../types';
import { 
  Lightbulb, 
  AlertOctagon, 
  AlertTriangle, 
  Info, 
  CheckCircle2, 
  GitMerge, 
  Layers 
} from 'lucide-react';

interface InsightsViewProps {
  insightsData: DataInsightsResponse | null;
  onRemediate: () => void;
}

export const InsightsView: React.FC<InsightsViewProps> = ({ insightsData, onRemediate }) => {
  if (!insightsData || insightsData.insights.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400">
        <Lightbulb className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No critical insights detected. Dataset appears clean and well-structured.</p>
      </div>
    );
  }

  const { insights, correlations, summary_verdict } = insightsData;

  const getIcon = (type: string) => {
    switch (type) {
      case 'danger':
        return <AlertOctagon className="w-5 h-5 text-rose-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-amber-400" />;
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
      default:
        return <Info className="w-5 h-5 text-indigo-400" />;
    }
  };

  const getCardStyle = (type: string) => {
    switch (type) {
      case 'danger':
        return 'border-rose-500/30 bg-rose-500/5 hover:border-rose-500/50';
      case 'warning':
        return 'border-amber-500/30 bg-amber-500/5 hover:border-amber-500/50';
      case 'success':
        return 'border-emerald-500/30 bg-emerald-500/5 hover:border-emerald-500/50';
      default:
        return 'border-indigo-500/30 bg-indigo-500/5 hover:border-indigo-500/50';
    }
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Executive Summary Card */}
      <div className="glass-card rounded-2xl p-6 border-indigo-500/20 bg-indigo-500/5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
              Autonomous Data Quality Verdict
            </span>
          </div>
          <p className="text-sm sm:text-base font-medium text-slate-200">
            {summary_verdict}
          </p>
        </div>
        <button
          onClick={onRemediate}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all whitespace-nowrap"
        >
          Remediate in Smart Clean
        </button>
      </div>

      {/* Grid of Automated Findings */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-white flex items-center space-x-2">
          <span>Discovered Statistical Findings & Anomalies</span>
          <span className="px-2 py-0.5 rounded-full text-xs bg-slate-800 text-slate-300 font-normal">
            {insights.length}
          </span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((item, idx) => (
            <div
              key={idx}
              className={`p-5 rounded-2xl border transition-all glass-card space-y-3 ${getCardStyle(item.type)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
                    {getIcon(item.type)}
                  </div>
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                      {item.category}
                    </span>
                    <h4 className="text-sm font-bold text-white">{item.title}</h4>
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                  item.importance === 'High' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-400'
                }`}>
                  {item.importance}
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {item.description}
              </p>

              <div className="pt-1 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>Column: <b className="text-slate-200">{item.column}</b></span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Correlation Highlights */}
      {correlations.length > 0 && (
        <div className="glass-card rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <GitMerge className="w-4 h-4 text-purple-400" />
                <span>Feature Correlation Relationships (Pearson)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Identifies strongly correlated variables that can indicate redundant features or key causal signals.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {correlations.map((corr, idx) => {
              const absVal = Math.abs(corr.correlation);
              const isStrong = absVal >= 0.6;
              return (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono font-medium text-slate-300 truncate max-w-[170px]">
                      {corr.col1} ↔ {corr.col2}
                    </span>
                    <span className={`font-mono font-bold ${
                      isStrong ? (corr.correlation > 0 ? 'text-emerald-400' : 'text-rose-400') : 'text-slate-400'
                    }`}>
                      {corr.correlation > 0 ? `+${corr.correlation}` : corr.correlation}
                    </span>
                  </div>

                  {/* Correlation Strength Bar */}
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${corr.correlation > 0 ? 'bg-indigo-500' : 'bg-rose-500'}`}
                      style={{ width: `${absVal * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
};
