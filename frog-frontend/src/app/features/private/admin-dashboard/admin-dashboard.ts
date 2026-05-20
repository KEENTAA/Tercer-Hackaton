import { ChangeDetectionStrategy, Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { TagModule } from 'primeng/tag';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { TabsModule } from 'primeng/tabs';
import { AuditService, PlagiarismService } from '@core/services';

@Component({
  selector: 'app-admin-dashboard',
  imports: [
    CommonModule,
    DatePipe,
    FormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    DatePickerModule,
    TagModule,
    ToastModule,
    TabsModule,
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

  auditLogs = signal<unknown[]>([]);
  highRiskReports = signal<any[]>([]);

  auditSkip = signal(0);
  auditLimit = signal(15);

  async ngOnInit(): Promise<void> {
    await this.loadAuditLogs();
    await this.loadHighRiskReports();
  }

  async loadAuditLogs(): Promise<void> {
    try {
      const data = await this.auditService.list(
        this.auditSkip(),
        this.auditLimit(),
      );
      this.auditLogs.set(data);
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

  getRiskLevel(percentage: number): 'success' | 'warn' | 'danger' | 'info' {
    if (percentage >= 80) return 'danger';
    if (percentage >= 50) return 'warn';
    return 'info';
  }
}
