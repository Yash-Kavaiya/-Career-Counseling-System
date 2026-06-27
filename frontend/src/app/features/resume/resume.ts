import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { ProfileStore } from '../../core/profile.store';
import { ResumeService } from '../../core/resume.service';
import {
  Achievement,
  CandidateProfile,
  Experience,
  Proficiency,
} from '../../core/profile.models';
import { DisclaimerBanner } from '../../shared/disclaimer-banner';

type Status = 'upload' | 'parsing' | 'review' | 'saving' | 'saved';

@Component({
  selector: 'app-resume',
  imports: [FormsModule, DisclaimerBanner, DecimalPipe],
  templateUrl: './resume.html',
})
export class Resume implements OnInit {
  private resume = inject(ResumeService);
  private store = inject(ProfileStore);
  private router = inject(Router);

  readonly status = signal<Status>('upload');
  readonly error = signal('');
  readonly version = signal(1);
  readonly dragOver = signal(false);
  readonly proficiencies: Proficiency[] = ['beginner', 'intermediate', 'advanced', 'expert'];

  file: File | null = null;
  fileName = '';
  profile: CandidateProfile | null = null;

  ngOnInit(): void {
    this.resume.get().subscribe({
      next: (e) => {
        this.profile = e.profile;
        this.version.set(e.version);
        this.store.set(e.profile);
        this.status.set('review');
      },
      error: () => {
        /* no profile yet — stay on upload */
      },
    });
  }

  pickFile(input: HTMLInputElement): void {
    const f = input.files?.[0];
    if (f) {
      this.file = f;
      this.fileName = f.name;
    }
  }

  onDrop(ev: DragEvent): void {
    ev.preventDefault();
    this.dragOver.set(false);
    const f = ev.dataTransfer?.files?.[0];
    if (f) {
      this.file = f;
      this.fileName = f.name;
    }
  }

  parse(): void {
    if (!this.file) return;
    this.status.set('parsing');
    this.error.set('');
    this.resume.parse(this.file).subscribe({
      next: (e) => {
        this.profile = e.profile;
        this.status.set('review');
      },
      error: (e) => {
        this.error.set(this.fmt(e, 'Could not parse the resume. Try another file.'));
        this.status.set('upload');
      },
    });
  }

  save(thenDiscovery: boolean): void {
    if (!this.profile) return;
    this.status.set('saving');
    this.error.set('');
    this.resume.save(this.profile).subscribe({
      next: (e) => {
        this.version.set(e.version);
        this.store.set(e.profile);
        this.status.set('saved');
        if (thenDiscovery) this.router.navigateByUrl('/discovery');
      },
      error: (e) => {
        this.error.set(this.fmt(e, 'Could not save your profile.'));
        this.status.set('review');
      },
    });
  }

  reupload(): void {
    this.file = null;
    this.fileName = '';
    this.status.set('upload');
  }

  // ---- editing helpers ----
  addExperience(): void {
    this.profile?.experiences.unshift({
      company: '',
      role: '',
      client: null,
      start: null,
      end: null,
      is_current: false,
      location: null,
      tech: [],
      achievements: [],
      summary: null,
    });
  }
  removeExperience(i: number): void {
    this.profile?.experiences.splice(i, 1);
  }
  addAchievement(e: Experience): void {
    e.achievements.push({ description: '', metric: null });
  }
  removeAchievement(e: Experience, i: number): void {
    e.achievements.splice(i, 1);
  }
  addSkill(): void {
    this.profile?.skills.push({ name: '', proficiency: 'intermediate', category: null, evidence: null });
  }
  removeSkill(i: number): void {
    this.profile?.skills.splice(i, 1);
  }
  addEducation(): void {
    this.profile?.education.push({ degree: '', institution: '', year: null, score: null });
  }
  removeEducation(i: number): void {
    this.profile?.education.splice(i, 1);
  }

  techStr(e: Experience): string {
    return e.tech.join(', ');
  }
  setTech(e: Experience, v: string): void {
    e.tech = v.split(',').map((s) => s.trim()).filter(Boolean);
  }
  listStr(v: string[]): string {
    return v.join(', ');
  }
  setPrefList(
    key: 'locations' | 'target_roles' | 'company_types' | 'priorities',
    v: string,
  ): void {
    if (this.profile) {
      this.profile.preferences[key] = v.split(',').map((s) => s.trim()).filter(Boolean);
    }
  }

  trackByIndex(i: number): number {
    return i;
  }

  private fmt(e: unknown, fallback: string): string {
    const d = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof d === 'string' ? d : fallback;
  }
}
