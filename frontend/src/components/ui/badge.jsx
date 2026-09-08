import React from 'react';
import { cn } from './utils';

export function Badge({ className, variant = 'default', children, ...props }) {
  const variants = {
    default: 'bg-slate-100 text-slate-800 border-slate-200',
    primary: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    low: 'bg-emerald-100 text-emerald-800 border-emerald-300 font-semibold',
    medium: 'bg-amber-100 text-amber-800 border-amber-300 font-semibold',
    high: 'bg-orange-100 text-orange-800 border-orange-300 font-semibold',
    critical: 'bg-red-100 text-red-800 border-red-300 font-semibold animate-pulse',
    outline: 'border border-slate-300 text-slate-700 bg-transparent',
    success: 'bg-green-100 text-green-800 border-green-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    danger: 'bg-rose-100 text-rose-800 border-rose-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors',
        variants[variant?.toLowerCase()] || variants.default,
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export function RiskBadge({ level, score, showScore = true, className }) {
  const lvl = level ? level.toLowerCase() : 'low';
  
  let variant = 'low';
  let label = 'Low Risk';
  let dotColor = 'bg-emerald-500';

  if (lvl.includes('crit') || (score !== undefined && score >= 81)) {
    variant = 'critical';
    label = 'Critical';
    dotColor = 'bg-red-600';
  } else if (lvl.includes('high') || (score !== undefined && score >= 61)) {
    variant = 'high';
    label = 'High Risk';
    dotColor = 'bg-orange-500';
  } else if (lvl.includes('med') || lvl.includes('mod') || (score !== undefined && score >= 31)) {
    variant = 'medium';
    label = 'Medium Risk';
    dotColor = 'bg-amber-500';
  } else {
    variant = 'low';
    label = 'Low Risk';
    dotColor = 'bg-emerald-500';
  }

  return (
    <Badge variant={variant} className={cn('text-xs px-2.5 py-1', className)}>
      <span className={cn('w-2 h-2 rounded-full inline-block mr-1', dotColor)} />
      <span>{label}</span>
      {showScore && score !== undefined && score !== null && (
        <span className="opacity-80 ml-1 font-mono text-[11px]">({score})</span>
      )}
    </Badge>
  );
}
