import { User, Course, Task, GradingCriterion, Attempt, GradeByCriterion, AuditLog, PlagiarismReport, PlagiarismMatch, TestCase, ExecutionResult } from '../models';
import { UserRole } from '../models';
import { AttemptStatus } from '../models';
import { AuditAction } from '../models';
import { CompilationStatus } from '../models';
import { PlagiarismStatus } from '../models';

export interface MockUserCredentials {
  codigo_universitario: string;
  password: string;
  user: User;
}

export const MOCK_USERS: MockUserCredentials[] = [
  {
    codigo_universitario: '2026-1105',
    password: '123456',
    user: { id_usuario: 1, codigo_universitario: '2026-1105', nombre: 'Juan Estudiante', correo: 'juan@universidad.edu', rol: UserRole.ESTUDIANTE },
  },
  {
    codigo_universitario: 'PROF-001',
    password: '123456',
    user: { id_usuario: 2, codigo_universitario: 'PROF-001', nombre: 'María Profesora', correo: 'maria@universidad.edu', rol: UserRole.PROFESOR },
  },
  {
    codigo_universitario: 'ADMIN-001',
    password: '123456',
    user: { id_usuario: 3, codigo_universitario: 'ADMIN-001', nombre: 'Carlos Admin', correo: 'carlos@universidad.edu', rol: UserRole.ADMIN },
  },
];

export const MOCK_COURSES: Course[] = [
  { id_curso: 1, codigo_curso: 'SIS-101', nombre: 'Introducción a la Programación', gestion: '1/2026', id_profesor: 2 },
  { id_curso: 2, codigo_curso: 'INF-212', nombre: 'Estructuras de Datos', gestion: '1/2026', id_profesor: 2 },
  { id_curso: 3, codigo_curso: 'SIS-300', nombre: 'Ingeniería de Software', gestion: '1/2026', id_profesor: 2 },
];

export const MOCK_TASKS: Task[] = [
  {
    id_tarea: 1,
    id_curso: 1,
    titulo: 'Hello World en Python',
    descripcion: 'Escribir un programa que imprima "Hello, World!" y reciba un nombre como parámetro.',
    fecha_limite: '2026-06-15T23:59:00',
  },
  {
    id_tarea: 2,
    id_curso: 1,
    titulo: 'Calculadora Básica',
    descripcion: 'Implementar una calculadora que sume, reste, multiplique y divida dos números.',
    fecha_limite: '2026-06-20T23:59:00',
  },
  {
    id_tarea: 3,
    id_curso: 2,
    titulo: 'LinkedList en Java',
    descripcion: 'Implementar una lista enlazada con métodos: insert, delete, search, y print.',
    fecha_limite: '2026-05-10T23:59:00',
  },
  {
    id_tarea: 4,
    id_curso: 2,
    titulo: 'Binary Search Tree',
    descripcion: 'Implementar un árbol binario de búsqueda con insert, delete, search y traversal.',
    fecha_limite: '2026-07-01T23:59:00',
  },
  {
    id_tarea: 5,
    id_curso: 3,
    titulo: 'Patrones de Diseño',
    descripcion: 'Implementar Singleton, Factory y Observer en un sistema de notificaciones.',
    fecha_limite: '2026-06-30T23:59:00',
  },
];

export const MOCK_CRITERIA: GradingCriterion[] = [
  { id_criterio: 1, id_tarea: 1, descripcion: 'Compila sin errores', ponderacion: 40 },
  { id_criterio: 2, id_tarea: 1, descripcion: 'Output correcto', ponderacion: 60 },
  { id_criterio: 3, id_tarea: 2, descripcion: 'Operaciones básicas correctas', ponderacion: 50 },
  { id_criterio: 4, id_tarea: 2, descripcion: 'Manejo de división por cero', ponderacion: 30 },
  { id_criterio: 5, id_tarea: 2, descripcion: 'Código limpio y comentado', ponderacion: 20 },
  { id_criterio: 6, id_tarea: 3, descripcion: 'Métodos implementados correctamente', ponderacion: 60 },
  { id_criterio: 7, id_tarea: 3, descripcion: 'Manejo de casos borde', ponderacion: 40 },
  { id_criterio: 8, id_tarea: 4, descripcion: 'Insert y Search funcionales', ponderacion: 40 },
  { id_criterio: 9, id_tarea: 4, descripcion: 'Delete funcional', ponderacion: 30 },
  { id_criterio: 10, id_tarea: 4, descripcion: 'Traversal correcto (in-order)', ponderacion: 30 },
  { id_criterio: 11, id_tarea: 5, descripcion: 'Singleton implementado', ponderacion: 25 },
  { id_criterio: 12, id_tarea: 5, descripcion: 'Factory implementado', ponderacion: 35 },
  { id_criterio: 13, id_tarea: 5, descripcion: 'Observer implementado', ponderacion: 40 },
];

export const MOCK_ATTEMPTS: Attempt[] = [
  {
    id_intento: 1, id_tarea: 1, id_estudiante: 1, numero_intento: 1,
    fecha_envio: '2026-05-15T10:30:00', url_codigo_fuente: '/storage/attempt_1.py',
    nota_total: 85, estado: AttemptStatus.CALIFICADO,
  },
  {
    id_intento: 2, id_tarea: 1, id_estudiante: 1, numero_intento: 2,
    fecha_envio: '2026-05-16T14:20:00', url_codigo_fuente: '/storage/attempt_2.py',
    nota_total: 95, estado: AttemptStatus.CALIFICADO,
  },
  {
    id_intento: 3, id_tarea: 2, id_estudiante: 1, numero_intento: 1,
    fecha_envio: '2026-05-17T09:00:00', url_codigo_fuente: '/storage/attempt_3.py',
    nota_total: 70, estado: AttemptStatus.CALIFICADO,
  },
  {
    id_intento: 4, id_tarea: 3, id_estudiante: 1, numero_intento: 1,
    fecha_envio: '2026-05-08T16:45:00', url_codigo_fuente: '/storage/attempt_4.java',
    nota_total: null, estado: AttemptStatus.RECHAZADO,
  },
  {
    id_intento: 5, id_tarea: 4, id_estudiante: 1, numero_intento: 1,
    fecha_envio: '2026-05-19T08:00:00', url_codigo_fuente: '/storage/attempt_5.java',
    nota_total: null, estado: AttemptStatus.PROCESANDO,
  },
  {
    id_intento: 6, id_tarea: 1, id_estudiante: 1, numero_intento: 3,
    fecha_envio: '2026-05-19T11:00:00', url_codigo_fuente: '/storage/attempt_6.py',
    nota_total: null, estado: AttemptStatus.ENVIADO,
  },
];

export const MOCK_GRADES_BY_CRITERION: GradeByCriterion[] = [
  { id_intento: 1, id_criterio: 1, nota_obtenida: 35, comentarios: 'Compiló correctamente' },
  { id_intento: 1, id_criterio: 2, nota_obtenida: 50, comentarios: 'Output correcto en 3 de 5 casos' },
  { id_intento: 2, id_criterio: 1, nota_obtenida: 40, comentarios: 'Compiló sin errores' },
  { id_intento: 2, id_criterio: 2, nota_obtenida: 55, comentarios: 'Output correcto en todos los casos' },
  { id_intento: 3, id_criterio: 3, nota_obtenida: 40, comentarios: 'Suma y resta correctas' },
  { id_intento: 3, id_criterio: 4, nota_obtenida: 10, comentarios: 'No maneja división por cero' },
  { id_intento: 3, id_criterio: 5, nota_obtenida: 20, comentarios: 'Código limpio' },
];

export const MOCK_EXECUTION_RESULTS: ExecutionResult[] = [
  {
    id_resultado: 1, id_intento_ref: 1, estado_compilacion: CompilationStatus.SUCCESS,
    tiempo_usado_ms: 120, memoria_usada_kb: 8192, salida_consola: 'Hello, World!\nHello, Juan!',
    aprobado: true,
  },
  {
    id_resultado: 2, id_intento_ref: 2, estado_compilacion: CompilationStatus.SUCCESS,
    tiempo_usado_ms: 95, memoria_usada_kb: 7680, salida_consola: 'Hello, World!\nHello, María!',
    aprobado: true,
  },
  {
    id_resultado: 3, id_intento_ref: 3, estado_compilacion: CompilationStatus.SUCCESS,
    tiempo_usado_ms: 200, memoria_usada_kb: 9216, salida_consola: '5 + 3 = 8\n10 / 0 = Error!',
    aprobado: false,
  },
  {
    id_resultado: 4, id_intento_ref: 4, estado_compilacion: CompilationStatus.COMPILATION_ERROR,
    tiempo_usado_ms: 0, memoria_usada_kb: 0, salida_consola: 'Error: cannot find symbol method insert(Node)',
    aprobado: false,
  },
];

export const MOCK_TEST_CASES: TestCase[] = [
  { id_caso: 1, id_tarea_ref: 1, entrada_datos: 'Juan', salida_esperada: 'Hello, World!\nHello, Juan!', tiempo_limite_ms: 1000 },
  { id_caso: 2, id_tarea_ref: 1, entrada_datos: 'María', salida_esperada: 'Hello, World!\nHello, María!', tiempo_limite_ms: 1000 },
  { id_caso: 3, id_tarea_ref: 2, entrada_datos: '5 3 +', salida_esperada: '8', tiempo_limite_ms: 500 },
  { id_caso: 4, id_tarea_ref: 2, entrada_datos: '10 0 /', salida_esperada: 'Error: división por cero', tiempo_limite_ms: 500 },
];

export const MOCK_AUDIT_LOGS: AuditLog[] = [
  {
    id_auditoria: 1, id_intento: 1, accion: AuditAction.CREACION_INTENTO,
    valor_anterior: '{}', valor_nuevo: '{"id_intento":1,"estado":"ENVIADO"}',
    fecha_cambio: '2026-05-15T10:30:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 2, id_intento: 1, accion: AuditAction.MODIFICACION_NOTA,
    valor_anterior: '{"nota_total":null}', valor_nuevo: '{"nota_total":85}',
    fecha_cambio: '2026-05-15T10:35:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 3, id_intento: 2, accion: AuditAction.CREACION_INTENTO,
    valor_anterior: '{}', valor_nuevo: '{"id_intento":2,"estado":"ENVIADO"}',
    fecha_cambio: '2026-05-16T14:20:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 4, id_intento: 2, accion: AuditAction.MODIFICACION_NOTA,
    valor_anterior: '{"nota_total":null}', valor_nuevo: '{"nota_total":95}',
    fecha_cambio: '2026-05-16T14:25:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 5, id_intento: 3, accion: AuditAction.CREACION_INTENTO,
    valor_anterior: '{}', valor_nuevo: '{"id_intento":3,"estado":"ENVIADO"}',
    fecha_cambio: '2026-05-17T09:00:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 6, id_intento: 4, accion: AuditAction.CREACION_INTENTO,
    valor_anterior: '{}', valor_nuevo: '{"id_intento":4,"estado":"ENVIADO"}',
    fecha_cambio: '2026-05-08T16:45:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 7, id_intento: 4, accion: AuditAction.CAMBIO_ESTADO,
    valor_anterior: '{"estado":"ENVIADO"}', valor_nuevo: '{"estado":"RECHAZADO"}',
    fecha_cambio: '2026-05-08T16:50:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 8, id_intento: 5, accion: AuditAction.CREACION_INTENTO,
    valor_anterior: '{}', valor_nuevo: '{"id_intento":5,"estado":"ENVIADO"}',
    fecha_cambio: '2026-05-19T08:00:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 9, id_intento: 5, accion: AuditAction.CAMBIO_ESTADO,
    valor_anterior: '{"estado":"ENVIADO"}', valor_nuevo: '{"estado":"PROCESANDO"}',
    fecha_cambio: '2026-05-19T08:01:00', ejecutado_por: 1,
  },
  {
    id_auditoria: 10, id_intento: 6, accion: AuditAction.CREACION_INTENTO,
    valor_anterior: '{}', valor_nuevo: '{"id_intento":6,"estado":"ENVIADO"}',
    fecha_cambio: '2026-05-19T11:00:00', ejecutado_por: 1,
  },
];

export const MOCK_PLAGIARISM_REPORTS: PlagiarismReport[] = [
  {
    id_reporte: 1, id_intento_ref: 1, porcentaje_similitud_total: 12,
    id_externo_turnitin: 'TT-2026-001', estado_analisis: PlagiarismStatus.COMPLETADO,
    fecha_analisis: '2026-05-15T10:40:00',
  },
  {
    id_reporte: 2, id_intento_ref: 2, porcentaje_similitud_total: 85,
    id_externo_turnitin: 'TT-2026-002', estado_analisis: PlagiarismStatus.COMPLETADO,
    fecha_analisis: '2026-05-16T14:30:00',
  },
  {
    id_reporte: 3, id_intento_ref: 3, porcentaje_similitud_total: 45,
    id_externo_turnitin: 'TT-2026-003', estado_analisis: PlagiarismStatus.COMPLETADO,
    fecha_analisis: '2026-05-17T09:10:00',
  },
  {
    id_reporte: 4, id_intento_ref: 4, porcentaje_similitud_total: 92,
    id_externo_turnitin: null, estado_analisis: PlagiarismStatus.COMPLETADO,
    fecha_analisis: '2026-05-08T17:00:00',
  },
  {
    id_reporte: 5, id_intento_ref: 5, porcentaje_similitud_total: 0,
    id_externo_turnitin: null, estado_analisis: PlagiarismStatus.PENDIENTE,
    fecha_analisis: '2026-05-19T08:00:00',
  },
];

export const MOCK_PLAGIARISM_MATCHES: PlagiarismMatch[] = [
  { id_reporte: 1, id_firma_coincidente: 101, porcentaje_coincidencia: 12 },
  { id_reporte: 2, id_firma_coincidente: 102, porcentaje_coincidencia: 85 },
  { id_reporte: 2, id_firma_coincidente: 103, porcentaje_coincidencia: 72 },
  { id_reporte: 3, id_firma_coincidente: 104, porcentaje_coincidencia: 45 },
  { id_reporte: 4, id_firma_coincidente: 105, porcentaje_coincidencia: 92 },
  { id_reporte: 4, id_firma_coincidente: 106, porcentaje_coincidencia: 88 },
];
