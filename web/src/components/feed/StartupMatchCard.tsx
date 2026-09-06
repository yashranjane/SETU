'use client';

import React from 'react';
import {
  Rocket,
  Award,
  CheckCircle2,
  FileText,
  Percent,
  Sliders,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { StartupMatch } from '@/lib/types';
import { getMoUUrl } from '@/lib/api';

interface StartupMatchCardProps {
  match: StartupMatch;
  rank: number;
  pilotId: number;
  onLockEscrow: (startupId: string) => void;
  isPilotCreated: boolean;
}

export const StartupMatchCard: React.FC<StartupMatchCardProps> = ({
  match,
  rank,
  pilotId,
  onLockEscrow,
  isPilotCreated,
}) => {
  const scorePercent = Math.round(match.composite_score * 100);

  // Score color grading
  const getScoreTheme = (score: number) => {
    if (score >= 80)
      return {
        bg: 'bg-emerald-50',
        text: 'text-emerald-700',
        border: 'border-emerald-200',
        badge: 'bg-emerald-600',
      };
    if (score >= 60)
      return {
        bg: 'bg-blue-50',
        text: 'text-blue-700',
        border: 'border-blue-200',
        badge: 'bg-blue-600',
      };
    return {
      bg: 'bg-amber-50',
      text: 'text-amber-700',
      border: 'border-amber-200',
      badge: 'bg-amber-600',
    };
  };

  const theme = getScoreTheme(scorePercent);
  const mouUrl = getMoUUrl(pilotId);

  return (
    <div
      className={`bg-white rounded-3xl border ${
        rank === 1 ? 'border-blue-300 ring-2 ring-blue-100 shadow-md' : 'border-slate-200/80 shadow-sm'
      } p-6 space-y-4 hover:shadow-md transition text-left`}
    >
      {/* Top Banner: Rank + Name + Score */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className={`h-9 w-9 rounded-2xl flex items-center justify-center font-black text-xs text-white shadow-sm ${
              rank === 1 ? 'bg-blue-600' : 'bg-slate-700'
            }`}
          >
            #{rank}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-black text-slate-900 leading-none">
                {match.startup_name}
              </h3>
              {rank === 1 && (
                <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                  Recommended Match
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 font-medium mt-1">
              Startup ID: <span className="font-mono">{match.startup_id}</span>
            </p>
          </div>
        </div>

        {/* Composite Score Pill */}
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-2xl border ${theme.bg} ${theme.border} ${theme.text}`}
        >
          <Sparkles className="w-4 h-4" />
          <div className="text-right">
            <div className="text-base font-black leading-none">{scorePercent}%</div>
            <div className="text-[9px] uppercase tracking-wider font-extrabold opacity-80 mt-0.5">
              Fit Score
            </div>
          </div>
        </div>
      </div>

      {/* Reason Chips */}
      <div className="flex flex-wrap gap-1.5 pt-1">
        {match.reason_codes.map((reason, idx) => (
          <span
            key={idx}
            className="text-[11px] font-bold px-3 py-1 rounded-xl bg-slate-100/90 text-slate-700 border border-slate-200/60"
          >
            {reason}
          </span>
        ))}
      </div>

      {/* 4-Factor Weighted Breakdown Bar */}
      <div className="space-y-1.5 bg-slate-50 p-3 rounded-2xl border border-slate-200/60">
        <div className="flex justify-between text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          <span>Weighted Formula Breakdown</span>
          <span>40% Sem &bull; 25% TRL &bull; 20% Comp &bull; 15% Cap</span>
        </div>
        <div className="grid grid-cols-4 gap-2 pt-1">
          <div className="bg-white p-2 rounded-xl border border-slate-100 text-center">
            <div className="text-[10px] text-slate-400 font-bold uppercase">Semantic</div>
            <div className="text-xs font-black text-blue-600 mt-0.5">
              {Math.round(match.semantic_fit * 100)}%
            </div>
          </div>
          <div className="bg-white p-2 rounded-xl border border-slate-100 text-center">
            <div className="text-[10px] text-slate-400 font-bold uppercase">TRL Level</div>
            <div className="text-xs font-black text-indigo-600 mt-0.5">
              TRL {match.raw_trl}
            </div>
          </div>
          <div className="bg-white p-2 rounded-xl border border-slate-100 text-center">
            <div className="text-[10px] text-slate-400 font-bold uppercase">Compliance</div>
            <div className="text-xs font-black text-emerald-600 mt-0.5">
              {Math.round(match.compliance_score * 100)}%
            </div>
          </div>
          <div className="bg-white p-2 rounded-xl border border-slate-100 text-center">
            <div className="text-[10px] text-slate-400 font-bold uppercase">Capacity</div>
            <div className="text-xs font-black text-amber-600 mt-0.5">
              {Math.round(match.capacity_score * 100)}%
            </div>
          </div>
        </div>
      </div>

      {/* Action CTA */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <a
          href={mouUrl}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-800 transition"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Preview GFR 173 MoU (PDF)</span>
          <ExternalLink className="w-3 h-3" />
        </a>

        <button
          onClick={() => onLockEscrow(match.startup_id)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-bold transition-all shadow-sm active:scale-[0.98] ${
            isPilotCreated
              ? 'bg-emerald-600 text-white shadow-emerald-500/20'
              : 'bg-slate-900 hover:bg-slate-800 text-white shadow-slate-900/20'
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>
            {isPilotCreated
              ? '✅ Pilot Active & MoU Executed'
              : '📄 Sign Sandbox MoU & Lock Escrow'}
          </span>
        </button>
      </div>
    </div>
  );
};
