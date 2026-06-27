import {
  AfterViewChecked,
  Component,
  ElementRef,
  OnInit,
  computed,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ChatMessage } from '../../core/discovery.models';
import { InterviewService } from '../../core/interview.service';
import { FeedbackItem, InterviewState, RubricScores } from '../../core/interview.models';

@Component({
  selector: 'app-interview',
  imports: [FormsModule, RouterLink],
  templateUrl: './interview.html',
})
export class Interview implements OnInit, AfterViewChecked {
  private svc = inject(InterviewService);
  private scroller = viewChild<ElementRef<HTMLElement>>('scroller');

  readonly state = signal<InterviewState | null>(null);
  readonly messages = signal<ChatMessage[]>([]);
  readonly feedbacks = signal<FeedbackItem[]>([]);
  readonly readiness = signal(0);
  readonly streaming = signal(false);
  readonly starting = signal(false);
  readonly loading = signal(true);
  readonly noProfile = signal(false);
  readonly error = signal('');
  draft = '';
  private shouldScroll = false;

  readonly latestFeedback = computed<FeedbackItem | null>(() => {
    const f = this.feedbacks();
    return f.length ? f[f.length - 1] : null;
  });

  readonly rubricRows: { key: keyof RubricScores; label: string }[] = [
    { key: 'correctness', label: 'Correctness' },
    { key: 'depth', label: 'Depth' },
    { key: 'structure', label: 'Structure' },
    { key: 'clarity', label: 'Clarity' },
    { key: 'communication', label: 'Communication' },
  ];

  ngOnInit(): void {
    this.svc.latest().subscribe({
      next: (s) => {
        this.applyState(s);
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

  private applyState(s: InterviewState): void {
    this.state.set(s);
    this.messages.set(s.messages);
    this.feedbacks.set(s.feedbacks);
    this.readiness.set(s.readiness);
    this.shouldScroll = true;
  }

  start(): void {
    this.starting.set(true);
    this.error.set('');
    this.svc.start().subscribe({
      next: (s) => {
        this.applyState(s);
        this.starting.set(false);
      },
      error: (e) => {
        this.starting.set(false);
        const d = e?.error?.detail ?? '';
        if (typeof d === 'string' && d.toLowerCase().includes('resume')) this.noProfile.set(true);
        else this.error.set(d || 'Could not start the interview.');
      },
    });
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
        } else if (evt['done']) {
          if (evt['feedback']) {
            const fb = evt['feedback'] as Omit<FeedbackItem, 'question' | 'answer'>;
            this.feedbacks.update((f) => [...f, { question: '', answer: text, ...fb } as FeedbackItem]);
          }
          if (typeof evt['readiness'] === 'number') this.readiness.set(evt['readiness'] as number);
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

  scoreColor(v: number): string {
    if (v >= 7) return 'bg-gb-mint';
    if (v >= 4) return 'bg-amber-400';
    return 'bg-red-400';
  }
}
