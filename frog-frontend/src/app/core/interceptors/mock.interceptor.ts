import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { delay, of, throwError } from 'rxjs';
import { mockDb } from '../mocks/mock-db';
import { MOCK_USERS } from '../mocks/mock-data';
import { env } from '../../../environments/environment';
import { AuditLog, PlagiarismReport, PlagiarismMatch, ExecutionResult, GradeByCriterion } from '../models';
import { AttemptStatus, AuditAction, PlagiarismStatus } from '../models';

const MOCK_DELAY_MS = 500;

function paginated<T>(data: T[], page: number, pageSize: number) {
  const start = (page - 1) * pageSize;
  return {
    data: data.slice(start, start + pageSize),
    total: data.length,
    page,
    pageSize,
  };
}

function wrap<T>(data: T) {
  return { data };
}

function handleRequest(method: string, url: string, body: unknown): { status: number; body: unknown } | null {
  const base = env.apiUrl;
  const path = url.replace(base, '');

  // ── AUTH ──
  if (method === 'POST' && path === '/auth/login') {
    const req = body as { codigo_universitario: string; password: string };
    const found = MOCK_USERS.find(
      (u) => u.codigo_universitario === req.codigo_universitario && u.password === req.password,
    );
    if (!found) {
      return { status: 401, body: { message: 'Credenciales incorrectas' } };
    }
    return {
      status: 200,
      body: { token: `mock-token-${found.user.id_usuario}`, user: found.user },
    };
  }

  if (method === 'POST' && path === '/auth/register') {
    return { status: 201, body: { data: (body as any) } };
  }

  // ── COURSES ──
  if (method === 'GET' && path === '/courses') {
    return { status: 200, body: paginated(mockDb.courses, 1, 20) };
  }

  if (method === 'GET' && path.match(/^\/courses\/student\/(\d+)$/)) {
    return { status: 200, body: wrap(mockDb.courses) };
  }

  if (method === 'GET' && path.match(/^\/courses\/(\d+)$/)) {
    const id = parseInt(path.split('/').pop()!);
    const course = mockDb.courses.find((c) => c.id_curso === id);
    return course ? { status: 200, body: wrap(course) } : { status: 404, body: { message: 'Not found' } };
  }

  if (method === 'POST' && path === '/courses') {
    const course = mockDb.addCourse(body as any);
    return { status: 201, body: wrap(course) };
  }

  // ── TASKS ──
  if (method === 'GET' && path === '/tasks') {
    return { status: 200, body: paginated(mockDb.tasks, 1, 20) };
  }

  if (method === 'GET' && path.match(/^\/tasks\/course\/(\d+)$/)) {
    const courseId = parseInt(path.split('/').pop()!);
    const tasks = mockDb.tasks.filter((t) => t.id_curso === courseId);
    return { status: 200, body: wrap(tasks) };
  }

  if (method === 'GET' && path.match(/^\/tasks\/(\d+)$/)) {
    const id = parseInt(path.split('/').pop()!);
    const task = mockDb.tasks.find((t) => t.id_tarea === id);
    return task ? { status: 200, body: wrap(task) } : { status: 404, body: { message: 'Not found' } };
  }

  if (method === 'POST' && path === '/tasks') {
    const task = mockDb.addTask(body as any);
    return { status: 201, body: wrap(task) };
  }

  if (method === 'DELETE' && path.match(/^\/tasks\/(\d+)$/)) {
    const id = parseInt(path.split('/').pop()!);
    mockDb.tasks = mockDb.tasks.filter((t) => t.id_tarea !== id);
    return { status: 200, body: null };
  }

  // ── CRITERIA ──
  if (method === 'GET' && path.match(/^\/tasks\/(\d+)\/criteria$/)) {
    const taskId = parseInt(path.split('/')[2]);
    const criteria = mockDb.criteria.filter((c) => c.id_tarea === taskId);
    return { status: 200, body: wrap(criteria) };
  }

  if (method === 'POST' && path.match(/^\/tasks\/(\d+)\/criteria$/)) {
    const taskId = parseInt(path.split('/')[2]);
    const criterion = mockDb.addCriterion({ ...(body as any), id_tarea: taskId });
    return { status: 201, body: wrap(criterion) };
  }

  if (method === 'DELETE' && path.match(/^\/tasks\/\d+\/criteria\/(\d+)$/)) {
    const criterionId = parseInt(path.split('/').pop()!);
    mockDb.criteria = mockDb.criteria.filter((c) => c.id_criterio !== criterionId);
    return { status: 200, body: null };
  }

  // ── ATTEMPTS ──
  if (method === 'GET' && path === '/attempts') {
    return { status: 200, body: paginated(mockDb.attempts, 1, 20) };
  }

  if (method === 'GET' && path.match(/^\/attempts\/student\/(\d+)$/)) {
    const studentId = parseInt(path.split('/').pop()!);
    const attempts = mockDb.attempts.filter((a) => a.id_estudiante === studentId);
    return { status: 200, body: wrap(attempts) };
  }

  if (method === 'GET' && path.match(/^\/attempts\/task\/(\d+)$/)) {
    const taskId = parseInt(path.split('/').pop()!);
    const attempts = mockDb.attempts.filter((a) => a.id_tarea === taskId);
    return { status: 200, body: wrap(attempts) };
  }

  if (method === 'GET' && path.match(/^\/attempts\/(\d+)$/)) {
    const id = parseInt(path.split('/').pop()!);
    const attempt = mockDb.attempts.find((a) => a.id_intento === id);
    if (!attempt) return { status: 404, body: { message: 'Not found' } };

    const calificaciones = mockDb.gradesByCriterion.filter((g) => g.id_intento === id);
    const ejecucion = mockDb.executionResults.find((r) => r.id_intento_ref === id);
    const plagio = mockDb.plagiarismReports.find((r) => r.id_intento_ref === id);
    const coincidencias = plagio
      ? mockDb.plagiarismMatches.filter((m) => m.id_reporte === plagio.id_reporte)
      : [];

    return {
      status: 200,
      body: wrap({
        ...attempt,
        calificaciones,
        ejecucion: ejecucion || undefined,
        plagio: plagio
          ? { ...plagio, coincidencias }
          : undefined,
      }),
    };
  }

  if (method === 'POST' && path === '/attempts') {
    const attemptBody = body as { id_tarea: number; url_codigo_fuente: string };
    const task = mockDb.tasks.find((t) => t.id_tarea === attemptBody.id_tarea);
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
      url_codigo_fuente: '',
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

    return { status: 201, body: wrap(attempt) };
  }

  if (method === 'POST' && path.match(/^\/attempts\/(\d+)\/upload$/)) {
    const id = parseInt(path.split('/')[2]);
    const attempt = mockDb.attempts.find((a) => a.id_intento === id);
    if (!attempt) return { status: 404, body: { message: 'Not found' } };
    return { status: 200, body: wrap(attempt) };
  }

  // ── PLAGIARISM ──
  if (method === 'GET' && path === '/plagiarism') {
    return { status: 200, body: paginated(mockDb.plagiarismReports, 1, 20) };
  }

  if (method === 'GET' && path.match(/^\/plagiarism\/attempt\/(\d+)$/)) {
    const attemptId = parseInt(path.split('/').pop()!);
    const report = mockDb.plagiarismReports.find((r) => r.id_intento_ref === attemptId);
    if (!report) return { status: 200, body: { data: null } };
    const coincidencias = mockDb.plagiarismMatches.filter((m) => m.id_reporte === report.id_reporte);
    return { status: 200, body: wrap({ ...report, coincidencias }) };
  }

  if (method === 'GET' && path.match(/^\/plagiarism\/task\/(\d+)$/)) {
    const taskId = parseInt(path.split('/').pop()!);
    const attemptIds = mockDb.attempts.filter((a) => a.id_tarea === taskId).map((a) => a.id_intento);
    const reports = mockDb.plagiarismReports.filter((r) => attemptIds.includes(r.id_intento_ref));
    return { status: 200, body: wrap(reports) };
  }

  if (method === 'GET' && path === '/plagiarism/high-risk') {
    const threshold = parseInt(new URL(url).searchParams.get('threshold') || '70');
    const reports = mockDb.plagiarismReports.filter((r) => r.porcentaje_similitud_total >= threshold);
    return { status: 200, body: wrap(reports) };
  }

  if (method === 'POST' && path.match(/^\/plagiarism\/analyze\/(\d+)$/)) {
    const attemptId = parseInt(path.split('/').pop()!);
    const report = mockDb.addPlagiarismReport({
      id_reporte: 0,
      id_intento_ref: attemptId,
      porcentaje_similitud_total: Math.floor(Math.random() * 100),
      id_externo_turnitin: `TT-2026-${Date.now()}`,
      estado_analisis: PlagiarismStatus.COMPLETADO,
      fecha_analisis: new Date().toISOString(),
    });
    return { status: 201, body: wrap(report) };
  }

  // ── AUDIT ──
  if (method === 'GET' && path === '/audit') {
    return { status: 200, body: paginated(mockDb.auditLogs, 1, 50) };
  }

  if (method === 'GET' && path.match(/^\/audit\/attempt\/(\d+)$/)) {
    const attemptId = parseInt(path.split('/').pop()!);
    const logs = mockDb.auditLogs.filter((l) => l.id_intento === attemptId);
    return { status: 200, body: wrap(logs) };
  }

  if (method === 'GET' && path === '/audit/range') {
    const from = new URL(url).searchParams.get('from');
    const to = new URL(url).searchParams.get('to');
    let logs = mockDb.auditLogs;
    if (from) logs = logs.filter((l) => new Date(l.fecha_cambio) >= new Date(from));
    if (to) logs = logs.filter((l) => new Date(l.fecha_cambio) <= new Date(to));
    return { status: 200, body: wrap(logs) };
  }

  if (method === 'GET' && path.match(/^\/audit\/user\/(\d+)$/)) {
    const userId = parseInt(path.split('/').pop()!);
    const logs = mockDb.auditLogs.filter((l) => l.ejecutado_por === userId);
    return { status: 200, body: wrap(logs) };
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
