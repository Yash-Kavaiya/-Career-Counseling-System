export interface Resource {
  name: string;
  url?: string | null;
  type: string;
  is_free: boolean;
}

export interface Milestone {
  title: string;
  done: boolean;
}

export interface RoadmapItem {
  priority: number;
  title: string;
  gap: string;
  action: string;
  why_it_matters: string;
  estimated_weeks: number;
  resources: Resource[];
  milestones: Milestone[];
}

export interface Roadmap {
  target_role: string;
  summary: string;
  items: RoadmapItem[];
}

export interface RoadmapEnvelope {
  roadmap: Roadmap;
  saved: boolean;
}
