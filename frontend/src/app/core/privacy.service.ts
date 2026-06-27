import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE } from './config';

@Injectable({ providedIn: 'root' })
export class PrivacyService {
  private http = inject(HttpClient);

  export(): Observable<unknown> {
    return this.http.get(`${API_BASE}/api/me/export`);
  }

  deleteAccount(): Observable<void> {
    return this.http.delete<void>(`${API_BASE}/api/me`);
  }
}
