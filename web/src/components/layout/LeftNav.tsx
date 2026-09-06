'use client';

import React from 'react';
import {
  Flame,
  Layers,
  Award,
  ShieldCheck,
  FileText,
  Plus,
  Building2,
  Rocket,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';

interface LeftNavProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  role: 'nodal_officer' | 'startup';
  setRole: (role: 'nodal_officer' | 'startup') => void;
  onOpenCreateChallenge: () => void;
  onOpenDossier: () => void;
}

export const LeftNav: React.FC<LeftNavProps> = ({
  activeTab,
  setActiveTab,
  role,
  setRole,
  onOpenCreateChallenge,
  onOpenDossier,
}) => {
  const navItems = [
    { id: 'stream', label: 'Home / Stream', icon: Flame, badge: 'Live' },
    { id: 'challenges', label: 'Challenges', icon: Layers, badge: '1' },
    { id: 'pilots', label: 'Active Pilots', icon: Rocket, badge: '1 Active' },
    { id: 'gem', label: 'GeM Handoffs', icon: Award, badge: 'GFR 173' },
    { id: 'audit', label: 'Audit Chains', icon: ShieldCheck, badge: '100%' },
  ];

  return (
    <aside className="w-full lg:w-64 flex flex-col justify-between h-auto lg:h-[calc(100vh-2rem)] lg:sticky lg:top-4 bg-white rounded-3xl border border-slate-200/80 p-5 shadow-sm">
      <div className="space-y-6">
        {/* Tricolor Accent & Logo */}
        <div>
          <div className="h-1.5 w-full rounded-full bg-gradient-to-r from-amber-500 via-slate-100 to-emerald-600 mb-4 shadow-sm" />
          <div className="flex items-center space-x-3">
            <div className="h-11 w-11 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-black text-xl shadow-md shadow-blue-500/20">
              S
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-black tracking-tight text-slate-900">
                  SETU
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                  OS
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">
                Procurement OS &bull; Maharashtra
              </p>
            </div>
          </div>
        </div>

        {/* Role Switcher Pill */}
        <div className="bg-slate-100 p-1.5 rounded-2xl border border-slate-200/70">
          <div className="text-[10px] uppercase tracking-wider font-bold text-slate-400 px-2 py-1 flex items-center justify-between">
            <span>Operating View</span>
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
          </div>
          <div className="grid grid-cols-2 gap-1 mt-1">
            <button
              onClick={() => setRole('nodal_officer')}
              className={`flex items-center justify-center gap-1.5 py-2 px-2.5 rounded-xl text-xs font-bold transition-all ${
                role === 'nodal_officer'
                  ? 'bg-white text-blue-700 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>Nodal Officer</span>
            </button>
            <button
              onClick={() => setRole('startup')}
              className={`flex items-center justify-center gap-1.5 py-2 px-2.5 rounded-xl text-xs font-bold transition-all ${
                role === 'startup'
                  ? 'bg-white text-emerald-700 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Rocket className="w-3.5 h-3.5" />
              <span>Startup</span>
            </button>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={onOpenCreateChallenge}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md shadow-blue-600/20 hover:shadow-lg transition-all active:scale-[0.98]"
        >
          <Plus className="w-4 h-4" />
          <span>Post Outcome Challenge</span>
        </button>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  if (item.id === 'gem') {
                    onOpenDossier();
                  } else {
                    setActiveTab(item.id);
                  }
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-bold'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? 'text-blue-600' : 'text-slate-400'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isActive
                        ? 'bg-blue-200/70 text-blue-800'
                        : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Profile / Legal Footer */}
      <div className="pt-4 border-t border-slate-100 mt-6">
        <div className="flex items-center justify-between p-2 rounded-2xl bg-slate-50 border border-slate-200/60">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-700">
              {role === 'nodal_officer' ? 'RP' : 'HS'}
            </div>
            <div className="text-left">
              <div className="text-xs font-bold text-slate-800 truncate max-w-[110px]">
                {role === 'nodal_officer' ? 'Shri R. Patil, IAS' : 'HydroSense AI'}
              </div>
              <div className="text-[10px] text-slate-500">
                {role === 'nodal_officer' ? 'Pune Municipal Corp' : 'DPIIT #49201'}
              </div>
            </div>
          </div>
          <CheckCircle2 className="w-4 h-4 text-blue-600" />
        </div>
        <p className="text-[10px] text-slate-400 text-center mt-2.5">
          GFR 2017 Rule 173 Sandbox Compliant
        </p>
      </div>
    </aside>
  );
};
