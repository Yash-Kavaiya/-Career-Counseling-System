import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';
import { InterviewState } from './interview.models';
import { SseService } from './sse.service';

@Injectable({ providedIn: 'root' })
export class InterviewService {
  private http = inject(HttpClient);
  private sse = inject(SseService);

  start(): Observable<InterviewState> {
    return this.http.post<InterviewState>(`${API_BASE}/api/interview/start`, {});
  }

  latest(): Observable<InterviewState> {
    return this.http.get<InterviewState>(`${API_BASE}/api/interview/latest`);
  }

  stream(sessionId: string, message: string, signal?: AbortSignal): AsyncGenerator<string> {
    return this.sse.stream('/api/interview/message', { session_id: sessionId, message }, signal);
  }
}
