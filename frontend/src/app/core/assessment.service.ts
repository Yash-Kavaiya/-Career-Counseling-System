import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';
import { AssessmentEnvelope } from './assessment.models';

@Injectable({ providedIn: 'root' })
export class AssessmentService {
  private http = inject(HttpClient);

  run(): Observable<AssessmentEnvelope> {
    return this.http.post<AssessmentEnvelope>(`${API_BASE}/api/assessment/run`, {});
  }

  get(): Observable<AssessmentEnvelope> {
    return this.http.get<AssessmentEnvelope>(`${API_BASE}/api/assessment`);
  }
}
