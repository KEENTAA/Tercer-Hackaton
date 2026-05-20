import { ChangeDetectionStrategy, Component, inject, OnInit, signal, computed } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { DatePickerModule } from 'primeng/datepicker';
import { TabsModule } from 'primeng/tabs';
import { TagModule } from 'primeng/tag';
import { MessageService, ConfirmationService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { AuthService, CourseService, TaskService, AttemptService, PlagiarismService } from '@core/services';
import { Course, Task, GradingCriterion, Attempt, CreateTaskRequest, CreateCriterionRequest } from '@core/models';

@Component({
  selector: 'app-professor-dashboard',
  imports: [
    DatePipe,
    FormsModule,
    ReactiveFormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    TextareaModule,
    DatePickerModule,
    TabsModule,
    TagModule,
    ToastModule,
    ConfirmDialogModule,
    InputNumberModule,
    SelectModule,
  ],
  templateUrl: './professor-dashboard.html',
  styleUrl: './professor-dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [MessageService, ConfirmationService],
})
export class ProfessorDashboard implements OnInit {
  private auth = inject(AuthService);
  private courseService = inject(CourseService);
  private taskService = inject(TaskService);
  private attemptService = inject(AttemptService);
  private plagiarismService = inject(PlagiarismService);
  private messageService = inject(MessageService);
  private confirmationService = inject(ConfirmationService);
  private fb = inject(FormBuilder);

  currentUser = this.auth.currentUser;

  courses = signal<Course[]>([]);
  tasks = signal<Task[]>([]);
  attempts = signal<Attempt[]>([]);
  selectedTask = signal<Task | null>(null);
  criteria = signal<GradingCriterion[]>([]);

  showCourseDialog = signal(false);
  showTaskDialog = signal(false);
  showCriterionDialog = signal(false);
  showAttemptsDialog = signal(false);

  coursePage = signal(1);
  coursePageSize = signal(10);

  courseForm: FormGroup = this.fb.group({
    codigo_curso: ['', Validators.required],
    nombre: ['', Validators.required],
    gestion: ['', Validators.required],
  });

  taskForm: FormGroup = this.fb.group({
    titulo: ['', Validators.required],
    descripcion: ['', Validators.required],
    fecha_limite: [null, Validators.required],
    id_curso: [null, Validators.required],
  });

  criterionForm: FormGroup = this.fb.group({
    descripcion: ['', Validators.required],
    ponderacion: [0, [Validators.required, Validators.min(0), Validators.max(100)]],
  });

  async ngOnInit(): Promise<void> {
    await this.loadCourses();
  }

  async loadCourses(): Promise<void> {
    try {
      const data = await this.courseService.list();
      this.courses.set(data.data);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar los cursos',
      });
    }
  }

  async loadTasks(): Promise<void> {
    try {
      const user = this.currentUser();
      if (!user) return;

      const allTasks: Task[] = [];
      for (const course of this.courses()) {
        if (course.id_profesor === user.id_usuario) {
          const tasks = await this.taskService.getByCourse(course.id_curso);
          allTasks.push(...tasks);
        }
      }
      this.tasks.set(allTasks);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar las tareas',
      });
    }
  }

  async loadCriteria(taskId: number): Promise<void> {
    try {
      const data = await this.taskService.getCriteria(taskId);
      this.criteria.set(data);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar los criterios',
      });
    }
  }

  async loadAttempts(taskId: number): Promise<void> {
    try {
      const data = await this.attemptService.getByTask(taskId);
      this.attempts.set(data);
      this.showAttemptsDialog.set(true);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudieron cargar los intentos',
      });
    }
  }

  openCourseDialog(): void {
    this.courseForm.reset();
    this.showCourseDialog.set(true);
  }

  async saveCourse(): Promise<void> {
    if (this.courseForm.invalid) {
      this.courseForm.markAllAsTouched();
      return;
    }

    try {
      const user = this.currentUser();
      await this.courseService.create({
        ...this.courseForm.value,
        id_profesor: user!.id_usuario,
      });
      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Curso creado correctamente',
      });
      this.showCourseDialog.set(false);
      await this.loadCourses();
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo crear el curso',
      });
    }
  }

  openTaskDialog(): void {
    this.taskForm.reset();
    this.showTaskDialog.set(true);
  }

  async saveTask(): Promise<void> {
    if (this.taskForm.invalid) {
      this.taskForm.markAllAsTouched();
      return;
    }

    try {
      await this.taskService.create(this.taskForm.value as CreateTaskRequest);
      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Tarea creada correctamente',
      });
      this.showTaskDialog.set(false);
      await this.loadTasks();
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo crear la tarea',
      });
    }
  }

  openCriterionDialog(task: Task): void {
    this.selectedTask.set(task);
    this.criterionForm.reset();
    this.showCriterionDialog.set(true);
  }

  async saveCriterion(): Promise<void> {
    if (this.criterionForm.invalid || !this.selectedTask()) return;

    try {
      await this.taskService.createCriterion(
        this.selectedTask()!.id_tarea,
        this.criterionForm.value as CreateCriterionRequest,
      );
      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Criterio agregado',
      });
      this.showCriterionDialog.set(false);
      await this.loadCriteria(this.selectedTask()!.id_tarea);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo agregar el criterio',
      });
    }
  }

  confirmDeleteTask(task: Task): void {
    this.confirmationService.confirm({
      message: `¿Estás seguro de eliminar "${task.titulo}"?`,
      header: 'Confirmar',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await this.taskService.delete(task.id_tarea);
          this.messageService.add({
            severity: 'success',
            summary: 'Eliminado',
            detail: 'Tarea eliminada',
          });
          await this.loadTasks();
        } catch {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo eliminar la tarea',
          });
        }
      },
    });
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

  paginatedCourses = computed(() => {
    const start = (this.coursePage() - 1) * this.coursePageSize();
    return this.courses().slice(start, start + this.coursePageSize());
  });

  onCoursePageChange(event: { first: number; rows: number }): void {
    this.coursePage.set(event.first / event.rows + 1);
    this.coursePageSize.set(event.rows);
  }
}
