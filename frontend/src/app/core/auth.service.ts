import { computed, Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

import { API_BASE } from './config';
import { RegisterPayload, Token, User } from './models';

const TOKEN_KEY = 'cc_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);

  readonly token = signal<string | null>(localStorage.getItem(TOKEN_KEY));
  readonly user = signal<User | null>(null);
  readonly isAuthenticated = computed(() => this.token() !== null);

  register(payload: RegisterPayload): Observable<Token> {
    return this.http
      .post<Token>(`${API_BASE}/api/auth/register`, payload)
      .pipe(tap((t) => this.setToken(t.access_token)));
  }

  login(email: string, password: string): Observable<Token> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);
    return this.http
      .post<Token>(`${API_BASE}/api/auth/login`, body.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(tap((t) => this.setToken(t.access_token)));
  }

  loadMe(): Observable<User> {
    return this.http
      .get<User>(`${API_BASE}/api/auth/me`)
      .pipe(tap((u) => this.user.set(u)));
  }

  setToken(token: string): void {
    this.token.set(token);
    localStorage.setItem(TOKEN_KEY, token);
  }

  logout(): void {
    this.token.set(null);
    this.user.set(null);
    localStorage.removeItem(TOKEN_KEY);
  }
}
