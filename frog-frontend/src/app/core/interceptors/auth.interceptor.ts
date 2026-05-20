import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '@core/services';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.getToken();

  if (token) {
    const cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
    return next(cloned).pipe(
      catchError((error: HttpErrorResponse) => handleError(error)),
    );
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => handleError(error)),
  );
};

function handleError(error: HttpErrorResponse) {
  const router = inject(Router);
  const auth = inject(AuthService);

  if (error.status === 401) {
    auth.logout();
    router.navigate(['/login']);
  }

  return throwError(() => error);
}
