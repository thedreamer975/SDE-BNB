'use client';

import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children, footer }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      dialog.showModal();
      document.body.style.overflow = 'hidden';
    } else {
      dialog.close();
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    const handleCancel = (e: Event) => {
      e.preventDefault();
      onClose();
    };

    dialog.addEventListener('cancel', handleCancel);
    return () => dialog.removeEventListener('cancel', handleCancel);
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <dialog
      ref={dialogRef}
      className="fixed inset-0 z-50 p-0 m-auto bg-bg rounded-modal shadow-lg backdrop:bg-black/50 backdrop:backdrop-blur-sm max-w-[780px] w-full max-h-[90vh] flex flex-col overflow-hidden text-text"
      onClick={(e) => {
        if (e.target === dialogRef.current) onClose();
      }}
    >
      <div className="flex items-center justify-center h-16 border-b border-border shrink-0 relative px-6">
        <button
          onClick={onClose}
          className="absolute left-6 p-2 -ml-2 rounded-full hover:bg-surface transition-colors"
          aria-label="Close"
        >
          <X size={20} />
        </button>
        <h2 className="text-base font-semibold">{title}</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-6">{children}</div>

      {footer && (
        <div className="border-t border-border p-4 sm:px-6 shrink-0 bg-bg flex items-center justify-between">
          {footer}
        </div>
      )}
    </dialog>
  );
}
