import { ChangeDetectionStrategy, Component, computed, inject, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { FileUploadModule } from 'primeng/fileupload';
import { TabsModule } from 'primeng/tabs';
import { AccordionModule } from 'primeng/accordion';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { TagModule } from 'primeng/tag';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { AuthService, CourseService, TaskService, AttemptService, PlagiarismService } from '@core/services';
import { Course, Task, Attempt, AttemptWithDetails, PlagiarismReportWithMatches } from '@core/models';

@Component({
  selector: 'app-student-dashboard',
  imports: [
    DatePipe,
    FormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    DialogModule,
    FileUploadModule,
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
  private plagiarismService = inject(PlagiarismService);
  private messageService = inject(MessageService);

  currentUser = this.auth.currentUser;

  courses = signal<Course[]>([]);
  tasks = signal<Task[]>([]);
  attempts = signal<Attempt[]>([]);
  selectedTask = signal<Task | null>(null);
  attemptDetail = signal<AttemptWithDetails | null>(null);
  plagiarismReport = signal<PlagiarismReportWithMatches | null>(null);

  showUploadDialog = signal(false);
  showAttemptDetailDialog = signal(false);
  uploading = signal(false);

  studentPage = signal(1);
  studentPageSize = signal(10);

  async ngOnInit(): Promise<void> {
    await this.loadCourses();
    await this.loadAttempts();
  }

  async loadCourses(): Promise<void> {
    try {
      const user = this.currentUser();
      if (user) {
        const data = await this.courseService.getMyCourses(user.id_usuario);
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
      const user = this.currentUser();
      if (user) {
        const data = await this.attemptService.getByStudent(user.id_usuario);
        this.attempts.set(data);
      }
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
      const data = await this.taskService.getByCourse(courseId);
      this.tasks.set(data);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar las tareas',
      });
    }
  }

  openUploadDialog(task: Task): void {
    this.selectedTask.set(task);
    this.showUploadDialog.set(true);
  }

  async onUpload(event: { files: File[] }): Promise<void> {
    const task = this.selectedTask();
    const user = this.currentUser();
    if (!task || !user || event.files.length === 0) return;

    this.uploading.set(true);

    try {
      const attempt = await this.attemptService.create({
        id_tarea: task.id_tarea,
        url_codigo_fuente: '',
      });

      await this.attemptService.uploadCode(attempt.id_intento, event.files[0]);

      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Código enviado correctamente',
      });

      this.showUploadDialog.set(false);
      await this.loadAttempts();
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo enviar el código',
      });
    } finally {
      this.uploading.set(false);
    }
  }

  async viewAttemptDetail(attempt: Attempt): Promise<void> {
    try {
      const detail = await this.attemptService.getById(attempt.id_intento);
      this.attemptDetail.set(detail);

      const plagiarism = await this.plagiarismService.getByAttempt(attempt.id_intento);
      this.plagiarismReport.set(plagiarism);

      this.showAttemptDetailDialog.set(true);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo cargar el detalle',
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

  isTaskExpired(task: Task): boolean {
    return new Date(task.fecha_limite) < new Date();
  }

  paginatedAttempts = computed(() => {
    const start = (this.studentPage() - 1) * this.studentPageSize();
    return this.attempts().slice(start, start + this.studentPageSize());
  });

  onStudentPageChange(event: { first: number; rows: number }): void {
    this.studentPage.set(event.first / event.rows + 1);
    this.studentPageSize.set(event.rows);
  }
}
