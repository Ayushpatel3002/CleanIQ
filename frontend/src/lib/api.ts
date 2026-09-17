import {
  DatasetSummary,
  DatasetPreview,
  ColumnIntelligence,
  ColumnDistribution,
  DataInsightsResponse,
  ColumnPlan,
  CompareResponse
} from '../types';

const BASE_URL = '/api';

export async function uploadDataset(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function loadDemoDataset() {
  const res = await fetch(`${BASE_URL}/load-demo`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to load demo dataset');
  return res.json();
}

export async function fetchDatasetData(id: string) {
  const res = await fetch(`${BASE_URL}/dataset/${id}/data`);
  if (!res.ok) throw new Error('Failed to fetch dataset');
  return res.json();
}

export async function fetchColumnsAnalysis(id: string): Promise<{ columns: ColumnIntelligence[] }> {
  const res = await fetch(`${BASE_URL}/dataset/${id}/columns`);
  if (!res.ok) throw new Error('Failed to fetch columns analysis');
  return res.json();
}

export async function fetchDistributions(id: string): Promise<{ distributions: Record<string, ColumnDistribution> }> {
  const res = await fetch(`${BASE_URL}/dataset/${id}/distributions`);
  if (!res.ok) throw new Error('Failed to fetch distributions');
  return res.json();
}

export async function fetchInsights(id: string): Promise<DataInsightsResponse> {
  const res = await fetch(`${BASE_URL}/dataset/${id}/insights`);
  if (!res.ok) throw new Error('Failed to fetch insights');
  return res.json();
}

export async function fetchSmartPlan(id: string): Promise<{ plan: ColumnPlan[] }> {
  const res = await fetch(`${BASE_URL}/dataset/${id}/smart-plan`);
  if (!res.ok) throw new Error('Failed to fetch smart cleaning plan');
  return res.json();
}

export async function applyColumnFix(
  id: string,
  data: { column: string; issue_type: string; fix_action: string; custom_value?: string }
) {
  const res = await fetch(`${BASE_URL}/dataset/${id}/apply-fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to apply fix');
  return res.json();
}

export async function runAutoClean(id: string) {
  const res = await fetch(`${BASE_URL}/dataset/${id}/auto-clean`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to run auto-clean');
  return res.json();
}

export async function undoLastFix(id: string) {
  const res = await fetch(`${BASE_URL}/dataset/${id}/undo`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Undo failed' }));
    throw new Error(err.detail || 'Undo failed');
  }
  return res.json();
}

export async function resetDataset(id: string) {
  const res = await fetch(`${BASE_URL}/dataset/${id}/reset`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to reset dataset');
  return res.json();
}

export async function findAndReplace(
  id: string,
  payload: { find_value: string; replace_value: string; columns?: string[]; is_regex?: boolean; match_case?: boolean }
) {
  const res = await fetch(`${BASE_URL}/dataset/${id}/find-replace`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to run find and replace');
  return res.json();
}

export async function fetchComparison(id: string): Promise<CompareResponse> {
  const res = await fetch(`${BASE_URL}/dataset/${id}/compare`);
  if (!res.ok) throw new Error('Failed to fetch comparison');
  return res.json();
}

export async function fetchQualityReport(id: string) {
  const res = await fetch(`${BASE_URL}/dataset/${id}/quality-report`);
  if (!res.ok) throw new Error('Failed to fetch quality report');
  return res.json();
}

export function getExportUrl(id: string, format: 'csv' | 'excel' | 'json' | 'pdf') {
  return `${BASE_URL}/dataset/${id}/export/${format}`;
}
