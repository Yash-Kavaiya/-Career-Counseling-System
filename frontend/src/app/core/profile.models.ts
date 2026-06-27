// Mirrors backend app/schemas/profile.py — the canonical candidate profile.

export type Proficiency = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export interface Achievement {
  description: string;
  metric?: string | null;
}

export interface Experience {
  company: string;
  client?: string | null;
  role: string;
  start?: string | null;
  end?: string | null;
  is_current: boolean;
  location?: string | null;
  tech: string[];
  achievements: Achievement[];
  summary?: string | null;
}

export interface Education {
  degree: string;
  institution: string;
  year?: string | null;
  score?: string | null;
}

export interface Skill {
  name: string;
  category?: string | null;
  proficiency?: Proficiency | null;
  evidence?: string | null;
}

export interface Project {
  name: string;
  description?: string | null;
  tech: string[];
  link?: string | null;
  highlights: string[];
}

export interface Certification {
  name: string;
  issuer?: string | null;
  status?: string | null;
}

export interface Preferences {
  current_ctc?: string | null;
  expected_ctc?: string | null;
  notice_period?: string | null;
  locations: string[];
  remote_preference?: string | null;
  company_types: string[];
  target_roles: string[];
  priorities: string[];
}

export interface CareerGap {
  dates?: string | null;
  reason?: string | null;
  activities?: string | null;
}

export interface UncertaintyFlag {
  field: string;
  reason: string;
  confidence: number;
}

export interface CandidateProfile {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  links: string[];
  headline?: string | null;
  summary?: string | null;
  total_experience_years?: number | null;
  experiences: Experience[];
  education: Education[];
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
  preferences: Preferences;
  career_gaps: CareerGap[];
  uncertainty_flags: UncertaintyFlag[];
}

export interface ProfileEnvelope {
  profile: CandidateProfile;
  version: number;
  saved: boolean;
}

export function emptyPreferences(): Preferences {
  return {
    current_ctc: null,
    expected_ctc: null,
    notice_period: null,
    locations: [],
    remote_preference: null,
    company_types: [],
    target_roles: [],
    priorities: [],
  };
}
