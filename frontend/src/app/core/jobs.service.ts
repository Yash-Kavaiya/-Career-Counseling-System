import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';
import { JDPaste, JobOut, MatchView } from './jobs.models';

@Injectable({ providedIn: 'root' })
export class JobsService {
  private http = inject(HttpClient);

  match(): Observable<MatchView[]> {
    return this.http.get<MatchView[]>(`${API_BASE}/api/jobs/match`);
  }

  list(): Observable<JobOut[]> {
    return this.http.get<JobOut[]>(`${API_BASE}/api/jobs`);
  }

  paste(body: JDPaste): Observable<JobOut> {
    return this.http.post<JobOut>(`${API_BASE}/api/jobs/paste`, body);
  }
}
