export interface Task {
  id_tarea: number;
  id_curso: number;
  titulo: string;
  descripcion: string;
  fecha_limite: string;
}

export interface GradingCriterion {
  id_criterio: number;
  id_tarea: number;
  descripcion: string;
  ponderacion: number;
}

export type CreateTaskRequest = Omit<Task, 'id_tarea'>;
export type UpdateTaskRequest = Partial<CreateTaskRequest>;
export type CreateCriterionRequest = Omit<GradingCriterion, 'id_criterio'>;
export type UpdateCriterionRequest = Partial<CreateCriterionRequest>;
