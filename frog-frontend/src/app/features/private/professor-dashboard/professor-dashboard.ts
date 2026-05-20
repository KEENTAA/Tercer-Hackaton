import { ChangeDetectionStrategy, Component, inject, OnInit, signal, computed } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
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
import { AuthService, CourseService, TaskService, AttemptService } from '@core/services';
import { Course, Task, Attempt, TaskCreate, CriterioCreate } from '@core/models';

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
  private messageService = inject(MessageService);
  private confirmationService = inject(ConfirmationService);
  private fb = inject(FormBuilder);

  currentUser = this.auth.currentUser;

  courses = signal<Course[]>([]);
  tasks = signal<Task[]>([]);
  attempts = signal<Attempt[]>([]);
  selectedTask = signal<Task | null>(null);

  showCourseDialog = signal(false);
  showTaskDialog = signal(false);
  showAttemptsDialog = signal(false);

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
    criterios: this.fb.array([]),
  });

  async ngOnInit(): Promise<void> {
    await this.loadCourses();
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

  async loadAttempts(taskId: number): Promise<void> {
    try {
      const data = await this.attemptService.getByStudent();
      const filtered = data.filter((a) => a.id_tarea === taskId);
      this.attempts.set(filtered);
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

  openTaskDialog(courseId: number): void {
    this.taskForm.reset();
    this.taskForm.patchValue({ id_curso: courseId });
    this.showTaskDialog.set(true);
  }

  addCriterion(): void {
    const criteria = this.taskForm.get('criterios') as FormArray;
    criteria.push(
      this.fb.group({
        descripcion: ['', Validators.required],
        ponderacion: [0, [Validators.required, Validators.min(0), Validators.max(100)]],
      }),
    );
  }

  removeCriterion(index: number): void {
    const criteria = this.taskForm.get('criterios') as FormArray;
    criteria.removeAt(index);
  }

  get criteriaArray(): FormGroup[] {
    const arr = this.taskForm.get('criterios') as FormArray;
    return (arr?.controls ?? []) as FormGroup[];
  }

  async saveTask(): Promise<void> {
    if (this.taskForm.invalid) {
      this.taskForm.markAllAsTouched();
      return;
    }

    try {
      const formValue = this.taskForm.value;
      const request: TaskCreate = {
        titulo: formValue.titulo,
        descripcion: formValue.descripcion,
        fecha_limite: formValue.fecha_limite.toISOString(),
        id_curso: formValue.id_curso,
        criterios: formValue.criterios as CriterioCreate[],
      };

      await this.taskService.create(request);
      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Tarea creada correctamente',
      });
      this.showTaskDialog.set(false);
      await this.loadTasks(request.id_curso);
    } catch {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo crear la tarea',
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
          await this.loadTasks(task.id_curso);
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
}
