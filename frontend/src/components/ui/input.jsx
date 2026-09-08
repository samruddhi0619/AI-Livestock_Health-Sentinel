import React from 'react';
import { cn } from './utils';

export const Input = React.forwardRef(({ className, type = 'text', error, ...props }, ref) => {
  return (
    <div className="w-full">
      <input
        type={type}
        className={cn(
          'flex h-11 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-150',
          error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
          className
        )}
        ref={ref}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
});
Input.displayName = 'Input';

export const Select = React.forwardRef(({ className, children, error, ...props }, ref) => {
  return (
    <div className="w-full">
      <select
        className={cn(
          'flex h-11 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-150',
          error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </select>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
});
Select.displayName = 'Select';

export const Textarea = React.forwardRef(({ className, error, rows = 3, ...props }, ref) => {
  return (
    <div className="w-full">
      <textarea
        rows={rows}
        className={cn(
          'flex w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-150',
          error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
          className
        )}
        ref={ref}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
});
Textarea.displayName = 'Textarea';
