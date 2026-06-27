import {
  AfterViewChecked,
  Component,
  ElementRef,
  OnInit,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ChatMessage } from '../../core/discovery.models';
import { CounselorService } from '../../core/counselor.service';
import { CounselorState } from '../../core/counselor.models';

@Component({
  selector: 'app-counselor',
  imports: [FormsModule, RouterLink],
  templateUrl: './counselor.html',
})
export class Counselor implements OnInit, AfterViewChecked {
  private svc = inject(CounselorService);
  private scroller = viewChild<ElementRef<HTMLElement>>('scroller');

  readonly state = signal<CounselorState | null>(null);
  readonly messages = signal<ChatMessage[]>([]);
  readonly streaming = signal(false);
  readonly starting = signal(false);
  readonly loading = signal(true);
  readonly noProfile = signal(false);
  readonly error = signal('');
  draft = '';
  private shouldScroll = false;

  readonly suggestions = [
    'What should I focus on this week?',
    'Am I ready to apply for SDE-2 roles?',
    'How do I explain my career gap in interviews?',
    'Which gap will move the needle most?',
  ];

  ngOnInit(): void {
    this.svc.latest().subscribe({
      next: (s) => {
        this.apply(s);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.shouldScroll = false;
      const el = this.scroller()?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    }
  }

  private apply(s: CounselorState): void {
    this.state.set(s);
    this.messages.set(s.messages);
    this.shouldScroll = true;
  }

  start(): void {
    this.starting.set(true);
    this.error.set('');
    this.svc.start().subscribe({
      next: (s) => {
        this.apply(s);
        this.starting.set(false);
      },
      error: (e) => {
        this.starting.set(false);
        const d = e?.error?.detail ?? '';
        if (typeof d === 'string' && d.toLowerCase().includes('resume')) this.noProfile.set(true);
        else this.error.set(d || 'Could not start the session.');
      },
    });
  }

  ask(text: string): void {
    this.draft = text;
    this.send();
  }

  async send(): Promise<void> {
    const s = this.state();
    const text = this.draft.trim();
    if (!s || !text || this.streaming()) return;
    this.draft = '';
    this.error.set('');
    this.messages.update((m) => [...m, { role: 'user', content: text }, { role: 'assistant', content: '' }]);
    this.streaming.set(true);
    this.shouldScroll = true;

    try {
      for await (const chunk of this.svc.stream(s.session_id, text)) {
        let evt: Record<string, unknown>;
        try {
          evt = JSON.parse(chunk);
        } catch {
          continue;
        }
        if (typeof evt['delta'] === 'string') {
          const delta = evt['delta'] as string;
          this.messages.update((m) => {
            const copy = [...m];
            const last = copy[copy.length - 1];
            copy[copy.length - 1] = { role: 'assistant', content: last.content + delta };
            return copy;
          });
          this.shouldScroll = true;
        } else if (evt['error']) {
          this.error.set(String(evt['error']));
        }
      }
    } catch {
      this.error.set('The connection was interrupted. Please try again.');
    } finally {
      this.streaming.set(false);
      this.shouldScroll = true;
    }
  }
}
