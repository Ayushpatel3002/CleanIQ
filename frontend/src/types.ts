export interface DatasetSummary {
  Rows: number;
  Columns: number;
  "Total Cells"?: number;
  "Missing Values": number;
  "Missing %"?: number;
  "Duplicate Rows": number;
  "Memory Usage (MB)": number;
  "Numeric Columns": number;
  "Categorical Columns": number;
  "Datetime Columns": number;
}

export interface DatasetPreview {
  columns: string[];
  dtypes: Record<string, string>;
  total_rows: number;
  total_columns: number;
  rows: Record<string, any>[];
}

export interface ColumnIntelligence {
  Column: string;
  "Data Type": string;
  "Missing Values": number;
  "Missing %": string;
  "Unique Values": number;
  Recommendation: string;
}

export interface NumericDistribution {
  kind: "numeric";
  bins: { range: string; count: number; midpoint: number }[];
  stats: {
    min: number;
    max: number;
    mean: number;
    median: number;
    std: number;
    skew: number;
  };
}

export interface CategoricalDistribution {
  kind: "categorical";
  categories: { label: string; count: number }[];
  total_unique: number;
}

export type ColumnDistribution = NumericDistribution | CategoricalDistribution;

export interface InsightItem {
  type: "danger" | "warning" | "info" | "success";
  category: string;
  title: string;
  description: string;
  column: string;
  importance: "High" | "Medium" | "Low";
}

export interface DataInsightsResponse {
  insights: InsightItem[];
  correlations: { col1: string; col2: string; correlation: number }[];
  summary_verdict: string;
  total_insights: number;
}

export interface FixOption {
  0: string; // action_code
  1: string; // label
}

export interface IssueItem {
  type: string;
  description: string;
  count: number;
  fix_options: [string, string][];
  default_fix: string;
  sample_bad?: any[];
}

export interface ColumnPlan {
  column: string;
  semantic_type: string;
  semantic_label: string;
  dtype: string;
  missing: number;
  unique: number;
  issues: IssueItem[];
  has_issues: boolean;
}

export interface DiffField {
  before: string;
  after: string;
  changed: boolean;
}

export interface DiffRow {
  row_index: number;
  has_diff: boolean;
  fields: Record<string, DiffField>;
}

export interface CompareResponse {
  stats: {
    rows_before: number;
    rows_after: number;
    rows_delta: number;
    columns_before: number;
    columns_after: number;
    diff_cells_in_sample: number;
    common_columns: string[];
  };
  diff_sample: DiffRow[];
}
