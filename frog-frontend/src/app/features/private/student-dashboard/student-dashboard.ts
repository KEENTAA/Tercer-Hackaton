import { ChangeDetectionStrategy, Component, inject, OnInit, signal, computed } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TabsModule } from 'primeng/tabs';
import { AccordionModule } from 'primeng/accordion';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { TagModule } from 'primeng/tag';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { AuthService, CourseService, TaskService, AttemptService } from '@core/services';
import { Course, Task, Attempt } from '@core/models';

@Component({
  selector: 'app-student-dashboard',
  imports: [
    DatePipe,
    FormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    DialogModule,
    TabsModule,
    AccordionModule,
    ToastModule,
    TagModule,
    ProgressSpinnerModule,
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
  private messageService = inject(MessageService);

  currentUser = this.auth.currentUser;

  courses = signal<Course[]>([]);
  tasks = signal<Task[]>([]);
  attempts = signal<Attempt[]>([]);
  selectedTask = signal<Task | null>(null);
  selectedAttempt = signal<Attempt | null>(null);

  showTaskDialog = signal(false);
  showAttemptDialog = signal(false);
  showSubmitDialog = signal(false);
  submitting = signal(false);

  attemptsSkip = signal(0);
  attemptsLimit = signal(10);

  async ngOnInit(): Promise<void> {
    await this.loadCourses();
    await this.loadAttempts();
  }

  async loadCourses(): Promise<void> {
    try {
      const user = this.currentUser();
      if (user) {
        const data = await this.courseService.list();
        this.courses.set(data);
      }
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
      const data = await this.attemptService.getByStudent(
        this.attemptsSkip(),
        this.attemptsLimit(),
      );
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
    this.showSubmitDialog.set(true);
  }

  async submitTask(url: string): Promise<void> {
    const task = this.selectedTask();
    if (!task) return;

    this.submitting.set(true);

    try {
      await this.attemptService.create({
        id_tarea: task.id_tarea,
        url_codigo_fuente: url,
      });

      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Tarea enviada correctamente',
      });

      this.showSubmitDialog.set(false);
      await this.loadAttempts();
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo enviar la tarea',
      });
    } finally {
      this.submitting.set(false);
    }
  }

  viewAttemptDetail(attempt: Attempt): void {
    this.selectedAttempt.set(attempt);
    this.showAttemptDialog.set(true);
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

  isTaskExpired(task: Task): boolean {
    return new Date(task.fecha_limite) < new Date();
  }

  parseNotaTotal(nota: string): number {
    const parsed = parseFloat(nota);
    return isNaN(parsed) ? 0 : parsed;
  }
}
