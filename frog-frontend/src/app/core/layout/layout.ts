import { ChangeDetectionStrategy, Component, computed, signal, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { Avatar } from 'primeng/avatar';
import { Badge } from 'primeng/badge';
import { ButtonModule } from 'primeng/button';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmationService, MessageService } from 'primeng/api';
import { AuthService } from '@core/services';
import { UserRole } from '@core/models';

interface MenuItem {
  label: string;
  icon: string;
  routerLink: string;
}

@Component({
  selector: 'app-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, Avatar, Badge, ButtonModule, ConfirmDialog, ToastModule],
  templateUrl: './layout.html',
  styleUrl: './layout.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [ConfirmationService, MessageService],
})
export class Layout {
  private auth = inject(AuthService);
  private router = inject(Router);
  private confirmationService = inject(ConfirmationService);

  sidebarCollapsed = signal(false);

  currentUser = this.auth.currentUser;
  userRole = this.auth.userRole;

  menuItems = computed<MenuItem[]>(() => {
    const role = this.userRole();
    const base: MenuItem[] = [];

    if (role === UserRole.ESTUDIANTE) {
      base.push(
        { label: 'Mis Cursos', icon: 'pi pi-book', routerLink: '/dashboard/student' },
        { label: 'Mis Envíos', icon: 'pi pi-upload', routerLink: '/dashboard/student/attempts' },
      );
    }

    if (role === UserRole.PROFESOR) {
      base.push(
        { label: 'Mis Cursos', icon: 'pi pi-book', routerLink: '/dashboard/professor' },
        { label: 'Tareas', icon: 'pi pi-file-edit', routerLink: '/dashboard/professor/tasks' },
        { label: 'Reportes', icon: 'pi pi-chart-bar', routerLink: '/dashboard/professor/reports' },
      );
    }

    if (role === UserRole.ADMIN) {
      base.push(
        { label: 'Auditoría', icon: 'pi pi-history', routerLink: '/dashboard/admin' },
        { label: 'Usuarios', icon: 'pi pi-users', routerLink: '/dashboard/admin/users' },
        { label: 'Reportes', icon: 'pi pi-chart-bar', routerLink: '/dashboard/admin/reports' },
      );
    }

    return base;
  });

  logout(): void {
    this.confirmationService.confirm({
      message: '¿Estás seguro de que deseas cerrar sesión?',
      header: 'Confirmar',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        this.auth.logout();
        this.router.navigate(['/login']);
      },
    });
  }
}
