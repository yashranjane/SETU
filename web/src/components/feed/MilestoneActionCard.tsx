'use client';

import React, { useState } from 'react';
import {
  CheckCircle2,
  Clock,
  ExternalLink,
  ShieldCheck,
  FileCheck2,
  Lock,
  ArrowRight,
  BadgeIndianRupee,
  Cpu,
} from 'lucide-react';
import { Milestone } from '@/lib/types';

interface MilestoneActionCardProps {
  milestone: Milestone;
  pilotId: number;
  onVerify: (pilotId: number, idx: number) => Promise<void>;
  isVerifying: boolean;
}

export const MilestoneActionCard: React.FC<MilestoneActionCardProps> = ({
  milestone,
  pilotId,
  onVerify,
  isVerifying,
}) => {
  const isApproved = milestone.status === 'Approved' || milestone.status === 'Disbursed';
  const isSubmitted = milestone.status === 'Submitted';

  const getStatusBadge = () => {
    if (isApproved) {
      return (
        <span className="flex items-center gap-1 text-[11px] font-extrabold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Disbursed (Escrow Released)
        </span>
      );
    }
    if (isSubmitted) {
      return (
        <span className="flex items-center gap-1 text-[11px] font-extrabold px-2.5 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-300 animate-pulse">
          <Clock className="w-3.5 h-3.5" />
          Ready for Nodal Verification
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-[11px] font-extrabold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
        <Lock className="w-3.5 h-3.5" />
        Escrow Locked
      </span>
    );
  };

  return (
    <div
      className={`bg-white rounded-3xl border ${
        isSubmitted
          ? 'border-amber-300 ring-2 ring-amber-100 shadow-md'
          : isApproved
          ? 'border-emerald-200 bg-emerald-50/20'
          : 'border-slate-200/80'
      } p-6 space-y-4 hover:shadow-md transition text-left`}
    >
      {/* Header: Milestone Index + Status */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div
            className={`h-9 w-9 rounded-2xl flex items-center justify-center font-black text-xs text-white ${
              isApproved ? 'bg-emerald-600' : isSubmitted ? 'bg-amber-600' : 'bg-slate-400'
            }`}
          >
            M{milestone.index}
          </div>
          <div>
            <h4 className="text-sm font-black text-slate-900">
              Phase {milestone.index}:{' '}
              {milestone.index === 1
                ? 'Ward 14 Sensor Array Setup & Telemetry Calibration'
                : milestone.index === 2
                ? '72-Hour Live Stormwater Stress Test & Detection'
                : 'Scale-Up Certification & PMC System Handover'}
            </h4>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Target Escrow Allocation: ₹{milestone.amount.toLocaleString('en-IN')}
            </p>
          </div>
        </div>
        {getStatusBadge()}
      </div>

      {/* Proof of Work / Evidence Link */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-200/70">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
          <FileCheck2 className="w-4 h-4 text-blue-600" />
          <span>Proof-of-Work:</span>
          {milestone.evidence_url ? (
            <a
              href={milestone.evidence_url}
              target="_blank"
              rel="noreferrer"
              className="text-blue-600 hover:text-blue-800 underline font-mono flex items-center gap-1"
            >
              <span>View Sensor Deployment Telemetry (PDF/Logs)</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          ) : (
            <span className="text-slate-400 italic font-normal">
              Awaiting startup upload
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 text-xs font-bold text-slate-600">
          <BadgeIndianRupee className="w-4 h-4 text-emerald-600" />
          <span>₹{milestone.amount.toLocaleString('en-IN')}</span>
        </div>
      </div>

      {/* Action CTA */}
      <div className="flex items-center justify-between pt-1">
        <div className="text-[11px] text-slate-500 font-medium">
          {isApproved
            ? '✅ Disbursed & Sealed with SHA-256 block in audit ledger.'
            : isSubmitted
            ? 'Requires Nodal Officer authorization to release escrow.'
            : 'Milestone is locked pending previous deliverable completion.'}
        </div>

        {isSubmitted && !isApproved && (
          <button
            onClick={() => onVerify(pilotId, milestone.index)}
            disabled={isVerifying}
            className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-600/20 hover:shadow-lg transition-all active:scale-[0.98] disabled:opacity-75"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{isVerifying ? 'Sealing Audit Block...' : '✅ Verify & Disburse Escrow'}</span>
          </button>
        )}
      </div>
    </div>
  );
};
