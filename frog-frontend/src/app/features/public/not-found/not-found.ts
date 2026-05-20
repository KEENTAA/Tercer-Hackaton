import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-not-found',
  imports: [ButtonModule],
  template: `
    <div class="not-found">
      <div class="not-found-content">
        <h1 class="error-code">404</h1>
        <h2 class="error-title">Página no encontrada</h2>
        <p class="error-description">
          La página que estás buscando no existe o fue movida.
        </p>
        <p-button
          label="Volver al inicio"
          icon="pi pi-home"
          (onClick)="goHome()"
        />
      </div>
    </div>
  `,
  styleUrl: './not-found.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotFound {
  private router = inject(Router);

  goHome(): void {
    this.router.navigate(['/']);
  }
}
