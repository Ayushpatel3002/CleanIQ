import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HeroLanding } from './components/HeroLanding';
import { TabsNavigation, TabKey } from './components/TabsNavigation';
import { OverviewView } from './components/views/OverviewView';
import { DistributionsView } from './components/views/DistributionsView';
import { InsightsView } from './components/views/InsightsView';
import { SmartCleanView } from './components/views/SmartCleanView';
import { BeforeAfterView } from './components/views/BeforeAfterView';
import { QualityReportView } from './components/views/QualityReportView';
import { ExportView } from './components/views/ExportView';

import {
  uploadDataset,
  loadDemoDataset,
  fetchDatasetData,
  fetchColumnsAnalysis,
  fetchDistributions,
  fetchInsights,
  fetchSmartPlan,
  applyColumnFix,
  runAutoClean,
  undoLastFix,
  resetDataset,
  findAndReplace,
  fetchComparison,
  fetchQualityReport,
} from './lib/api';

import {
  DatasetSummary,
  DatasetPreview,
  ColumnIntelligence,
  ColumnDistribution,
  DataInsightsResponse,
  ColumnPlan,
  CompareResponse,
} from './types';
import { Loader2, Sparkles, CheckCircle, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [datasetName, setDatasetName] = useState<string | null>(null);
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [healthScore, setHealthScore] = useState<number | null>(null);
  const [healthLabel, setHealthLabel] = useState<string | null>(null);
  const [preview, setPreview] = useState<DatasetPreview | null>(null);
  const [canUndo, setCanUndo] = useState(false);
  const [fixLog, setFixLog] = useState<any[]>([]);

  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  // Tab Specific Data Caches
  const [columnsAnalysis, setColumnsAnalysis] = useState<ColumnIntelligence[]>([]);
  const [distributions, setDistributions] = useState<Record<string, ColumnDistribution>>({});
  const [insightsData, setInsightsData] = useState<DataInsightsResponse | null>(null);
  const [smartPlan, setSmartPlan] = useState<ColumnPlan[]>([]);
  const [compareData, setCompareData] = useState<CompareResponse | null>(null);
  const [qualityReport, setQualityReport] = useState<Record<string, any> | null>(null);

  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Helper to refresh all data after an edit or on dataset load
  const refreshDatasetDetails = async (id: string) => {
    try {
      const [
        dataRes,
        colsRes,
        distRes,
        insightsRes,
        planRes,
        compareRes,
        qualityRes,
      ] = await Promise.all([
        fetchDatasetData(id),
        fetchColumnsAnalysis(id),
        fetchDistributions(id),
        fetchInsights(id),
        fetchSmartPlan(id),
        fetchComparison(id),
        fetchQualityReport(id),
      ]);

      setSummary(dataRes.summary);
      setHealthScore(dataRes.health_score);
      setHealthLabel(dataRes.health_label);
      setPreview(dataRes.preview);
      setCanUndo(dataRes.can_undo);
      setFixLog(dataRes.fix_log || []);

      setColumnsAnalysis(colsRes.columns);
      setDistributions(distRes.distributions);
      setInsightsData(insightsRes);
      setSmartPlan(planRes.plan);
      setCompareData(compareRes);
      setQualityReport(qualityRes.quality_report);
    } catch (err: any) {
      console.error(err);
      showToast(err.message || 'Failed to refresh dataset metrics', 'error');
    }
  };

  const handleUploadFile = async (file: File) => {
    setIsLoading(true);
    try {
      const res = await uploadDataset(file);
      setDatasetId(res.dataset_id);
      setDatasetName(res.filename);
      setActiveTab('overview');
      await refreshDatasetDetails(res.dataset_id);
      showToast(`Loaded '${file.name}' successfully!`);
    } catch (err: any) {
      showToast(err.message || 'Upload failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadDemo = async () => {
    setIsLoading(true);
    try {
      const res = await loadDemoDataset();
      setDatasetId(res.dataset_id);
      setDatasetName(res.filename);
      setActiveTab('overview');
      await refreshDatasetDetails(res.dataset_id);
      showToast('Loaded Sample Enterprise Dataset with 250 records and dirty data patterns!');
    } catch (err: any) {
      showToast(err.message || 'Failed to load demo dataset', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplySingleFix = async (data: {
    column: string;
    issue_type: string;
    fix_action: string;
    custom_value?: string;
  }) => {
    if (!datasetId) return;
    setIsLoading(true);
    try {
      const res = await applyColumnFix(datasetId, data);
      await refreshDatasetDetails(datasetId);
      showToast(res.message || 'Fix applied successfully!');
    } catch (err: any) {
      showToast(err.message || 'Failed to apply fix', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunAutoClean = async () => {
    if (!datasetId) return;
    setIsLoading(true);
    try {
      const res = await runAutoClean(datasetId);
      await refreshDatasetDetails(datasetId);
      showToast('Executed full automated cleaning pipeline!');
      setActiveTab('compare');
    } catch (err: any) {
      showToast(err.message || 'Auto-clean failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUndo = async () => {
    if (!datasetId) return;
    setIsLoading(true);
    try {
      const res = await undoLastFix(datasetId);
      await refreshDatasetDetails(datasetId);
      showToast(res.message || 'Reverted last change');
    } catch (err: any) {
      showToast(err.message || 'Undo failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    if (!datasetId) return;
    if (!window.confirm('Reset dataset back to raw uploaded state? This will discard all applied fixes.')) {
      return;
    }
    setIsLoading(true);
    try {
      const res = await resetDataset(datasetId);
      await refreshDatasetDetails(datasetId);
      showToast(res.message || 'Reset to original dataset');
    } catch (err: any) {
      showToast(err.message || 'Reset failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFindReplace = async (payload: {
    find_value: string;
    replace_value: string;
    columns?: string[];
    is_regex?: boolean;
    match_case?: boolean;
  }) => {
    if (!datasetId) return;
    setIsLoading(true);
    try {
      const res = await findAndReplace(datasetId, payload);
      await refreshDatasetDetails(datasetId);
      showToast(res.message || 'Find and replace executed!');
    } catch (err: any) {
      showToast(err.message || 'Find and replace failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const totalIssuesCount = smartPlan.reduce((acc, curr) => acc + (curr.has_issues ? curr.issues.length : 0), 0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      
      {/* Top Navbar */}
      <Navbar
        datasetName={datasetName}
        healthScore={healthScore}
        healthLabel={healthLabel}
        canUndo={canUndo}
        onUndo={handleUndo}
        onReset={handleReset}
        onAutoClean={handleRunAutoClean}
        onNewUpload={() => setDatasetId(null)}
        isLoading={isLoading}
      />

      {/* Main Container */}
      <main className="flex-1">
        {!datasetId || !summary || !preview ? (
          <HeroLanding
            onFileSelected={handleUploadFile}
            onLoadDemo={handleLoadDemo}
            isLoading={isLoading}
          />
        ) : (
          <div>
            {/* Sub-Navigation Tabs */}
            <TabsNavigation
              activeTab={activeTab}
              onTabChange={setActiveTab}
              issuesCount={totalIssuesCount}
              insightsCount={insightsData?.total_insights || 0}
            />

            {/* Tab Body */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
              {activeTab === 'overview' && (
                <OverviewView
                  summary={summary}
                  healthScore={healthScore ?? 100}
                  healthLabel={healthLabel ?? 'Good'}
                  preview={preview}
                  columnsAnalysis={columnsAnalysis}
                  onGoToSmartClean={() => setActiveTab('smart_clean')}
                />
              )}

              {activeTab === 'distributions' && (
                <DistributionsView distributions={distributions} />
              )}

              {activeTab === 'insights' && (
                <InsightsView
                  insightsData={insightsData}
                  onRemediate={() => setActiveTab('smart_clean')}
                />
              )}

              {activeTab === 'smart_clean' && (
                <SmartCleanView
                  plan={smartPlan}
                  fixLog={fixLog}
                  onApplyFix={handleApplySingleFix}
                  onFindReplace={handleFindReplace}
                  isLoading={isLoading}
                />
              )}

              {activeTab === 'compare' && (
                <BeforeAfterView compareData={compareData} />
              )}

              {activeTab === 'quality' && (
                <QualityReportView qualityReport={qualityReport} />
              )}

              {activeTab === 'export' && (
                <ExportView
                  datasetId={datasetId}
                  datasetName={datasetName || 'dataset'}
                  totalRows={summary.Rows}
                  totalColumns={summary.Columns}
                />
              )}
            </div>
          </div>
        )}
      </main>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce">
          <div className={`flex items-center space-x-2.5 px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-xl text-xs font-medium ${
            toastMessage.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/30 text-emerald-200'
              : 'bg-rose-950/90 border-rose-500/30 text-rose-200'
          }`}>
            {toastMessage.type === 'success' ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400" />
            )}
            <span>{toastMessage.text}</span>
          </div>
        </div>
      )}

      {/* Global Loading Spinner Overlay */}
      {isLoading && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center">
          <div className="p-6 rounded-2xl glass-card flex flex-col items-center space-y-3 shadow-2xl border-indigo-500/20">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs font-semibold text-slate-200">Processing Data Operation...</p>
          </div>
        </div>
      )}

    </div>
  );
};
