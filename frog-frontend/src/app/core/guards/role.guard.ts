import { inject } from '@angular/core';
import { Router, type CanActivateFn } from '@angular/router';
import { AuthService } from '@core/services';
import { UserRole } from '@core/models';

export const roleGuard = (...roles: UserRole[]): CanActivateFn => {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const userRole = auth.userRole();

    if (!userRole || !roles.includes(userRole)) {
      router.navigate(['/dashboard']);
      return false;
    }

    return true;
  };
};
