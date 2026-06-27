export interface JobOut {
  id: number;
  title: string;
  company: string;
  location: string;
  remote: string;
  salary_band: string;
  tech: string[];
  source: string;
}

export interface MatchView {
  job: JobOut;
  fit_score: number;
  reasons: string[];
  missing_pieces: string[];
  talking_points: string[];
}

export interface JDPaste {
  title: string;
  company: string;
  location: string;
  remote: string;
  jd_text: string;
}
