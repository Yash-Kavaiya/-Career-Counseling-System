import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';
import { CandidateProfile, ProfileEnvelope } from './profile.models';

@Injectable({ providedIn: 'root' })
export class ResumeService {
  private http = inject(HttpClient);

  parse(file: File): Observable<ProfileEnvelope> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<ProfileEnvelope>(`${API_BASE}/api/resume/parse`, form);
  }

  save(profile: CandidateProfile): Observable<ProfileEnvelope> {
    return this.http.put<ProfileEnvelope>(`${API_BASE}/api/resume/profile`, profile);
  }

  get(): Observable<ProfileEnvelope> {
    return this.http.get<ProfileEnvelope>(`${API_BASE}/api/resume/profile`);
  }
}
