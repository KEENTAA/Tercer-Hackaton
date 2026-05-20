export const CompilationStatus = {
  SUCCESS: 'SUCCESS',
  COMPILATION_ERROR: 'COMPILATION_ERROR',
  RUNTIME_ERROR: 'RUNTIME_ERROR',
} as const;

export type CompilationStatus = typeof CompilationStatus[keyof typeof CompilationStatus];

export type SupportedLanguage = 'python' | 'javascript' | 'java' | 'c' | 'cpp';

/** @deprecated Use CasoPruebaResponse instead */
export type TestCase = Partial<CasoPruebaResponse> & { id_caso: number; id_tarea_ref: number };

/** @deprecated Use EjecucionResponse instead */
export type ExecutionResult = Partial<EjecucionResponse> & { id_resultado: number; id_intento_ref: number };

export interface CasoPruebaCreate {
  id_tarea_ref: number;
  entrada_datos?: string;
  salida_esperada: string;
  tiempo_limite_ms?: number;
  descripcion?: string;
  es_obligatorio?: boolean;
}

export interface CasoPruebaCreateBatch {
  casos: CasoPruebaCreate[];
}

export interface CasoPruebaResponse {
  id_caso: number;
  id_tarea_ref: number;
  entrada_datos?: string;
  salida_esperada: string;
  tiempo_limite_ms: number;
  descripcion?: string;
  es_obligatorio: boolean;
  creado_en: string;
}

export interface EjecucionRequest {
  id_intento_ref: number;
  id_tarea_ref: number;
  lenguaje: SupportedLanguage;
  codigo_fuente: string;
}

export interface DetalleResultadoCaso {
  id_caso: number;
  descripcion?: string;
  entrada_datos?: string;
  salida_esperada: string;
  salida_obtenida: string;
  paso: boolean;
  tiempo_ms?: number;
  es_obligatorio: boolean;
  error?: string;
}

export interface EjecucionResponse {
  id_resultado: number;
  id_intento_ref: number;
  id_tarea_ref: number;
  lenguaje: string;
  estado_compilacion: CompilationStatus;
  aprobado: boolean;
  casos_totales: number;
  casos_aprobados: number;
  tiempo_usado_ms?: number;
  memoria_usada_kb?: number;
  salida_consola?: string;
  detalle_casos: DetalleResultadoCaso[];
  ejecutado_en: string;
}

export interface ResultadoEjecucionResponse {
  id_resultado: number;
  id_intento_ref: number;
  id_tarea_ref: number;
  lenguaje: string;
  estado_compilacion: CompilationStatus;
  aprobado: boolean;
  casos_totales: number;
  casos_aprobados: number;
  tiempo_usado_ms?: number;
  memoria_usada_kb?: number;
  salida_consola?: string;
  detalle_casos?: DetalleResultadoCaso[];
  ejecutado_en: string;
}
