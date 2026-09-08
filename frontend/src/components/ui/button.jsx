import React from 'react';
import { cn } from './utils';

export const Button = React.forwardRef(({
  className,
  variant = 'primary',
  size = 'md',
  disabled,
  children,
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer';

  const variants = {
    primary: 'bg-emerald-700 hover:bg-emerald-800 text-white shadow-sm focus:ring-emerald-600',
    secondary: 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200 focus:ring-emerald-500',
    accent: 'bg-amber-500 hover:bg-amber-600 text-white shadow-sm focus:ring-amber-400',
    outline: 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-emerald-500',
    destructive: 'bg-red-600 hover:bg-red-700 text-white shadow-sm focus:ring-red-500',
    ghost: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
    subtle: 'bg-slate-100 text-slate-700 hover:bg-slate-200'
  };

  const sizes = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2.5 gap-2',
    lg: 'text-base px-5 py-3 gap-2.5 font-semibold',
    icon: 'p-2'
  };

  return (
    <button
      ref={ref}
      disabled={disabled}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';
