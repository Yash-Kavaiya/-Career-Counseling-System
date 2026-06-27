import { Component, OnInit, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private auth = inject(AuthService);
  private router = inject(Router);

  readonly isAuth = this.auth.isAuthenticated;
  readonly user = this.auth.user;

  readonly nav = [
    { path: '/dashboard', label: 'Home' },
    { path: '/counselor', label: 'Counselor' },
    { path: '/resume', label: 'Resume' },
    { path: '/discovery', label: 'Discovery' },
    { path: '/assessment', label: 'Assessment' },
    { path: '/jobs', label: 'Jobs' },
    { path: '/interview', label: 'Interview' },
    { path: '/roadmap', label: 'Roadmap' },
  ];

  ngOnInit(): void {
    if (this.auth.isAuthenticated() && !this.auth.user()) {
      this.auth.loadMe().subscribe({ error: () => this.auth.logout() });
    }
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
