export interface CriterioCreate {
  descripcion: string;
  ponderacion: number;
}

export interface CriterioResponse {
  id_criterio: number;
  id_tarea: number;
  descripcion: string;
  ponderacion: number;
}

export interface Task {
  id_tarea: number;
  id_curso: number;
  titulo: string;
  descripcion: string;
  fecha_limite: string;
  criterios?: CriterioResponse[];
}

export interface TaskCreate {
  titulo: string;
  descripcion: string;
  fecha_limite: string;
  id_curso: number;
  criterios: CriterioCreate[];
}

export interface TaskUpdate {
  titulo?: string;
  descripcion?: string;
  fecha_limite?: string;
}

/** @deprecated Use CriterioResponse instead */
export type GradingCriterion = CriterioResponse;
