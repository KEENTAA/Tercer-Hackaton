export enum AuditAction {
  CREACION_INTENTO = 'CREACION_INTENTO',
  MODIFICACION_NOTA = 'MODIFICACION_NOTA',
  CAMBIO_ESTADO = 'CAMBIO_ESTADO',
  CREACION_TAREA = 'CREACION_TAREA',
  MODIFICACION_TAREA = 'MODIFICACION_TAREA',
  ELIMINACION_TAREA = 'ELIMINACION_TAREA',
}

export interface AuditLog {
  id_auditoria: number;
  id_intento: number;
  accion: AuditAction;
  valor_anterior: string;
  valor_nuevo: string;
  fecha_cambio: string;
  ejecutado_por: number;
}

export type AuditLogEntry = Omit<AuditLog, 'id_auditoria' | 'fecha_cambio'>;
