import { ChatMessage } from './discovery.models';

export interface CounselorState {
  session_id: string;
  messages: ChatMessage[];
}

export interface Overview {
  has_profile: boolean;
  profile_name?: string | null;
  has_assessment: boolean;
  readiness?: number | null;
  target_role?: string | null;
  has_roadmap: boolean;
  roadmap_done: number;
  roadmap_total: number;
  discovery_turns: number;
  discovery_covered: number;
  discovery_total: number;
  latest_insight?: string | null;
  interview_turns: number;
}
