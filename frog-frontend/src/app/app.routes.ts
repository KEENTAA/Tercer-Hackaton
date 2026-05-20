import { Routes } from '@angular/router';
import { authGuard } from '@core/guards/auth.guard';
import { roleGuard } from '@core/guards/role.guard';
import { UserRole } from '@core/models';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('@features/auth/login/login').then((m) => m.Login),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('@core/layout/layout').then((m) => m.Layout),
    canActivate: [authGuard],
    children: [
      {
        path: 'student',
        loadComponent: () =>
          import('@features/private/student-dashboard/student-dashboard').then(
            (m) => m.StudentDashboard,
          ),
        canActivate: [roleGuard(UserRole.ESTUDIANTE)],
      },
      {
        path: 'professor',
        loadComponent: () =>
          import('@features/private/professor-dashboard/professor-dashboard').then(
            (m) => m.ProfessorDashboard,
          ),
        canActivate: [roleGuard(UserRole.PROFESOR)],
      },
      {
        path: 'admin',
        loadComponent: () =>
          import('@features/private/admin-dashboard/admin-dashboard').then(
            (m) => m.AdminDashboard,
          ),
        canActivate: [roleGuard(UserRole.ADMIN)],
      },
      {
        path: '',
        redirectTo: 'student',
        pathMatch: 'full',
      },
    ],
  },
  {
    path: '404',
    loadComponent: () =>
      import('@features/public/not-found/not-found').then((m) => m.NotFound),
  },
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: '404',
  },
];
