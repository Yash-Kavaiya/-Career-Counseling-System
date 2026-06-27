import { ChatMessage } from './discovery.models';

export interface RubricScores {
  correctness: number;
  clarity: number;
  depth: number;
  structure: number;
  communication: number;
}

export interface FeedbackItem {
  question: string;
  answer: string;
  overall: number;
  scores: RubricScores;
  strengths: string[];
  improvements: string[];
  better_answer: string;
}

export interface InterviewState {
  session_id: string;
  target_role: string;
  messages: ChatMessage[];
  feedbacks: FeedbackItem[];
  readiness: number;
  turns: number;
}
