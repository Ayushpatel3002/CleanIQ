import React from 'react';
import { 
  BarChart3, 
  Sparkles, 
  FileSearch, 
  GitCompare, 
  PieChart, 
  Lightbulb, 
  Download 
} from 'lucide-react';

export type TabKey = 'overview' | 'distributions' | 'insights' | 'smart_clean' | 'compare' | 'quality' | 'export';

interface TabsNavigationProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  issuesCount?: number;
  insightsCount?: number;
}

export const TabsNavigation: React.FC<TabsNavigationProps> = ({
  activeTab,
  onTabChange,
  issuesCount = 0,
  insightsCount = 0,
}) => {
  const tabs: { key: TabKey; label: string; icon: React.ReactNode; badge?: number; badgeColor?: string }[] = [
    { key: 'overview', label: 'Overview & Profile', icon: <BarChart3 className="w-4 h-4" /> },
    { key: 'distributions', label: 'Distributions', icon: <PieChart className="w-4 h-4" /> },
    { 
      key: 'insights', 
      label: 'Deep Insights', 
      icon: <Lightbulb className="w-4 h-4" />, 
      badge: insightsCount > 0 ? insightsCount : undefined,
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30'
    },
    { 
      key: 'smart_clean', 
      label: 'Smart Clean', 
      icon: <Sparkles className="w-4 h-4 text-indigo-400" />,
      badge: issuesCount > 0 ? issuesCount : undefined,
      badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30'
    },
    { key: 'compare', label: 'Before vs After', icon: <GitCompare className="w-4 h-4" /> },
    { key: 'quality', label: 'Quality Audit', icon: <FileSearch className="w-4 h-4" /> },
    { key: 'export', label: 'Export & Save', icon: <Download className="w-4 h-4" /> },
  ];

  return (
    <div className="border-b border-slate-800 bg-slate-950/60 backdrop-blur-md sticky top-16 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex space-x-1 sm:space-x-2 overflow-x-auto py-2.5 no-scrollbar">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => onTabChange(tab.key)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.badge !== undefined && (
                  <span className={`px-1.5 py-0.2 rounded-full text-[11px] font-bold border ${tab.badgeColor || 'bg-slate-800 text-slate-300'}`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};
