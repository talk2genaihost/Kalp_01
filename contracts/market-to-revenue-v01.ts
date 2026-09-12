export interface MarketSignal {
  signal_id: string;
  category: string;
  geography: string;
  trend: string;
  evidence: string[];
  source: string;
  provider: string;
  observed_at: string;
  confidence: number;
}

export interface Opportunity {
  opportunity_id: string;
  signal_id: string;
  customer_segment: string;
  problem: string;
  opportunity_score: number;
  confidence: number;
}

export interface Action {
  action_id: string;
  opportunity_id: string;
  recommendation: string;
  expected_outcome: string;
}

export interface Campaign {
  campaign_id: string;
  action_id: string;
  creative_id: string;
  channel: string;
}

export interface CustomerResponse {
  response_id: string;
  campaign_id: string;
  customer_id: string;
  response_type: string;
  responded_at: string;
}

export interface Conversion {
  conversion_id: string;
  response_id: string;
  value: number;
}

export interface RevenueEvent {
  revenue_id: string;
  conversion_id: string;
  amount: number;
  currency: string;
  occurred_at: string;
}

export interface Attribution {
  attribution_id: string;
  revenue_id: string;
  opportunity_id: string;
  campaign_id: string;
  attribution_model: "deterministic_origin_100";
  attributed_amount: number;
}

export interface LearningCandidate {
  memory_id: string;
  signal_id: string;
  opportunity_id: string;
  campaign_id: string;
  revenue_id: string;
  lesson: string;
}

export interface MTRVerticalSlice {
  signal: MarketSignal;
  opportunity: Opportunity;
  action: Action;
  campaign: Campaign;
  response: CustomerResponse;
  conversion: Conversion;
  revenue: RevenueEvent;
  attribution: Attribution;
  learning: LearningCandidate;
}

export function assertLineage(slice: MTRVerticalSlice): void {
  if (slice.opportunity.signal_id !== slice.signal.signal_id) throw new Error("Broken signal → opportunity lineage");
  if (slice.action.opportunity_id !== slice.opportunity.opportunity_id) throw new Error("Broken opportunity → action lineage");
  if (slice.campaign.action_id !== slice.action.action_id) throw new Error("Broken action → campaign lineage");
  if (slice.response.campaign_id !== slice.campaign.campaign_id) throw new Error("Broken campaign → response lineage");
  if (slice.conversion.response_id !== slice.response.response_id) throw new Error("Broken response → conversion lineage");
  if (slice.revenue.conversion_id !== slice.conversion.conversion_id) throw new Error("Broken conversion → revenue lineage");
  if (slice.attribution.revenue_id !== slice.revenue.revenue_id) throw new Error("Broken revenue → attribution lineage");
  if (slice.attribution.opportunity_id !== slice.opportunity.opportunity_id) throw new Error("Broken opportunity attribution lineage");
  if (slice.attribution.campaign_id !== slice.campaign.campaign_id) throw new Error("Broken campaign attribution lineage");
  if (slice.learning.revenue_id !== slice.revenue.revenue_id) throw new Error("Broken revenue → learning lineage");
}
