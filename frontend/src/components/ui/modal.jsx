import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { cn } from './utils';

export function Modal({ isOpen, onClose, title, description, children, maxWidth = 'max-w-xl', className }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className={cn(
          'relative w-full bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]',
          maxWidth,
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            {title && <h3 className="text-lg font-bold text-slate-900">{title}</h3>}
            {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg p-1.5 transition-colors cursor-pointer"
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto flex-1">
          {children}
        </div>
      </div>
    </div>
  );
}
