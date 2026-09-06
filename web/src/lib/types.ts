export interface Challenge {
  id: number;
  title: string;
  outcome_statement: string;
  budget_ceiling: number;
  status: string;
}

export interface MatchBreakdown {
  semantic_contribution: number;
  trl_contribution: number;
  compliance_contribution: number;
  capacity_contribution: number;
}

export interface StartupMatch {
  startup_id: string;
  startup_name: string;
  composite_score: number;
  semantic_fit: number;
  trl_score: number;
  raw_trl: number;
  compliance_score: number;
  capacity_score: number;
  breakdown: MatchBreakdown;
  reason_codes: string[];
}

export interface Milestone {
  id: number;
  pilot_id: number;
  index: number;
  amount: number;
  evidence_url?: string | null;
  status: 'Pending' | 'Submitted' | 'InReview' | 'Approved' | 'Rejected' | 'Disbursed';
}

export interface Pilot {
  id: number;
  challenge_id: number;
  startup_id: string;
  mou_url?: string | null;
  status: 'PilotApproved' | 'MoUSigned' | 'InProgress' | 'MilestoneReview' | 'ScaleUpRecommended' | 'Closed';
}

export interface AuditBlock {
  id: number;
  actor: string;
  action: string;
  entity_id: string;
  prev_hash: string;
  curr_hash: string;
  timestamp: string;
}

export interface VerifyAuditResponse {
  pilot_id: number;
  challenge_id: number;
  tamper_evident: boolean;
  blocks_verified: number;
  status: string;
  latest_hash: string | null;
}

export interface GeMDossier {
  dossier_type: string;
  statutory_authority: string;
  pilot_reference_id: string;
  generation_timestamp: string;
  procuring_department: {
    state: string;
    department: string;
    nodal_officer: string;
  };
  startup_profile: {
    startup_id: string;
    legal_name: string;
    solution_title: string;
    dpiit_recognized: boolean;
    trl: number;
  };
  challenge_outcomes: {
    challenge_id: number | null;
    title: string;
    budget_ceiling_inr: number;
    total_disbursed_inr: number;
  };
  milestone_verification_matrix: Array<{
    index: number;
    amount_inr: number;
    status: string;
    evidence_url?: string | null;
  }>;
  audit_certification: {
    total_audit_blocks: number;
    latest_sealed_hash: string | null;
    chain_tamper_evident: boolean;
  };
  gem_startup_runway_recommendation: {
    status: string;
    scale_up_multiplier_eligible: boolean;
    tender_waiver_justification: string;
  };
}
