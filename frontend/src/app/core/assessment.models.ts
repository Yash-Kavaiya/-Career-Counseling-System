export interface RadarAxis {
  axis: string;
  score: number;
  target: number;
}

export interface Strength {
  title: string;
  evidence: string;
}

export type Severity = 'low' | 'medium' | 'high' | 'critical';

export interface Gap {
  title: string;
  severity: Severity;
  business_impact: string;
  how_to_close: string;
}

export interface Assessment {
  target_role: string;
  level: string;
  summary: string;
  readiness_score: number;
  radar: RadarAxis[];
  strengths: Strength[];
  gaps: Gap[];
}

export interface AssessmentEnvelope {
  assessment: Assessment;
  saved: boolean;
}
