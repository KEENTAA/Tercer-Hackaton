import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { DatePipe, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TabsModule } from 'primeng/tabs';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { TagModule } from 'primeng/tag';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SelectModule } from 'primeng/select';
import { TextareaModule } from 'primeng/textarea';
import { InputTextModule } from 'primeng/inputtext';
import { AuthService, CourseService, TaskService, AttemptService, RunnerService } from '@core/services';
import { Course, Task, Attempt, SupportedLanguage } from '@core/models';

@Component({
  selector: 'app-student-dashboard',
  imports: [
    CommonModule,
    DatePipe,
    FormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    DialogModule,
    TabsModule,
    ToastModule,
    TagModule,
    ProgressSpinnerModule,
    SelectModule,
    TextareaModule,
    InputTextModule,
  ],
  templateUrl: './student-dashboard.html',
  styleUrl: './student-dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [MessageService],
})
export class StudentDashboard implements OnInit {
  private auth = inject(AuthService);
  private courseService = inject(CourseService);
  private taskService = inject(TaskService);
  private attemptService = inject(AttemptService);
  private runnerService = inject(RunnerService);
  private messageService = inject(MessageService);

  currentUser = this.auth.currentUser;

  courses = signal<Course[]>([]);
  tasks = signal<Task[]>([]);
  attempts = signal<Attempt[]>([]);
  selectedTask = signal<Task | null>(null);
  selectedAttempt = signal<Attempt | null>(null);
  executionResult = signal<any>(null);

  showTaskDialog = signal(false);
  showAttemptDialog = signal(false);
  showSubmitDialog = signal(false);
  showResultDialog = signal(false);
  submitting = signal(false);
  executing = signal(false);

  submitCode = signal('');
  selectedLanguage = signal<SupportedLanguage>('python');

  languages: { label: string; value: SupportedLanguage }[] = [
    { label: 'Python', value: 'python' },
    { label: 'JavaScript', value: 'javascript' },
    { label: 'Java', value: 'java' },
    { label: 'C', value: 'c' },
    { label: 'C++', value: 'cpp' },
  ];

  async ngOnInit(): Promise<void> {
    await this.loadCourses();
    await this.loadAttempts();
  }

  async loadCourses(): Promise<void> {
    try {
      const data = await this.courseService.list();
      this.courses.set(data);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar los cursos',
      });
    }
  }

  async loadAttempts(): Promise<void> {
    try {
      const data = await this.attemptService.getByStudent();
      this.attempts.set(data);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar los intentos',
      });
    }
  }

  async loadTasks(courseId: number): Promise<void> {
    try {
      const data = await this.taskService.getTasksByCourseStudent(courseId);
      this.tasks.set(data);
      this.showTaskDialog.set(true);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar las tareas',
      });
    }
  }

  openSubmitDialog(task: Task): void {
    this.selectedTask.set(task);
    this.submitCode.set('');
    this.selectedLanguage.set('python');
    this.showSubmitDialog.set(true);
  }

  async submitAndExecute(): Promise<void> {
    const task = this.selectedTask();
    const code = this.submitCode().trim();
    if (!task || !code) return;

    this.submitting.set(true);

    try {
      const attempt = await this.attemptService.create({
        id_tarea: task.id_tarea,
        url_codigo_fuente: 'local',
      });

      this.messageService.add({
        severity: 'success',
        summary: 'Enviado',
        detail: 'Código enviado, ejecutando...',
      });

      this.showSubmitDialog.set(false);

      await this.executeCode(attempt.id_intento, task.id_tarea, code);
      await this.loadAttempts();
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo enviar el código',
      });
    } finally {
      this.submitting.set(false);
    }
  }

  async executeCode(
    idIntento: number,
    idTarea: number,
    codigo: string,
  ): Promise<void> {
    this.executing.set(true);

    try {
      const result = await this.runnerService.execute({
        id_intento_ref: idIntento,
        id_tarea_ref: idTarea,
        lenguaje: this.selectedLanguage(),
        codigo_fuente: codigo,
      });

      this.executionResult.set(result);
      this.showResultDialog.set(true);

      if (result.aprobado) {
        this.messageService.add({
          severity: 'success',
          summary: '¡Aprobado!',
          detail: `Pasaste ${result.casos_aprobados}/${result.casos_totales} casos`,
        });
      } else {
        this.messageService.add({
          severity: 'warn',
          summary: 'No aprobado',
          detail: `${result.casos_aprobados}/${result.casos_totales} casos pasados`,
        });
      }
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo ejecutar el código',
      });
    } finally {
      this.executing.set(false);
    }
  }

  viewAttemptDetail(attempt: Attempt): void {
    this.selectedAttempt.set(attempt);
    this.showAttemptDialog.set(true);
  }

  async viewExecutionResult(attempt: Attempt): Promise<void> {
    try {
      const result = await this.runnerService.getResults(attempt.id_intento);
      if (result) {
        this.executionResult.set(result);
        this.showResultDialog.set(true);
      } else {
        this.messageService.add({
          severity: 'info',
          summary: 'Sin resultados',
          detail: 'Aún no hay resultados de ejecución',
        });
      }
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo cargar el resultado',
      });
    }
  }

  getStatusSeverity(status: string): 'success' | 'warn' | 'danger' | 'info' {
    switch (status) {
      case 'CALIFICADO':
        return 'success';
      case 'PROCESANDO':
        return 'warn';
      case 'RECHAZADO':
        return 'danger';
      default:
        return 'info';
    }
  }

  getCompilationStatusSeverity(status: string): 'success' | 'warn' | 'danger' | 'info' {
    switch (status) {
      case 'SUCCESS':
        return 'success';
      case 'COMPILATION_ERROR':
        return 'danger';
      case 'RUNTIME_ERROR':
        return 'warn';
      default:
        return 'info';
    }
  }

  isTaskExpired(task: Task): boolean {
    return new Date(task.fecha_limite) < new Date();
  }
}
