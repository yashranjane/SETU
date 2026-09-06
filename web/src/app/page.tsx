'use client';

import React, { useEffect, useState } from 'react';
import { LeftNav } from '@/components/layout/LeftNav';
import { RightAuditRail } from '@/components/layout/RightAuditRail';
import { ChallengeFeedCard } from '@/components/feed/ChallengeFeedCard';
import { StartupMatchCard } from '@/components/feed/StartupMatchCard';
import { MilestoneActionCard } from '@/components/feed/MilestoneActionCard';
import { CreateChallengeModal } from '@/components/modals/CreateChallengeModal';
import { GeMDossierModal } from '@/components/modals/GeMDossierModal';
import {
  AuditBlock,
  Challenge,
  Milestone,
  Pilot,
  StartupMatch,
} from '@/lib/types';
import {
  createPilot,
  getAuditChain,
  getChallenges,
  getPilot,
  matchStartups,
  verifyMilestone,
} from '@/lib/api';
import {
  Flame,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Layers,
  Building2,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState('stream');
  const [role, setRole] = useState<'nodal_officer' | 'startup'>('nodal_officer');

  // Core State
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [matches, setMatches] = useState<StartupMatch[]>([]);
  const [isMatching, setIsMatching] = useState(false);
  const [activePilot, setActivePilot] = useState<Pilot | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [auditBlocks, setAuditBlocks] = useState<AuditBlock[]>([]);
  const [isVerifying, setIsVerifying] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDossierModalOpen, setIsDossierModalOpen] = useState(false);

  // Initial Load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const chList = await getChallenges();
      setChallenges(chList);

      const pilotData = await getPilot(1);
      setActivePilot(pilotData.pilot);
      setMilestones(pilotData.milestones);

      const auditList = await getAuditChain(1);
      setAuditBlocks(auditList);
    } catch (err) {
      console.error('Error loading initial data:', err);
    }
  };

  const handleRunMatch = async (challengeId: number) => {
    setIsMatching(true);
    try {
      const res = await matchStartups(challengeId);
      setMatches(res.matches);
      showNotification('⚡ Explainable AI match complete! Top 3 candidates ranked by multi-factor composite score.');
    } catch (err) {
      console.error('Match error:', err);
    } finally {
      setIsMatching(false);
    }
  };

  const handleLockEscrow = async (startupId: string) => {
    try {
      const res = await createPilot(challenges[0]?.id || 1, startupId);
      setActivePilot(res.pilot);
      setMilestones(res.milestones);

      // Refresh audit logs to show pilot initialization
      const logs = await getAuditChain(res.pilot.id);
      setAuditBlocks(logs);

      showNotification(`📄 GFR 173 Sandbox MoU signed! Escrow allocated for ${startupId}.`);
    } catch (err) {
      console.error('Lock escrow error:', err);
    }
  };

  const handleVerifyMilestone = async (pilotId: number, idx: number) => {
    setIsVerifying(true);
    try {
      const res = await verifyMilestone(pilotId, idx);

      // Update local milestones state
      setMilestones((prev) =>
        prev.map((m) => (m.index === idx ? res.milestone : m))
      );

      // Append new block to audit rail
      const logs = await getAuditChain(pilotId);
      setAuditBlocks(logs);

      showNotification(
        `✅ Milestone ${idx} verified! ₹${res.escrow_disbursement_inr.toLocaleString(
          'en-IN'
        )} disbursed & sealed with SHA-256 block.`
      );
    } catch (err) {
      console.error('Verify error:', err);
    } finally {
      setIsVerifying(false);
    }
  };

  const showNotification = (msg: string) => {
    setNotification(msg);
    setTimeout(() => {
      setNotification(null);
    }, 6000);
  };

  const disbursedAmount = milestones
    .filter((m) => m.status === 'Approved' || m.status === 'Disbursed')
    .reduce((acc, m) => acc + m.amount, 0);

  const totalBudget = challenges[0]?.budget_ceiling || 300000;

  return (
    <div className="min-h-screen bg-slate-100/70 text-slate-900 antialiased font-sans p-2 sm:p-4 lg:p-6">
      {/* Top Banner Alert (Toast) */}
      {notification && (
        <div className="fixed top-5 left-1/2 -translate-x-1/2 z-50 max-w-xl w-[90%] p-4 rounded-2xl bg-slate-900 text-white shadow-2xl border border-slate-700 flex items-center justify-between gap-3 animate-in fade-in slide-in-from-top-4">
          <div className="flex items-center gap-3 text-xs font-bold leading-snug">
            <Sparkles className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{notification}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-slate-400 hover:text-white text-xs font-bold px-2 py-1"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* 3-Column Responsive Grid */}
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6 items-start justify-center">
        {/* Left Column: Navigation Rail (20%) */}
        <LeftNav
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          role={role}
          setRole={setRole}
          onOpenCreateChallenge={() => setIsCreateModalOpen(true)}
          onOpenDossier={() => setIsDossierModalOpen(true)}
        />

        {/* Center Column: High-Speed Operational Feed (55%) */}
        <main className="w-full lg:flex-1 space-y-6">
          {/* Feed Header */}
          <div className="bg-white rounded-3xl border border-slate-200/80 p-5 shadow-sm flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center font-black">
                <Flame className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-base font-black text-slate-900">
                  Procurement Stream &bull; Maharashtra Sandbox
                </h1>
                <p className="text-xs text-slate-500 font-medium">
                  Autonomous innovation challenge matching & milestone escrows
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                Live Node: Pune MC
              </span>
            </div>
          </div>

          {/* Active Outcome Challenge Card */}
          {challenges.map((challenge) => (
            <ChallengeFeedCard
              key={challenge.id}
              challenge={challenge}
              onRunMatch={handleRunMatch}
              isMatching={isMatching}
              matchCount={matches.length}
            />
          ))}

          {/* Matched Candidates Section (Explainable AI) */}
          {matches.length > 0 && (
            <div className="space-y-4 pt-2">
              <div className="flex items-center justify-between px-2">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <h3 className="text-xs font-black uppercase tracking-wider text-slate-800">
                    Explainable AI Candidate Rankings ({matches.length})
                  </h3>
                </div>
                <span className="text-xs text-slate-500 font-semibold">
                  Model: paraphrase-multilingual-MiniLM-L12-v2
                </span>
              </div>

              <div className="space-y-4">
                {matches.map((match, idx) => (
                  <StartupMatchCard
                    key={match.startup_id}
                    match={match}
                    rank={idx + 1}
                    pilotId={activePilot?.id || 1}
                    onLockEscrow={handleLockEscrow}
                    isPilotCreated={
                      activePilot?.startup_id === match.startup_id
                    }
                  />
                ))}
              </div>
            </div>
          )}

          {/* Milestone Action & Escrow Verification Section */}
          <div className="space-y-4 pt-4">
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <h3 className="text-xs font-black uppercase tracking-wider text-slate-800">
                  Pilot Milestone Escrows (Ward 14 HydroSense AI)
                </h3>
              </div>
              <span className="text-xs font-mono font-bold text-slate-500">
                GFR 173 Disbursals
              </span>
            </div>

            <div className="space-y-4">
              {milestones.map((m) => (
                <MilestoneActionCard
                  key={m.id || m.index}
                  milestone={m}
                  pilotId={activePilot?.id || 1}
                  onVerify={handleVerifyMilestone}
                  isVerifying={isVerifying}
                />
              ))}
            </div>
          </div>
        </main>

        {/* Right Column: Cryptographic Audit Rail (25%) */}
        <RightAuditRail
          pilotId={activePilot?.id || 1}
          auditBlocks={auditBlocks}
          totalBudget={totalBudget}
          disbursedAmount={disbursedAmount}
          onOpenDossier={() => setIsDossierModalOpen(true)}
          onRefreshAudit={loadInitialData}
        />
      </div>

      {/* Modals */}
      <CreateChallengeModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreated={(ch) => {
          setChallenges((prev) => [ch, ...prev]);
          showNotification(`🚀 New Challenge "${ch.title}" published & sealed in audit chain.`);
        }}
      />

      <GeMDossierModal
        isOpen={isDossierModalOpen}
        onClose={() => setIsDossierModalOpen(false)}
        pilotId={activePilot?.id || 1}
      />
    </div>
  );
}
