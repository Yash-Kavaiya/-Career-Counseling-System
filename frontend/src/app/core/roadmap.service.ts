import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';
import { RoadmapEnvelope } from './roadmap.models';

@Injectable({ providedIn: 'root' })
export class RoadmapService {
  private http = inject(HttpClient);

  generate(): Observable<RoadmapEnvelope> {
    return this.http.post<RoadmapEnvelope>(`${API_BASE}/api/roadmap/generate`, {});
  }

  get(): Observable<RoadmapEnvelope> {
    return this.http.get<RoadmapEnvelope>(`${API_BASE}/api/roadmap`);
  }

  toggleMilestone(
    itemIndex: number,
    milestoneIndex: number,
    done: boolean,
  ): Observable<RoadmapEnvelope> {
    return this.http.patch<RoadmapEnvelope>(`${API_BASE}/api/roadmap/milestone`, {
      item_index: itemIndex,
      milestone_index: milestoneIndex,
      done,
    });
  }
}
