import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';
import { CounselorState, Overview } from './counselor.models';
import { SseService } from './sse.service';

@Injectable({ providedIn: 'root' })
export class CounselorService {
  private http = inject(HttpClient);
  private sse = inject(SseService);

  start(): Observable<CounselorState> {
    return this.http.post<CounselorState>(`${API_BASE}/api/counselor/start`, {});
  }

  latest(): Observable<CounselorState> {
    return this.http.get<CounselorState>(`${API_BASE}/api/counselor/latest`);
  }

  stream(sessionId: string, message: string, signal?: AbortSignal): AsyncGenerator<string> {
    return this.sse.stream('/api/counselor/message', { session_id: sessionId, message }, signal);
  }

  overview(): Observable<Overview> {
    return this.http.get<Overview>(`${API_BASE}/api/me/overview`);
  }
}
