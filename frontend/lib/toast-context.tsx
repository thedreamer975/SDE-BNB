'use client';

import React, {
  createContext,
  useCallback,
  useContext,
  useState,
  useRef,
} from 'react';
import { X } from 'lucide-react';

export interface Toast {
  id: string;
  message: string;
  type?: 'default' | 'error' | 'success';
  action?: { label: string; href: string };
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue>({
  toasts: [],
  addToast: () => '',
  removeToast: () => {},
});

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  }, []);

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = crypto.randomUUID();
      setToasts((prev) => [...prev, { ...toast, id }]);
      const timer = setTimeout(() => removeToast(id), 4000);
      timers.current.set(id, timer);
      return id;
    },
    [removeToast],
  );

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastStack toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

function ToastStack({
  toasts,
  removeToast,
}: {
  toasts: Toast[];
  removeToast: (id: string) => void;
}) {
  if (toasts.length === 0) return null;
  return (
    <div
      aria-live="polite"
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[9999] flex flex-col gap-2 items-center pointer-events-none"
    >
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onClose={() => removeToast(t.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  const bg =
    toast.type === 'error'
      ? 'bg-error'
      : toast.type === 'success'
        ? 'bg-success'
        : 'bg-[#222222]';
  return (
    <div
      role={toast.type === 'error' ? 'alert' : 'status'}
      className={`${bg} text-white text-sm font-medium px-4 py-3 rounded-[8px] shadow-lg flex items-center gap-3 pointer-events-auto min-w-[240px] max-w-[420px] animate-in`}
      onMouseEnter={() => {
        /* pause handled by hover CSS */
      }}
    >
      <span className="flex-1">{toast.message}</span>
      {toast.action && (
        <a
          href={toast.action.href}
          className="underline underline-offset-2 shrink-0 hover:no-underline"
        >
          {toast.action.label}
        </a>
      )}
      <button
        onClick={onClose}
        aria-label="Dismiss notification"
        className="shrink-0 opacity-70 hover:opacity-100"
      >
        <X size={16} />
      </button>
    </div>
  );
}

export function useToast(): ToastContextValue {
  return useContext(ToastContext);
}
