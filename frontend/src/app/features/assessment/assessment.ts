import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { AssessmentService } from '../../core/assessment.service';
import { Assessment as AssessmentModel, Severity } from '../../core/assessment.models';
import { DisclaimerBanner } from '../../shared/disclaimer-banner';
import { RadarChart } from '../../shared/radar-chart';

@Component({
  selector: 'app-assessment',
  imports: [RouterLink, DisclaimerBanner, RadarChart],
  templateUrl: './assessment.html',
})
export class Assessment implements OnInit {
  private svc = inject(AssessmentService);

  readonly assessment = signal<AssessmentModel | null>(null);
  readonly loading = signal(true);
  readonly running = signal(false);
  readonly noProfile = signal(false);
  readonly error = signal('');

  private readonly severityClasses: Record<Severity, string> = {
    critical: 'bg-red-100 text-red-700',
    high: 'bg-orange-100 text-orange-700',
    medium: 'bg-amber-100 text-amber-700',
    low: 'bg-gray-100 text-gray-600',
  };

  ngOnInit(): void {
    this.svc.get().subscribe({
      next: (e) => {
        this.assessment.set(e.assessment);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  run(): void {
    this.running.set(true);
    this.error.set('');
    this.svc.run().subscribe({
      next: (e) => {
        this.assessment.set(e.assessment);
        this.running.set(false);
      },
      error: (err) => {
        this.running.set(false);
        const d = err?.error?.detail ?? '';
        if (typeof d === 'string' && d.toLowerCase().includes('resume')) {
          this.noProfile.set(true);
        } else {
          this.error.set(d || 'Could not generate your assessment.');
        }
      },
    });
  }

  severityClass(s: Severity): string {
    return this.severityClasses[s];
  }
}
