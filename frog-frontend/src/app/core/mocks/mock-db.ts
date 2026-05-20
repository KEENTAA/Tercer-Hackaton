import { Course, Task, GradingCriterion, Attempt, AuditLog, PlagiarismReport, PlagiarismMatch, TestCase, ExecutionResult, GradeByCriterion } from '../models';
import {
  MOCK_COURSES, MOCK_TASKS, MOCK_CRITERIA, MOCK_ATTEMPTS,
  MOCK_AUDIT_LOGS, MOCK_PLAGIARISM_REPORTS, MOCK_PLAGIARISM_MATCHES,
  MOCK_TEST_CASES, MOCK_EXECUTION_RESULTS, MOCK_GRADES_BY_CRITERION,
} from './mock-data';

function clone<T>(data: T): T {
  return JSON.parse(JSON.stringify(data));
}

export class MockDb {
  courses: Course[] = clone(MOCK_COURSES);
  tasks: Task[] = clone(MOCK_TASKS);
  criteria: GradingCriterion[] = clone(MOCK_CRITERIA);
  attempts: Attempt[] = clone(MOCK_ATTEMPTS);
  gradesByCriterion: GradeByCriterion[] = clone(MOCK_GRADES_BY_CRITERION);
  executionResults: ExecutionResult[] = clone(MOCK_EXECUTION_RESULTS);
  testCases: TestCase[] = clone(MOCK_TEST_CASES);
  auditLogs: AuditLog[] = clone(MOCK_AUDIT_LOGS);
  plagiarismReports: PlagiarismReport[] = clone(MOCK_PLAGIARISM_REPORTS);
  plagiarismMatches: PlagiarismMatch[] = clone(MOCK_PLAGIARISM_MATCHES);

  private nextCourseId = 4;
  private nextTaskId = 6;
  private nextCriterionId = 14;
  private nextAttemptId = 7;
  private nextAuditId = 11;
  private nextReportId = 6;
  private nextResultId = 5;

  reset(): void {
    this.courses = clone(MOCK_COURSES);
    this.tasks = clone(MOCK_TASKS);
    this.criteria = clone(MOCK_CRITERIA);
    this.attempts = clone(MOCK_ATTEMPTS);
    this.gradesByCriterion = clone(MOCK_GRADES_BY_CRITERION);
    this.executionResults = clone(MOCK_EXECUTION_RESULTS);
    this.testCases = clone(MOCK_TEST_CASES);
    this.auditLogs = clone(MOCK_AUDIT_LOGS);
    this.plagiarismReports = clone(MOCK_PLAGIARISM_REPORTS);
    this.plagiarismMatches = clone(MOCK_PLAGIARISM_MATCHES);
    this.nextCourseId = 4;
    this.nextTaskId = 6;
    this.nextCriterionId = 14;
    this.nextAttemptId = 7;
    this.nextAuditId = 11;
    this.nextReportId = 6;
    this.nextResultId = 5;
  }

  addCourse(course: Course): Course {
    course.id_curso = this.nextCourseId++;
    this.courses.push(course);
    return course;
  }

  addTask(task: Task): Task {
    task.id_tarea = this.nextTaskId++;
    this.tasks.push(task);
    return task;
  }

  addCriterion(criterion: GradingCriterion): GradingCriterion {
    criterion.id_criterio = this.nextCriterionId++;
    this.criteria.push(criterion);
    return criterion;
  }

  addAttempt(attempt: Attempt): Attempt {
    attempt.id_intento = this.nextAttemptId++;
    this.attempts.push(attempt);
    return attempt;
  }

  addAuditLog(log: AuditLog): AuditLog {
    log.id_auditoria = this.nextAuditId++;
    this.auditLogs.unshift(log);
    return log;
  }

  addPlagiarismReport(report: PlagiarismReport): PlagiarismReport {
    report.id_reporte = this.nextReportId++;
    this.plagiarismReports.push(report);
    return report;
  }

  addExecutionResult(result: ExecutionResult): ExecutionResult {
    result.id_resultado = this.nextResultId++;
    this.executionResults.push(result);
    return result;
  }
}

export const mockDb = new MockDb();
