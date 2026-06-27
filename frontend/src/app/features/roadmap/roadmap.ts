import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { RoadmapService } from '../../core/roadmap.service';
import { Roadmap as RoadmapModel } from '../../core/roadmap.models';
import { DisclaimerBanner } from '../../shared/disclaimer-banner';

@Component({
  selector: 'app-roadmap',
  imports: [RouterLink, DisclaimerBanner],
  templateUrl: './roadmap.html',
})
export class Roadmap implements OnInit {
  private svc = inject(RoadmapService);

  readonly roadmap = signal<RoadmapModel | null>(null);
  readonly loading = signal(true);
  readonly generating = signal(false);
  readonly needs = signal<'' | 'resume' | 'assessment'>('');
  readonly error = signal('');

  readonly totalMilestones = computed(() =>
    this.roadmap()?.items.reduce((n, it) => n + it.milestones.length, 0) ?? 0,
  );
  readonly doneMilestones = computed(() =>
    this.roadmap()?.items.reduce(
      (n, it) => n + it.milestones.filter((m) => m.done).length,
      0,
    ) ?? 0,
  );
  readonly progress = computed(() =>
    this.totalMilestones() ? Math.round((this.doneMilestones() / this.totalMilestones()) * 100) : 0,
  );

  ngOnInit(): void {
    this.svc.get().subscribe({
      next: (e) => {
        this.roadmap.set(e.roadmap);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  generate(): void {
    this.generating.set(true);
    this.error.set('');
    this.needs.set('');
    this.svc.generate().subscribe({
      next: (e) => {
        this.roadmap.set(e.roadmap);
        this.generating.set(false);
      },
      error: (err) => {
        this.generating.set(false);
        const d: string = (err?.error?.detail ?? '').toString().toLowerCase();
        if (d.includes('resume')) this.needs.set('resume');
        else if (d.includes('assessment')) this.needs.set('assessment');
        else this.error.set(err?.error?.detail || 'Could not build your roadmap.');
      },
    });
  }

  toggle(itemIndex: number, milestoneIndex: number, done: boolean): void {
    this.svc.toggleMilestone(itemIndex, milestoneIndex, done).subscribe({
      next: (e) => this.roadmap.set(e.roadmap),
    });
  }
}
