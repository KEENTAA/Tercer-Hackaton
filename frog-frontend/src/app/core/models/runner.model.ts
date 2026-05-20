export enum CompilationStatus {
  SUCCESS = 'SUCCESS',
  COMPILATION_ERROR = 'COMPILATION_ERROR',
  RUNTIME_ERROR = 'RUNTIME_ERROR',
}

export interface TestCase {
  id_caso: number;
  id_tarea_ref: number;
  entrada_datos: string;
  salida_esperada: string;
  tiempo_limite_ms: number;
}

export interface TestCaseCreate {
  id_tarea_ref: number;
  entrada_datos: string;
  salida_esperada: string;
  tiempo_limite_ms: number;
}

export interface ExecuteRequest {
  id_intento_ref: number;
  id_tarea_ref: number;
  codigo_fuente: string;
  lenguaje: string;
  version?: string;
}

export interface ExecutionResult {
  id_resultado: number;
  id_intento_ref: number;
  estado_compilacion: CompilationStatus;
  tiempo_usado_ms: number;
  memoria_usada_kb: number;
  salida_consola: string;
  aprobado: boolean;
}

export interface ExecuteResponse {
  id_intento_ref: number;
  estado: string;
  mensaje: string;
}
