import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { delay, of, throwError } from 'rxjs';
import { mockDb } from '../mocks/mock-db';
import { MOCK_USERS } from '../mocks/mock-data';
import { env } from '../../../environments/environment';
import { AuditLog, PlagiarismReport, PlagiarismMatch, ExecutionResult, GradeByCriterion } from '../models';
import { AttemptStatus, AuditAction, PlagiarismStatus } from '../models';

const MOCK_DELAY_MS = 500;

function getSessionUser() {
  const raw = localStorage.getItem('frog_user');
  return raw ? JSON.parse(raw) : null;
}

function setSessionUser(user: any) {
  localStorage.setItem('frog_user', JSON.stringify(user));
  localStorage.setItem('frog_token', `mock-token-${user.id_usuario}`);
}

function clearSession() {
  localStorage.removeItem('frog_user');
  localStorage.removeItem('frog_token');
}

function paginated<T>(data: T[], skip: number, limit: number) {
  return data.slice(skip, skip + limit);
}

function extractPath(url: string): string | null {
  if (url.startsWith(env.apiBaseUrl)) {
    return url.replace(env.apiBaseUrl, '');
  }
  if (url.startsWith(env.plagiarismBaseUrl)) {
    return url.replace(env.plagiarismBaseUrl, '');
  }
  return null;
}

function handleRequest(method: string, url: string, body: unknown): { status: number; body: unknown } | null {
  const path = extractPath(url);
  if (!path) return null;

  // ── AUTH ──
  if (method === 'POST' && path === '/api/auth/login') {
    const req = body as { codigo_universitario: string; password: string };
    const found = MOCK_USERS.find(
      (u) => u.codigo_universitario === req.codigo_universitario && u.password === req.password,
    );
    if (!found) {
      return { status: 401, body: { detail: 'Credenciales incorrectas' } };
    }
    setSessionUser(found.user);
    return {
      status: 200,
      body: { access_token: `mock-token-${found.user.id_usuario}`, token_type: 'bearer' },
    };
  }

  if (method === 'POST' && path === '/api/auth/registro') {
    const newUser = { ...(body as any), id_usuario: mockDb.courses.length + 100 };
    return { status: 201, body: newUser };
  }

  if (method === 'GET' && path === '/api/auth/me') {
    const user = getSessionUser();
    if (!user) return { status: 401, body: { detail: 'No autenticado' } };
    return { status: 200, body: user };
  }

  if (method === 'PUT' && path === '/api/auth/me') {
    const user = getSessionUser();
    if (!user) return { status: 401, body: { detail: 'No autenticado' } };
    const updated = { ...user, ...(body as any) };
    setSessionUser(updated);
    return { status: 200, body: updated };
  }

  // ── COURSES (Professor) ──
  if (method === 'GET' && path === '/api/profesor/cursos') {
    const urlObj = new URL(url);
    const skip = parseInt(urlObj.searchParams.get('skip') || '0');
    const limit = parseInt(urlObj.searchParams.get('limit') || '100');
    return { status: 200, body: paginated(mockDb.courses, skip, limit) };
  }

  if (method === 'POST' && path === '/api/profesor/cursos') {
    const course = mockDb.addCourse(body as any);
    return { status: 201, body: course };
  }

  if (method === 'PUT' && path.match(/^\/api\/profesor\/cursos\/\d+$/)) {
    const id = parseInt(path.split('/').pop()!);
    const course = mockDb.courses.find((c) => c.id_curso === id);
    if (!course) return { status: 404, body: { detail: 'Curso no encontrado' } };
    const updates = body as any;
    Object.assign(course, updates);
    return { status: 200, body: course };
  }

  if (method === 'DELETE' && path.match(/^\/api\/profesor\/cursos\/\d+$/)) {
    const id = parseInt(path.split('/').pop()!);
    mockDb.courses = mockDb.courses.filter((c) => c.id_curso !== id);
    return { status: 200, body: null };
  }

  if (method === 'GET' && path === '/api/profesor/estudiantes') {
    const urlObj = new URL(url);
    const skip = parseInt(urlObj.searchParams.get('skip') || '0');
    const limit = parseInt(urlObj.searchParams.get('limit') || '100');
    const students = MOCK_USERS.filter((u) => u.user.rol === 'ESTUDIANTE').map((u) => u.user);
    return { status: 200, body: paginated(students, skip, limit) };
  }

  // ── TASKS (Professor) ──
  if (method === 'GET' && path.match(/^\/api\/profesor\/cursos\/\d+\/tareas$/)) {
    const courseId = parseInt(path.split('/')[4]);
    const urlObj = new URL(url);
    const skip = parseInt(urlObj.searchParams.get('skip') || '0');
    const limit = parseInt(urlObj.searchParams.get('limit') || '50');
    const tasks = mockDb.tasks.filter((t) => t.id_curso === courseId);
    return { status: 200, body: paginated(tasks, skip, limit) };
  }

  if (method === 'POST' && path === '/api/profesor/tareas') {
    const taskBody = body as any;
    const task = mockDb.addTask({
      id_tarea: 0,
      id_curso: taskBody.id_curso,
      titulo: taskBody.titulo,
      descripcion: taskBody.descripcion,
      fecha_limite: taskBody.fecha_limite,
      criterios: taskBody.criterios?.map((c: any, i: number) => ({
        id_criterio: 0,
        id_tarea: 0,
        descripcion: c.descripcion,
        ponderacion: c.ponderacion,
      })),
    });
    if (taskBody.criterios) {
      for (const c of taskBody.criterios) {
        mockDb.addCriterion({
          id_criterio: 0,
          id_tarea: task.id_tarea,
          descripcion: c.descripcion,
          ponderacion: c.ponderacion,
        });
      }
    }
    return { status: 201, body: task };
  }

  if (method === 'PUT' && path.match(/^\/api\/profesor\/tareas\/\d+$/)) {
    const id = parseInt(path.split('/').pop()!);
    const task = mockDb.tasks.find((t) => t.id_tarea === id);
    if (!task) return { status: 404, body: { detail: 'Tarea no encontrada' } };
    Object.assign(task, body as any);
    return { status: 200, body: task };
  }

  if (method === 'DELETE' && path.match(/^\/api\/profesor\/tareas\/\d+$/)) {
    const id = parseInt(path.split('/').pop()!);
    mockDb.tasks = mockDb.tasks.filter((t) => t.id_tarea !== id);
    return { status: 200, body: null };
  }

  // ── TASKS (Student) ──
  if (method === 'GET' && path.match(/^\/api\/estudiante\/tareas\/\d+$/)) {
    const courseId = parseInt(path.split('/').pop()!);
    const urlObj = new URL(url);
    const skip = parseInt(urlObj.searchParams.get('skip') || '0');
    const limit = parseInt(urlObj.searchParams.get('limit') || '50');
    const tasks = mockDb.tasks.filter((t) => t.id_curso === courseId);
    return { status: 200, body: paginated(tasks, skip, limit) };
  }

  // ── ATTEMPTS ──
  if (method === 'GET' && path === '/api/estudiante/intentos') {
    const urlObj = new URL(url);
    const skip = parseInt(urlObj.searchParams.get('skip') || '0');
    const limit = parseInt(urlObj.searchParams.get('limit') || '50');
    return { status: 200, body: paginated(mockDb.attempts, skip, limit) };
  }

  if (method === 'POST' && path === '/api/estudiante/intentos') {
    const attemptBody = body as { id_tarea: number; url_codigo_fuente: string };
    const studentAttempts = mockDb.attempts.filter((a) => a.id_tarea === attemptBody.id_tarea);
    const numero = studentAttempts.length + 1;

    const attempt = mockDb.addAttempt({
      id_intento: 0,
      id_estudiante: 1,
      numero_intento: numero,
      fecha_envio: new Date().toISOString(),
      nota_total: null,
      estado: AttemptStatus.ENVIADO,
      id_tarea: attemptBody.id_tarea,
      url_codigo_fuente: attemptBody.url_codigo_fuente,
    });

    mockDb.addAuditLog({
      id_auditoria: 0,
      id_intento: attempt.id_intento,
      accion: AuditAction.CREACION_INTENTO,
      valor_anterior: '{}',
      valor_nuevo: JSON.stringify({ id_intento: attempt.id_intento, estado: 'ENVIADO' }),
      fecha_cambio: new Date().toISOString(),
      ejecutado_por: 1,
    });

    return { status: 201, body: attempt };
  }

  if (method === 'PUT' && path.match(/^\/api\/estudiante\/intentos\/\d+$/)) {
    const id = parseInt(path.split('/').pop()!);
    const attempt = mockDb.attempts.find((a) => a.id_intento === id);
    if (!attempt) return { status: 404, body: { detail: 'Intento no encontrado' } };
    const urlObj = new URL(url);
    const nuevaUrl = urlObj.searchParams.get('nueva_url');
    if (nuevaUrl) attempt.url_codigo_fuente = nuevaUrl;
    return { status: 200, body: attempt };
  }

  if (method === 'DELETE' && path.match(/^\/api\/estudiante\/intentos\/\d+$/)) {
    const id = parseInt(path.split('/').pop()!);
    mockDb.attempts = mockDb.attempts.filter((a) => a.id_intento !== id);
    return { status: 200, body: null };
  }

  // ── PLAGIARISM (mock endpoints - real ones pass through) ──
  if (method === 'GET' && path.match(/^\/api\/plagiarism\/task\/\d+$/)) {
    const taskId = parseInt(path.split('/').pop()!);
    const attemptIds = mockDb.attempts.filter((a) => a.id_tarea === taskId).map((a) => a.id_intento);
    const reports = mockDb.plagiarismReports.filter((r) => attemptIds.includes(r.id_intento_ref));
    return { status: 200, body: reports };
  }

  if (method === 'GET' && path === '/api/plagiarism/high-risk') {
    const urlObj = new URL(url);
    const threshold = parseInt(urlObj.searchParams.get('threshold') || '70');
    const reports = mockDb.plagiarismReports.filter((r) => r.porcentaje_similitud_total >= threshold);
    return { status: 200, body: reports };
  }

  if (method === 'POST' && path.match(/^\/api\/plagiarism\/analyze\/\d+$/)) {
    const attemptId = parseInt(path.split('/').pop()!);
    const report = mockDb.addPlagiarismReport({
      id_reporte: 0,
      id_intento_ref: attemptId,
      porcentaje_similitud_total: Math.floor(Math.random() * 100),
      id_externo_turnitin: `TT-2026-${Date.now()}`,
      estado_analisis: PlagiarismStatus.COMPLETADO,
      fecha_analisis: new Date().toISOString(),
    });
    return { status: 201, body: report };
  }

  if (method === 'GET' && path.match(/^\/api\/plagiarism\/attempt\/\d+$/)) {
    const attemptId = parseInt(path.split('/').pop()!);
    const report = mockDb.plagiarismReports.find((r) => r.id_intento_ref === attemptId);
    if (!report) return { status: 200, body: null };
    const coincidencias = mockDb.plagiarismMatches.filter((m) => m.id_reporte === report.id_reporte);
    return { status: 200, body: { ...report, coincidencias } };
  }

  // ── AUDIT ──
  if (method === 'GET' && path === '/api/profesor/auditoria') {
    const urlObj = new URL(url);
    const skip = parseInt(urlObj.searchParams.get('skip') || '0');
    const limit = parseInt(urlObj.searchParams.get('limit') || '50');
    return { status: 200, body: paginated(mockDb.auditLogs, skip, limit) };
  }

  return null;
}

export const mockInterceptor: HttpInterceptorFn = (req, next) => {
  if (!env.useMocks) {
    return next(req);
  }

  const result = handleRequest(req.method, req.url, req.body);

  if (!result) {
    return next(req);
  }

  if (result.status >= 400) {
    return throwError(() => ({ status: result.status, error: result.body })).pipe(delay(MOCK_DELAY_MS));
  }

  const response = new HttpResponse({
    status: result.status,
    body: result.body,
  });

  return of(response).pipe(delay(MOCK_DELAY_MS));
};
