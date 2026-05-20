import { EjecucionResponse } from './runner.model';
import { PlagiarismReport } from './plagiarism.model';

export enum AttemptStatus {
  ENVIADO = 'ENVIADO',
  PROCESANDO = 'PROCESANDO',
  CALIFICADO = 'CALIFICADO',
  RECHAZADO = 'RECHAZADO',
}

export interface CalificacionDetallada {
  id_intento: number;
  id_criterio: number;
  nota_obtenida: number;
  comentarios: string;
}

/** @deprecated Use CalificacionDetallada instead */
export type GradeByCriterion = CalificacionDetallada;

export interface Attempt {
  id_intento: number;
  id_tarea: number;
  id_estudiante: number;
  numero_intento: number;
  fecha_envio: string;
  url_codigo_fuente: string;
  nota_total: string | number | null;
  estado: AttemptStatus;
  calificaciones_detalladas?: CalificacionDetallada[];
}

export interface AttemptCreate {
  id_tarea: number;
  url_codigo_fuente: string;
}

export interface AttemptWithDetails extends Attempt {
  ejecucion?: EjecucionResponse;
  plagio?: PlagiarismReport;
}
