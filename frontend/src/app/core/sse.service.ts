import { Injectable, inject } from '@angular/core';

import { AuthService } from './auth.service';
import { API_BASE } from './config';

/**
 * Streams a POST endpoint that emits Server-Sent Events (`data:` lines).
 * Uses fetch + ReadableStream so we can send a JSON body and the JWT header
 * (EventSource supports neither). Yields the raw payload string of each event.
 */
@Injectable({ providedIn: 'root' })
export class SseService {
  private auth = inject(AuthService);

  async *stream(
    path: string,
    body: unknown,
    signal?: AbortSignal,
  ): AsyncGenerator<string> {
    const token = this.auth.token();
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
      signal,
    });
    if (!res.ok || !res.body) {
      throw new Error(`Stream failed: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop() ?? '';
      for (const evt of events) {
        for (const line of evt.split('\n')) {
          if (line.startsWith('data:')) {
            const data = line.slice(5).trim();
            if (data === '[DONE]') return;
            yield data;
          }
        }
      }
    }
  }
}
