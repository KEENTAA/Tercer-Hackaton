import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-empty-state',
  imports: [],
  template: `
    <div class="empty-state">
      @if (icon()) {
        <i [class]="icon()" class="empty-icon"></i>
      }
      <p class="empty-text">{{ message() }}</p>
    </div>
  `,
  styleUrl: './empty-state.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EmptyState {
  message = input('No hay datos disponibles');
  icon = input<string>('pi pi-inbox');
}
