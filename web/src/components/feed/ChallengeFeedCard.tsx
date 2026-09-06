'use client';

import React from 'react';
import {
  Sparkles,
  Building2,
  BadgeIndianRupee,
  Cpu,
  Layers,
  CheckCircle2,
} from 'lucide-react';
import { Challenge } from '@/lib/types';

interface ChallengeFeedCardProps {
  challenge: Challenge;
  onRunMatch: (challengeId: number) => void;
  isMatching: boolean;
  matchCount: number;
}

export const ChallengeFeedCard: React.FC<ChallengeFeedCardProps> = ({
  challenge,
  onRunMatch,
  isMatching,
  matchCount,
}) => {
  return (
    <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition space-y-5">
      {/* Header Info */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-700 font-bold">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold uppercase tracking-wider text-blue-700">
                Pune Municipal Corporation &bull; Ward 14
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                GFR 173 Sandbox
              </span>
            </div>
            <h2 className="text-lg font-black text-slate-900 mt-0.5 leading-snug">
              {challenge.title}
            </h2>
          </div>
        </div>

        {/* Budget Ceiling Pill */}
        <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-2xl bg-slate-50 border border-slate-200 text-slate-800 font-black text-sm">
          <BadgeIndianRupee className="w-4 h-4 text-emerald-600" />
          <span>₹{challenge.budget_ceiling.toLocaleString('en-IN')}</span>
        </div>
      </div>

      {/* Outcome Statement */}
      <div className="space-y-2">
        <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Target Outcome & Scope
        </div>
        <p className="text-sm text-slate-600 leading-relaxed">
          {challenge.outcome_statement}
        </p>
      </div>

      {/* Badges and CTA */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-slate-100 font-semibold text-slate-600">
            <Cpu className="w-3.5 h-3.5 text-blue-600" />
            AI & Sensor Telemetry
          </span>
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-slate-100 font-semibold text-slate-600">
            <Layers className="w-3.5 h-3.5 text-indigo-600" />
            90-Day Pilot
          </span>
        </div>

        <button
          onClick={() => onRunMatch(challenge.id)}
          disabled={isMatching}
          className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 hover:shadow-lg transition-all active:scale-[0.98] disabled:opacity-75"
        >
          <Sparkles className={`w-4 h-4 ${isMatching ? 'animate-spin' : ''}`} />
          <span>
            {isMatching
              ? 'Analyzing Semantics & TRL...'
              : matchCount > 0
              ? `Re-Run AI Match (${matchCount} Matched)`
              : '⚡ Run Explainable AI Match'}
          </span>
        </button>
      </div>
    </div>
  );
};
