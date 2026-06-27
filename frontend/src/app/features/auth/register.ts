import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-register',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
})
export class Register {
  private auth = inject(AuthService);
  private router = inject(Router);

  fullName = '';
  email = '';
  password = '';
  consent = false;
  readonly error = signal('');
  readonly loading = signal(false);

  submit(): void {
    if (!this.email || !this.password) return;
    if (this.password.length < 8) {
      this.error.set('Password must be at least 8 characters.');
      return;
    }
    if (!this.consent) {
      this.error.set('Please accept the consent notice to continue.');
      return;
    }
    this.loading.set(true);
    this.error.set('');
    this.auth
      .register({
        email: this.email,
        password: this.password,
        full_name: this.fullName,
        consent_given: this.consent,
      })
      .subscribe({
        next: () => {
          this.auth.loadMe().subscribe();
          this.router.navigateByUrl('/dashboard');
        },
        error: (e) => {
          this.error.set(this.formatError(e));
          this.loading.set(false);
        },
      });
  }

  private formatError(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(', ');
    }
    return 'Could not create your account. Please try again.';
  }
}
