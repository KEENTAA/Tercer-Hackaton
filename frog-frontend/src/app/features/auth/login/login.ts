import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { CardModule } from 'primeng/card';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { AuthService } from '@core/services';
import { UserRole } from '@core/models';

@Component({
  selector: 'app-login',
  imports: [
    ReactiveFormsModule,
    ButtonModule,
    InputTextModule,
    PasswordModule,
    CardModule,
    ToastModule,
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [MessageService],
})
export class Login {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);
  private messageService = inject(MessageService);

  loginForm: FormGroup = this.fb.group({
    codigo_universitario: ['', [Validators.required]],
    password: ['', [Validators.required, Validators.minLength(6)]],
  });

  loading = signal(false);

  get codigo() {
    return this.loginForm.get('codigo_universitario');
  }

  get password() {
    return this.loginForm.get('password');
  }

  async onSubmit(): Promise<void> {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.loading.set(true);

    try {
      const user = await this.auth.login(this.loginForm.value);
      const route = this.getRouteByRole(user.rol);
      this.router.navigate([route]);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Código universitario o contraseña incorrectos',
      });
    } finally {
      this.loading.set(false);
    }
  }

  private getRouteByRole(role: UserRole): string {
    switch (role) {
      case UserRole.ESTUDIANTE:
        return '/dashboard/student';
      case UserRole.PROFESOR:
        return '/dashboard/professor';
      case UserRole.ADMIN:
        return '/dashboard/admin';
      default:
        return '/dashboard';
    }
  }
}
