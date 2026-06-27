import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  templateUrl: './login.html',
})
export class Login {
  private auth = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  readonly error = signal('');
  readonly loading = signal(false);

  submit(): void {
    if (!this.email || !this.password) return;
    this.loading.set(true);
    this.error.set('');
    this.auth.login(this.email, this.password).subscribe({
      next: () => {
        this.auth.loadMe().subscribe();
        this.router.navigateByUrl('/dashboard');
      },
      error: (e) => {
        this.error.set(e?.error?.detail ?? 'Could not sign in. Check your credentials.');
        this.loading.set(false);
      },
    });
  }
}
