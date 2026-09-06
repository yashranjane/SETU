'use client';

import React, { useEffect, useState } from 'react';
import { X, Award, FileCheck, ShieldCheck, CheckCircle2, Download, Building2 } from 'lucide-react';
import { GeMDossier } from '@/lib/types';
import { getDossier } from '@/lib/api';

interface GeMDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  pilotId: number;
}

export const GeMDossierModal: React.FC<GeMDossierModalProps> = ({
  isOpen,
  onClose,
  pilotId,
}) => {
  const [dossier, setDossier] = useState<GeMDossier | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      getDossier(pilotId)
        .then((res) => setDossier(res))
        .finally(() => setLoading(false));
    }
  }, [isOpen, pilotId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-2xl bg-white rounded-3xl border border-slate-200 shadow-2xl p-6 space-y-5 text-left max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="h-10 w-10 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-700 font-bold">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-black text-slate-900">
                  GeM Startup Runway Scale-Up Dossier
                </h3>
                <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  GFR 173 Direct
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Government of Maharashtra &bull; Innovation Sandbox Certified
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

        {loading || !dossier ? (
          <div className="p-12 text-center text-slate-500 text-sm font-semibold animate-pulse">
            Compiling Cryptographic Scale-Up Dossier...
          </div>
        ) : (
          <div className="space-y-4">
            {/* Status Banner */}
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                <div>
                  <div className="text-xs font-bold text-emerald-950">
                    {dossier.gem_startup_runway_recommendation.status}
                  </div>
                  <p className="text-[11px] text-emerald-700 mt-0.5">
                    {dossier.gem_startup_runway_recommendation.tender_waiver_justification}
                  </p>
                </div>
              </div>
              <span className="text-xs font-black font-mono px-3 py-1 rounded-xl bg-emerald-600 text-white shadow-sm">
                Scale-Up Ready
              </span>
            </div>

            {/* Profile Grid */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Awarded Startup
                </div>
                <div className="text-sm font-black text-slate-900 mt-0.5">
                  {dossier.startup_profile.legal_name}
                </div>
                <div className="text-xs text-slate-500 mt-0.5">
                  TRL {dossier.startup_profile.trl} &bull; DPIIT Certified
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Procuring Department
                </div>
                <div className="text-sm font-black text-slate-900 mt-0.5">
                  {dossier.procuring_department.department}
                </div>
                <div className="text-xs text-slate-500 mt-0.5">
                  Nodal: {dossier.procuring_department.nodal_officer}
                </div>
              </div>
            </div>

            {/* Verification Matrix */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-600">
                Milestone Verification Matrix
              </div>
              <div className="space-y-1.5">
                {dossier.milestone_verification_matrix.map((m) => (
                  <div
                    key={m.index}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-slate-200/60 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-800">Milestone {m.index}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {m.status}
                      </span>
                    </div>
                    <span className="font-mono font-bold text-slate-700">
                      ₹{m.amount_inr.toLocaleString('en-IN')}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Cryptographic Certification Box */}
            <div className="p-4 rounded-2xl bg-slate-900 text-slate-100 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Audit Chain Attestation</span>
                </div>
                <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-slate-800 text-emerald-400">
                  {dossier.audit_certification.total_audit_blocks} Blocks Verified
                </span>
              </div>
              <div className="text-[10px] font-mono text-slate-400 truncate bg-slate-800 p-2 rounded-xl border border-slate-700">
                Head Hash: {dossier.audit_certification.latest_sealed_hash}
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-slate-500 font-medium">
                Ref: {dossier.pilot_reference_id}
              </span>
              <button
                onClick={onClose}
                className="px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md transition"
              >
                Close Dossier
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
