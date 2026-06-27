import { Routes } from '@angular/router';

import { authGuard } from './core/auth.guard';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login').then((m) => m.Login),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register').then((m) => m.Register),
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/dashboard/dashboard').then((m) => m.Dashboard),
  },
  {
    path: 'resume',
    canActivate: [authGuard],
    loadComponent: () => import('./features/resume/resume').then((m) => m.Resume),
  },
  {
    path: 'discovery',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/discovery/discovery').then((m) => m.Discovery),
  },
  {
    path: 'assessment',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/assessment/assessment').then((m) => m.Assessment),
  },
  {
    path: 'jobs',
    canActivate: [authGuard],
    loadComponent: () => import('./features/jobs/jobs').then((m) => m.Jobs),
  },
  {
    path: 'interview',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/interview/interview').then((m) => m.Interview),
  },
  {
    path: 'roadmap',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/roadmap/roadmap').then((m) => m.Roadmap),
  },
  {
    path: 'counselor',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/counselor/counselor').then((m) => m.Counselor),
  },
  { path: '**', redirectTo: 'dashboard' },
];
