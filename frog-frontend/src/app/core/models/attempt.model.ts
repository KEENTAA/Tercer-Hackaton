import { ExecutionResult } from './runner.model';
import { PlagiarismReport } from './plagiarism.model';

export enum AttemptStatus {
  ENVIADO = 'ENVIADO',
  PROCESANDO = 'PROCESANDO',
  CALIFICADO = 'CALIFICADO',
  RECHAZADO = 'RECHAZADO',
}

export interface Attempt {
  id_intento: number;
  id_tarea: number;
  id_estudiante: number;
  numero_intento: number;
  fecha_envio: string;
  url_codigo_fuente: string;
  nota_total: number | null;
  estado: AttemptStatus;
}

export interface GradeByCriterion {
  id_intento: number;
  id_criterio: number;
  nota_obtenida: number;
  comentarios: string;
}

export interface AttemptWithDetails extends Attempt {
  calificaciones: GradeByCriterion[];
  ejecucion?: ExecutionResult;
  plagio?: PlagiarismReport;
}

export type CreateAttemptRequest = Pick<Attempt, 'id_tarea' | 'url_codigo_fuente'>;
export type UpdateAttemptStatus = Pick<Attempt, 'estado' | 'nota_total'>;
