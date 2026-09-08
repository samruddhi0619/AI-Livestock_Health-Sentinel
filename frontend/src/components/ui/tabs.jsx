import React from 'react';
import { cn } from './utils';

export function Tabs({ activeTab, onTabChange, tabs, className }) {
  return (
    <div className={cn('flex items-center gap-1 p-1 bg-slate-100 rounded-xl overflow-x-auto', className)}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-all duration-150 cursor-pointer',
              isActive
                ? 'bg-white text-emerald-800 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
            )}
          >
            {Icon && <Icon size={16} className={isActive ? 'text-emerald-700' : 'text-slate-400'} />}
            <span>{tab.label}</span>
            {tab.badge !== undefined && (
              <span className={cn(
                'ml-1 px-1.5 py-0.2 text-[11px] rounded-full font-mono',
                isActive ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'
              )}>
                {tab.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
