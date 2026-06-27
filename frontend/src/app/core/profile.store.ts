import { Injectable, computed, inject, signal } from '@angular/core';

import { CandidateProfile } from './profile.models';
import { ResumeService } from './resume.service';

/** App-wide cache of the current candidate profile (shared by later steps). */
@Injectable({ providedIn: 'root' })
export class ProfileStore {
  private resume = inject(ResumeService);

  readonly profile = signal<CandidateProfile | null>(null);
  readonly loaded = signal(false);
  readonly hasProfile = computed(() => this.profile() !== null);

  /** Load once from the backend if not already loaded. */
  ensureLoaded(): void {
    if (this.loaded()) return;
    this.resume.get().subscribe({
      next: (e) => {
        this.profile.set(e.profile);
        this.loaded.set(true);
      },
      error: () => this.loaded.set(true),
    });
  }

  set(profile: CandidateProfile): void {
    this.profile.set(profile);
    this.loaded.set(true);
  }
}
