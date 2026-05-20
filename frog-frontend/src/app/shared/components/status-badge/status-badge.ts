import { ChangeDetectionStrategy, Component, input, computed } from '@angular/core';
import { TagModule } from 'primeng/tag';

export type StatusType = 'success' | 'warn' | 'danger' | 'info' | 'secondary' | 'contrast';

@Component({
  selector: 'app-status-badge',
  imports: [TagModule],
  template: `
    <p-tag
      [severity]="severity()"
      [value]="label()"
    ></p-tag>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusBadge {
  status = input.required<string>();
  label = input<string>('');

  severity = computed<StatusType>(() => {
    const s = this.status();
    switch (s) {
      case 'CALIFICADO':
      case 'SUCCESS':
      case 'COMPLETADO':
      case 'Abierta':
        return 'success';
      case 'PROCESANDO':
      case 'PENDIENTE':
        return 'warn';
      case 'RECHAZADO':
      case 'FALLIDO':
      case 'COMPILATION_ERROR':
      case 'RUNTIME_ERROR':
      case 'Cerrada':
        return 'danger';
      case 'ENVIADO':
        return 'info';
      default:
        return 'info';
    }
  });
}
