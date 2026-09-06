'use client';

import React, { useState } from 'react';
import { X, Plus, Building2, Sparkles, BadgeIndianRupee } from 'lucide-react';
import { createChallenge } from '@/lib/api';
import { Challenge } from '@/lib/types';

interface CreateChallengeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (challenge: Challenge) => void;
}

export const CreateChallengeModal: React.FC<CreateChallengeModalProps> = ({
  isOpen,
  onClose,
  onCreated,
}) => {
  const [title, setTitle] = useState('');
  const [outcome, setOutcome] = useState('');
  const [budget, setBudget] = useState('500000');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !outcome.trim()) return;

    setLoading(true);
    try {
      const created = await createChallenge({
        title,
        outcome_statement: outcome,
        budget_ceiling: parseFloat(budget) || 500000,
      });
      onCreated(created);
      onClose();
    } catch (err) {
      console.error('Error creating challenge:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-lg bg-white rounded-3xl border border-slate-200 shadow-2xl p-6 space-y-5 text-left">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-700 font-bold">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-black text-slate-900">
                Post Outcome Challenge
              </h3>
              <p className="text-xs text-slate-500">
                GFR 2017 Rule 173 &bull; Maharashtra Sandbox
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-xl hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Challenge Title
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)}
              placeholder="e.g. AI Sensor Network for Pothole Detection & Roughness Mapping"
              className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Target Outcome Statement
            </label>
            <textarea
              required
              rows={3}
              value={outcome}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setOutcome(e.target.value)}
              placeholder="Describe the problem, operational constraints, and desired metric outcome..."
              className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Sandbox Escrow Budget Ceiling (INR ₹)
            </label>
            <div className="relative">
              <BadgeIndianRupee className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="number"
                required
                min="50000"
                step="10000"
                value={budget}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setBudget(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-2xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 font-medium font-mono"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-600/20 hover:shadow-lg transition-all active:scale-[0.98] disabled:opacity-75"
            >
              <Plus className="w-4 h-4" />
              <span>{loading ? 'Publishing & Hashing...' : 'Publish Challenge'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
