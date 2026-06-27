import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';
import { DiscoveryState } from './discovery.models';
import { SseService } from './sse.service';

@Injectable({ providedIn: 'root' })
export class DiscoveryService {
  private http = inject(HttpClient);
  private sse = inject(SseService);

  start(): Observable<DiscoveryState> {
    return this.http.post<DiscoveryState>(`${API_BASE}/api/discovery/start`, {});
  }

  latest(): Observable<DiscoveryState> {
    return this.http.get<DiscoveryState>(`${API_BASE}/api/discovery/latest`);
  }

  stream(sessionId: string, message: string, signal?: AbortSignal): AsyncGenerator<string> {
    return this.sse.stream('/api/discovery/message', { session_id: sessionId, message }, signal);
  }
}
