export enum PlagiarismStatus {
  PENDIENTE = 'PENDIENTE',
  COMPLETADO = 'COMPLETADO',
  FALLIDO = 'FALLIDO',
}

export interface PlagiarismReport {
  id_reporte: number;
  id_intento_ref: number;
  porcentaje_similitud_total: number;
  id_externo_turnitin: string | null;
  estado_analisis: PlagiarismStatus;
  fecha_analisis: string;
}

export interface PlagiarismMatch {
  id_reporte: number;
  id_firma_coincidente: number;
  porcentaje_coincidencia: number;
}

export interface PlagiarismReportWithMatches extends PlagiarismReport {
  coincidencias: PlagiarismMatch[];
}
