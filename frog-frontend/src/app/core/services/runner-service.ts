import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import {
  CasoPruebaCreateBatch,
  CasoPruebaResponse,
  EjecucionRequest,
  EjecucionResponse,
  ResultadoEjecucionResponse,
} from '@core/models';

@Injectable({ providedIn: 'root' })
export class RunnerService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.runnerBaseUrl;

  async createTestCases(batch: CasoPruebaCreateBatch): Promise<CasoPruebaResponse[]> {
    return firstValueFrom(
      this.http.post<CasoPruebaResponse[]>(`${this.apiUrl}/runner/test-cases`, batch),
    );
  }

  async getTestCasesByAssignment(idTareaRef: number): Promise<CasoPruebaResponse[]> {
    return firstValueFrom(
      this.http.get<CasoPruebaResponse[]>(`${this.apiUrl}/runner/test-cases/assignment/${idTareaRef}`),
    );
  }

  async execute(request: EjecucionRequest): Promise<EjecucionResponse> {
    return firstValueFrom(
      this.http.post<EjecucionResponse>(`${this.apiUrl}/runner/execute`, request),
    );
  }

  async getResults(idIntentoRef: number): Promise<ResultadoEjecucionResponse | null> {
    return firstValueFrom(
      this.http.get<ResultadoEjecucionResponse | null>(`${this.apiUrl}/runner/results/${idIntentoRef}`),
    );
  }

  async getResultsByAssignment(idTareaRef: number): Promise<ResultadoEjecucionResponse[]> {
    return firstValueFrom(
      this.http.get<ResultadoEjecucionResponse[]>(`${this.apiUrl}/runner/results/assignment/${idTareaRef}`),
    );
  }
}
