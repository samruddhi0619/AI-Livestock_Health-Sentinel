import React from 'react';
import { cn } from './utils';

export function Card({ className, ...props }) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-slate-200/80 bg-white text-slate-900 shadow-sm transition-all duration-200',
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }) {
  return (
    <div
      className={cn('flex flex-col space-y-1.5 p-6 border-b border-slate-100', className)}
      {...props}
    />
  );
}

export function CardTitle({ className, ...props }) {
  return (
    <h3
      className={cn('text-lg font-semibold leading-none tracking-tight text-slate-900', className)}
      {...props}
    />
  );
}

export function CardDescription({ className, ...props }) {
  return (
    <p
      className={cn('text-sm text-slate-500 font-normal mt-1', className)}
      {...props}
    />
  );
}

export function CardContent({ className, ...props }) {
  return <div className={cn('p-6', className)} {...props} />;
}

export function CardFooter({ className, ...props }) {
  return (
    <div
      className={cn('flex items-center p-6 pt-0', className)}
      {...props}
    />
  );
}
