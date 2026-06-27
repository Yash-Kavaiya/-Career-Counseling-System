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
import { Router, RouterLink } from '@angular/router';

import { DiscoveryService } from '../../core/discovery.service';
import { ChatMessage, DiscoveryState } from '../../core/discovery.models';

@Component({
  selector: 'app-discovery',
  imports: [FormsModule, RouterLink],
  templateUrl: './discovery.html',
})
export class Discovery implements OnInit, AfterViewChecked {
  private svc = inject(DiscoveryService);
  private router = inject(Router);

  private scroller = viewChild<ElementRef<HTMLElement>>('scroller');

  readonly state = signal<DiscoveryState | null>(null);
  readonly messages = signal<ChatMessage[]>([]);
  readonly streaming = signal(false);
  readonly starting = signal(false);
  readonly loading = signal(true);
  readonly noProfile = signal(false);
  readonly error = signal('');
  draft = '';
  private shouldScroll = false;

  readonly coveredCount = computed(() => this.state()?.covered_topics.length ?? 0);
  readonly totalTopics = computed(() => this.state()?.all_topics.length ?? 0);
  readonly progress = computed(() =>
    this.totalTopics() ? Math.round((this.coveredCount() / this.totalTopics()) * 100) : 0,
  );

  ngOnInit(): void {
    this.svc.latest().subscribe({
      next: (s) => {
        this.state.set(s);
        this.messages.set(s.messages);
        this.loading.set(false);
        this.shouldScroll = true;
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

  start(): void {
    this.starting.set(true);
    this.error.set('');
    this.svc.start().subscribe({
      next: (s) => {
        this.state.set(s);
        this.messages.set(s.messages);
        this.starting.set(false);
        this.shouldScroll = true;
      },
      error: (e) => {
        this.starting.set(false);
        const detail = e?.error?.detail ?? '';
        if (typeof detail === 'string' && detail.toLowerCase().includes('resume')) {
          this.noProfile.set(true);
        } else {
          this.error.set(detail || 'Could not start the session.');
        }
      },
    });
  }

  isCovered(key: string): boolean {
    return this.state()?.covered_topics.includes(key) ?? false;
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
          this.state.update((st) =>
            st
              ? {
                  ...st,
                  covered_topics: (evt['covered_topics'] as string[]) ?? st.covered_topics,
                  key_insights: (evt['key_insights'] as string[]) ?? st.key_insights,
                  pending_questions: (evt['pending_questions'] as string[]) ?? st.pending_questions,
                  turns: (evt['turns'] as number) ?? st.turns,
                }
              : st,
          );
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
