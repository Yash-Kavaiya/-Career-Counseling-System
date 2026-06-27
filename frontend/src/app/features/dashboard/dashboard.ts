import { Component, OnInit, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { CounselorService } from '../../core/counselor.service';
import { Overview } from '../../core/counselor.models';
import { PrivacyService } from '../../core/privacy.service';
import { DisclaimerBanner } from '../../shared/disclaimer-banner';

interface JourneyStep {
  path: string;
  n: number;
  title: string;
  desc: string;
  key: 'resume' | 'discovery' | 'assessment' | 'jobs' | 'interview' | 'roadmap';
}

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, DisclaimerBanner],
  templateUrl: './dashboard.html',
})
export class Dashboard implements OnInit {
  private auth = inject(AuthService);
  private counselor = inject(CounselorService);
  private privacy = inject(PrivacyService);
  private router = inject(Router);

  readonly user = this.auth.user;
  readonly overview = signal<Overview | null>(null);
  readonly exporting = signal(false);

  readonly steps: JourneyStep[] = [
    { path: '/resume', n: 1, key: 'resume', title: 'Parse your resume', desc: 'Upload any resume and get a clean, structured profile with confidence flags you can edit.' },
    { path: '/discovery', n: 2, key: 'discovery', title: 'Discovery chat', desc: 'A counselor-style conversation that fills the gaps and surfaces your real goals and constraints.' },
    { path: '/assessment', n: 3, key: 'assessment', title: 'Strengths & gaps', desc: 'Evidence-based strengths, prioritized gaps with business impact, and a skill radar.' },
    { path: '/jobs', n: 4, key: 'jobs', title: 'Match jobs', desc: 'Roles that fit — each with why it matches, what to emphasize, and what to close first.' },
    { path: '/interview', n: 5, key: 'interview', title: 'Mock interview', desc: 'Adaptive practice with rubric-based scoring and a better-answer outline.' },
    { path: '/roadmap', n: 6, key: 'roadmap', title: 'Learning roadmap', desc: 'A prioritized, time-boxed plan with resources and milestones.' },
  ];

  ngOnInit(): void {
    this.counselor.overview().subscribe({ next: (o) => this.overview.set(o) });
  }

  get firstName(): string {
    const name = this.user()?.full_name?.trim();
    if (name) return name.split(' ')[0];
    return this.user()?.email?.split('@')[0] ?? 'there';
  }

  exportData(): void {
    this.exporting.set(true);
    this.privacy.export().subscribe({
      next: (data) => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'my-career-data.json';
        a.click();
        URL.revokeObjectURL(url);
        this.exporting.set(false);
      },
      error: () => this.exporting.set(false),
    });
  }

  deleteData(): void {
    if (!confirm('Delete your account and ALL your data? This cannot be undone.')) return;
    this.privacy.deleteAccount().subscribe({
      next: () => {
        this.auth.logout();
        this.router.navigateByUrl('/register');
      },
    });
  }

  done(key: JourneyStep['key']): boolean {
    const o = this.overview();
    if (!o) return false;
    switch (key) {
      case 'resume':
        return o.has_profile;
      case 'discovery':
        return o.discovery_turns > 0;
      case 'assessment':
        return o.has_assessment;
      case 'interview':
        return o.interview_turns > 0;
      case 'roadmap':
        return o.has_roadmap;
      default:
        return false;
    }
  }
}
