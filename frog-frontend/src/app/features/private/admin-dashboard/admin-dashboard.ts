import { ChangeDetectionStrategy, Component, inject, OnInit, signal, computed } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { TagModule } from 'primeng/tag';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { TabsModule } from 'primeng/tabs';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { AuditService, PlagiarismService } from '@core/services';
import { AuditLog, PlagiarismReport, AuditAction } from '@core/models';

@Component({
  selector: 'app-admin-dashboard',
  imports: [
    DatePipe,
    FormsModule,
    ReactiveFormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    DatePickerModule,
    TagModule,
    ToastModule,
    TabsModule,
    DialogModule,
    InputTextModule,
    SelectModule,
  ],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [MessageService],
})
export class AdminDashboard implements OnInit {
  private auditService = inject(AuditService);
  private plagiarismService = inject(PlagiarismService);
  private messageService = inject(MessageService);
  private fb = inject(FormBuilder);

  auditLogs = signal<AuditLog[]>([]);
  plagiarismReports = signal<PlagiarismReport[]>([]);
  highRiskReports = signal<PlagiarismReport[]>([]);

  dateRange = signal<[Date, Date] | null>(null);
  selectedAction = signal<string | null>(null);

  showFilterDialog = signal(false);

  auditPage = signal(1);
  auditPageSize = signal(15);

  auditActions = [
    { label: 'Todas', value: null },
    { label: 'Creación de Intento', value: AuditAction.CREACION_INTENTO },
    { label: 'Modificación de Nota', value: AuditAction.MODIFICACION_NOTA },
    { label: 'Cambio de Estado', value: AuditAction.CAMBIO_ESTADO },
    { label: 'Creación de Tarea', value: AuditAction.CREACION_TAREA },
  ];

  async ngOnInit(): Promise<void> {
    await this.loadAuditLogs();
    await this.loadHighRiskReports();
  }

  async loadAuditLogs(): Promise<void> {
    try {
      if (this.dateRange()) {
        const [from, to] = this.dateRange()!;
        const data = await this.auditService.getByDateRange(
          from.toISOString(),
          to.toISOString(),
        );
        this.auditLogs.set(data);
      } else {
        const data = await this.auditService.list();
        this.auditLogs.set(data.data);
      }
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar los logs de auditoría',
      });
    }
  }

  async loadHighRiskReports(threshold = 70): Promise<void> {
    try {
      const data = await this.plagiarismService.getHighRiskReports(threshold);
      this.highRiskReports.set(data);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar los reportes de plagio',
      });
    }
  }

  async applyFilters(): Promise<void> {
    await this.loadAuditLogs();
    this.showFilterDialog.set(false);
  }

  resetFilters(): void {
    this.dateRange.set(null);
    this.selectedAction.set(null);
    this.loadAuditLogs();
  }

  getActionLabel(action: string): string {
    const found = this.auditActions.find((a) => a.value === action);
    return found?.label ?? action;
  }

  getRiskLevel(percentage: number): 'success' | 'warn' | 'danger' | 'info' {
    if (percentage >= 80) return 'danger';
    if (percentage >= 50) return 'warn';
    return 'info';
  }

  paginatedAuditLogs = computed(() => {
    const start = (this.auditPage() - 1) * this.auditPageSize();
    return this.auditLogs().slice(start, start + this.auditPageSize());
  });

  onAuditPageChange(event: { first: number; rows: number }): void {
    this.auditPage.set(event.first / event.rows + 1);
    this.auditPageSize.set(event.rows);
  }
}
