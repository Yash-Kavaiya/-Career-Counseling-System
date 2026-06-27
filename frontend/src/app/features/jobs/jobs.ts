import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { JobsService } from '../../core/jobs.service';
import { MatchView } from '../../core/jobs.models';
import { DisclaimerBanner } from '../../shared/disclaimer-banner';

@Component({
  selector: 'app-jobs',
  imports: [FormsModule, RouterLink, DisclaimerBanner],
  templateUrl: './jobs.html',
})
export class Jobs implements OnInit {
  private svc = inject(JobsService);

  readonly matches = signal<MatchView[]>([]);
  readonly loading = signal(true);
  readonly noProfile = signal(false);
  readonly error = signal('');
  readonly remoteFilter = signal<string>('all');
  readonly showPaste = signal(false);
  readonly pasting = signal(false);

  pTitle = '';
  pCompany = '';
  pText = '';

  readonly filters = ['all', 'remote', 'hybrid', 'onsite'];
  readonly filtered = computed(() => {
    const f = this.remoteFilter();
    const all = this.matches();
    return f === 'all' ? all : all.filter((m) => m.job.remote === f);
  });

  ngOnInit(): void {
    this.run();
  }

  run(): void {
    this.loading.set(true);
    this.error.set('');
    this.svc.match().subscribe({
      next: (m) => {
        this.matches.set(m);
        this.loading.set(false);
      },
      error: (e) => {
        this.loading.set(false);
        const d = e?.error?.detail ?? '';
        if (typeof d === 'string' && d.toLowerCase().includes('resume')) {
          this.noProfile.set(true);
        } else {
          this.error.set(d || 'Could not match jobs right now.');
        }
      },
    });
  }

  paste(): void {
    if (!this.pTitle.trim() || !this.pText.trim()) return;
    this.pasting.set(true);
    this.svc
      .paste({ title: this.pTitle, company: this.pCompany, jd_text: this.pText, location: '', remote: '' })
      .subscribe({
        next: () => {
          this.pTitle = '';
          this.pCompany = '';
          this.pText = '';
          this.showPaste.set(false);
          this.pasting.set(false);
          this.run();
        },
        error: () => {
          this.pasting.set(false);
          this.error.set('Could not add that job description.');
        },
      });
  }

  scoreClass(s: number): string {
    if (s >= 85) return 'gb-gradient text-white';
    if (s >= 70) return 'bg-gb-spring/15 text-gb-mint';
    return 'bg-amber-100 text-amber-700';
  }
}
