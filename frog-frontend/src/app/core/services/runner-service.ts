import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { TestCase, TestCaseCreate, ExecuteRequest, ExecutionResult, ExecuteResponse } from '@core/models';

@Injectable({ providedIn: 'root' })
export class RunnerService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.runnerBaseUrl;

  async createTestCase(request: TestCaseCreate): Promise<TestCase> {
    return firstValueFrom(
      this.http.post<TestCase>(`${this.apiUrl}/runner/test-cases`, request),
    );
  }

  async getTestCasesByAssignment(idTareaRef: number): Promise<TestCase[]> {
    return firstValueFrom(
      this.http.get<TestCase[]>(`${this.apiUrl}/runner/test-cases/assignment/${idTareaRef}`),
    );
  }

  async execute(request: ExecuteRequest): Promise<ExecuteResponse> {
    return firstValueFrom(
      this.http.post<ExecuteResponse>(`${this.apiUrl}/runner/execute`, request),
    );
  }

  async getResults(idIntentoRef: number): Promise<ExecutionResult | null> {
    return firstValueFrom(
      this.http.get<ExecutionResult | null>(`${this.apiUrl}/runner/results/${idIntentoRef}`),
    );
  }

  async getResultsByAssignment(idTareaRef: number): Promise<ExecutionResult[]> {
    return firstValueFrom(
      this.http.get<ExecutionResult[]>(`${this.apiUrl}/runner/results/assignment/${idTareaRef}`),
    );
  }
}
