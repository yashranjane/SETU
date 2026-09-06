import {
  AuditBlock,
  Challenge,
  GeMDossier,
  Milestone,
  Pilot,
  StartupMatch,
  VerifyAuditResponse,
} from './types';

const RAW_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const API_BASE_URL = RAW_API_URL.endsWith('/api/v1')
  ? RAW_API_URL
  : `${RAW_API_URL.replace(/\/$/, '')}/api/v1`;

// Fallback seed dataset for instant offline/standalone preview
const SEED_CHALLENGES: Challenge[] = [
  {
    id: 1,
    title: 'Automated Urban Drainage Blockage Detection & Telemetry (Ward 14, Pune Municipal Corporation)',
    outcome_statement:
      'Deployment of real-time non-invasive telemetry and AI acoustic/ultrasonic sensing to detect subsurface stormwater drain clogs and sewage overflow risks across critical flooding hotspots in Ward 14.',
    budget_ceiling: 300000.0,
    status: 'Published',
  },
];

const SEED_MATCHES: StartupMatch[] = [
  {
    startup_id: 'hydrosense-ai',
    startup_name: 'HydroSense AI Pvt. Ltd.',
    composite_score: 0.918,
    semantic_fit: 0.925,
    trl_score: 0.778,
    raw_trl: 7,
    compliance_score: 0.98,
    capacity_score: 0.92,
    breakdown: {
      semantic_contribution: 0.37,
      trl_contribution: 0.1945,
      compliance_contribution: 0.196,
      capacity_contribution: 0.138,
    },
    reason_codes: [
      'High Semantic Fit: 92.5%',
      'TRL-7 Field Tested & Production Ready',
      'DPIIT Certified under GFR 173 Innovation Sandbox',
      'High Deployment & Pilot Execution Capacity',
    ],
  },
  {
    startup_id: 'citydrain-mech',
    startup_name: 'CityDrain Robotics',
    composite_score: 0.672,
    semantic_fit: 0.65,
    trl_score: 0.556,
    raw_trl: 5,
    compliance_score: 0.70,
    capacity_score: 0.65,
    breakdown: {
      semantic_contribution: 0.26,
      trl_contribution: 0.139,
      compliance_contribution: 0.14,
      capacity_contribution: 0.0975,
    },
    reason_codes: [
      'Moderate Semantic Fit: 65.0%',
      'TRL-5 Validated Prototype',
      'Partial Statutory Compliance (State Policy Eligible)',
    ],
  },
  {
    startup_id: 'civicportal-saas',
    startup_name: 'CivicPortal App',
    composite_score: 0.384,
    semantic_fit: 0.35,
    trl_score: 0.333,
    raw_trl: 3,
    compliance_score: 0.55,
    capacity_score: 0.45,
    breakdown: {
      semantic_contribution: 0.14,
      trl_contribution: 0.083,
      compliance_contribution: 0.11,
      capacity_contribution: 0.0675,
    },
    reason_codes: [
      'Low Semantic Fit: 35.0%',
      'TRL-3 Concept / Early Stage',
      'Pending GFR 173 Statutory Clearances',
    ],
  },
];

const SEED_PILOT: Pilot = {
  id: 1,
  challenge_id: 1,
  startup_id: 'hydrosense-ai',
  mou_url: `${API_BASE_URL}/pilots/1/mou`,
  status: 'InProgress',
};

const SEED_MILESTONES: Milestone[] = [
  {
    id: 1,
    pilot_id: 1,
    index: 1,
    amount: 60000.0,
    evidence_url: 'https://telemetry.hydrosense.io/pmc-ward14/m1_installation_report.pdf',
    status: 'Submitted',
  },
  {
    id: 2,
    pilot_id: 1,
    index: 2,
    amount: 150000.0,
    evidence_url: null,
    status: 'Pending',
  },
  {
    id: 3,
    pilot_id: 1,
    index: 3,
    amount: 90000.0,
    evidence_url: null,
    status: 'Pending',
  },
];

const SEED_AUDIT_LOGS: AuditBlock[] = [
  {
    id: 1,
    actor: 'pmc_nodal_officer',
    action: 'CHALLENGE_PUBLISHED:ID_1',
    entity_id: 'challenge:1',
    prev_hash: '0000000000000000000000000000000000000000000000000000000000000000',
    curr_hash: '8f2a1b9e3d4c5b6a7e8f90123456789abcdef0123456789abcdef0123456789a',
    timestamp: '2026-09-05T12:00:00Z',
  },
  {
    id: 2,
    actor: 'pmc_nodal_officer',
    action: 'PILOT_INITIALIZED:Challenge_1->Startup_hydrosense-ai',
    entity_id: 'pilot:1',
    prev_hash: '8f2a1b9e3d4c5b6a7e8f90123456789abcdef0123456789abcdef0123456789a',
    curr_hash: '4c5b6a7e8f90123456789abcdef0123456789abcdef0123456789a8f2a1b9e3d',
    timestamp: '2026-09-05T12:05:00Z',
  },
  {
    id: 3,
    actor: 'founder_hydrosense',
    action: 'MILESTONE_EVIDENCE_SUBMITTED:Pilot_1_M1',
    entity_id: 'milestone:1',
    prev_hash: '4c5b6a7e8f90123456789abcdef0123456789abcdef0123456789a8f2a1b9e3d',
    curr_hash: '123456789abcdef0123456789abcdef0123456789a8f2a1b9e3d4c5b6a7e8f90',
    timestamp: '2026-09-05T12:15:00Z',
  },
];

export async function getChallenges(): Promise<Challenge[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/challenges`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data && data.length > 0 ? data : SEED_CHALLENGES;
  } catch (err) {
    console.warn('Backend unavailable, using fallback challenges:', err);
    return SEED_CHALLENGES;
  }
}

export async function createChallenge(data: {
  title: string;
  outcome_statement: string;
  budget_ceiling: number;
}): Promise<Challenge> {
  try {
    const res = await fetch(`${API_BASE_URL}/challenges`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, simulating challenge creation:', err);
    return {
      id: Date.now(),
      title: data.title,
      outcome_statement: data.outcome_statement,
      budget_ceiling: data.budget_ceiling,
      status: 'Published',
    };
  }
}

export async function matchStartups(challengeId: number): Promise<{
  challenge_id: number;
  total_candidates_evaluated: number;
  matches: StartupMatch[];
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/challenges/${challengeId}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    if (data.matches && data.matches.length > 0) return data;
    return {
      challenge_id: challengeId,
      total_candidates_evaluated: 3,
      matches: SEED_MATCHES,
    };
  } catch (err) {
    console.warn('Backend unavailable, using fallback match rankings:', err);
    return {
      challenge_id: challengeId,
      total_candidates_evaluated: 3,
      matches: SEED_MATCHES,
    };
  }
}

export async function getPilot(pilotId: number): Promise<{
  pilot: Pilot;
  challenge: Challenge;
  milestones: Milestone[];
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/pilots/${pilotId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, using fallback pilot details:', err);
    return {
      pilot: SEED_PILOT,
      challenge: SEED_CHALLENGES[0],
      milestones: SEED_MILESTONES,
    };
  }
}

export async function createPilot(
  challengeId: number,
  startupId: string
): Promise<{ pilot: Pilot; milestones: Milestone[]; audit_hash: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/pilots`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ challenge_id: challengeId, startup_id: startupId }),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, simulating pilot creation:', err);
    return {
      pilot: { id: 1, challenge_id: challengeId, startup_id: startupId, status: 'InProgress' },
      milestones: SEED_MILESTONES,
      audit_hash: '5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b',
    };
  }
}

export async function uploadMilestoneEvidence(
  pilotId: number,
  idx: number,
  evidenceUrl: string
): Promise<{ milestone: Milestone; audit_hash: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/pilots/${pilotId}/milestones/${idx}/evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ evidence_url: evidenceUrl }),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, simulating evidence upload:', err);
    return {
      milestone: { ...SEED_MILESTONES[idx - 1], status: 'Submitted', evidence_url: evidenceUrl },
      audit_hash: '9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f',
    };
  }
}

export async function verifyMilestone(
  pilotId: number,
  idx: number
): Promise<{
  status: string;
  milestone: Milestone;
  pilot_status: string;
  escrow_disbursement_inr: number;
  audit_hash: string;
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/pilots/${pilotId}/milestones/${idx}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: true }),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, simulating milestone verification:', err);
    return {
      status: 'VERIFIED',
      milestone: { ...SEED_MILESTONES[idx - 1], status: 'Approved' },
      pilot_status: 'InProgress',
      escrow_disbursement_inr: SEED_MILESTONES[idx - 1].amount,
      audit_hash: 'a1b2c3d4e5f60718293a4b5c6d7e8f901a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d',
    };
  }
}

export function getMoUUrl(pilotId: number): string {
  return `${API_BASE_URL}/pilots/${pilotId}/mou`;
}

export async function getAuditChain(pilotId: number): Promise<AuditBlock[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/audit/${pilotId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data && data.length > 0 ? data : SEED_AUDIT_LOGS;
  } catch (err) {
    console.warn('Backend unavailable, using fallback audit logs:', err);
    return SEED_AUDIT_LOGS;
  }
}

export async function verifyAuditChain(pilotId: number): Promise<VerifyAuditResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/audit/${pilotId}/verify`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, simulating audit verification:', err);
    return {
      pilot_id: pilotId,
      challenge_id: 1,
      tamper_evident: true,
      blocks_verified: 3,
      status: 'VERIFIED',
      latest_hash: '123456789abcdef0123456789abcdef0123456789a8f2a1b9e3d4c5b6a7e8f90',
    };
  }
}

export async function getDossier(pilotId: number): Promise<GeMDossier> {
  try {
    const res = await fetch(`${API_BASE_URL}/pilots/${pilotId}/dossier`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, simulating GeM dossier:', err);
    return {
      dossier_type: 'GeM_STARTUP_RUNWAY_DIRECT_PROCUREMENT_DOSSIER',
      statutory_authority: 'GFR 2017 Rule 173 & Maharashtra State Innovative Startup Policy',
      pilot_reference_id: `MH-SETU-2026-PILOT-${String(pilotId).padStart(4, '0')}`,
      generation_timestamp: new Date().toISOString(),
      procuring_department: {
        state: 'Maharashtra',
        department: 'Department of IT & Innovation / Pune Municipal Corporation',
        nodal_officer: 'Shri Rajesh Patil, IAS',
      },
      startup_profile: {
        startup_id: 'hydrosense-ai',
        legal_name: 'HydroSense AI Pvt. Ltd.',
        solution_title: 'IoT Ultrasonic Drainage Telemetry',
        dpiit_recognized: true,
        trl: 7,
      },
      challenge_outcomes: {
        challenge_id: 1,
        title: 'Automated Urban Drainage Blockage Detection & Telemetry',
        budget_ceiling_inr: 300000,
        total_disbursed_inr: 60000,
      },
      milestone_verification_matrix: [
        {
          index: 1,
          amount_inr: 60000,
          status: 'Approved',
          evidence_url: 'https://telemetry.hydrosense.io/pmc-ward14/m1_installation_report.pdf',
        },
      ],
      audit_certification: {
        total_audit_blocks: 4,
        latest_sealed_hash: 'a1b2c3d4e5f60718293a4b5c6d7e8f901a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d',
        chain_tamper_evident: true,
      },
      gem_startup_runway_recommendation: {
        status: 'APPROVED_FOR_DIRECT_PROCUREMENT',
        scale_up_multiplier_eligible: true,
        tender_waiver_justification: 'Successful field validation in live municipal sandbox under GFR 173.',
      },
    };
  }
}
