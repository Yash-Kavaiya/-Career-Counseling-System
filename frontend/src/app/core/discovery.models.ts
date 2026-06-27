export interface Topic {
  key: string;
  label: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface DiscoveryState {
  session_id: string;
  stage: string;
  all_topics: Topic[];
  covered_topics: string[];
  key_insights: string[];
  pending_questions: string[];
  turns: number;
  messages: ChatMessage[];
}
