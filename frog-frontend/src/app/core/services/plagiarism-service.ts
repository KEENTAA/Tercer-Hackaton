import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { PlagiarismReport, PlagiarismReportWithMatches, PaginatedResponse } from '@core/models';

@Injectable({ providedIn: 'root' })
export class PlagiarismService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${env.apiUrl}/plagiarism`;

  async list(page = 1, pageSize = 20): Promise<PaginatedResponse<PlagiarismReport>> {
    const response = await firstValueFrom(
      this.http.get<PaginatedResponse<PlagiarismReport>>(this.apiUrl, {
        params: { page: page.toString(), pageSize: pageSize.toString() },
      }),
    );
    return response;
  }

  async getByAttempt(attemptId: number): Promise<PlagiarismReportWithMatches | null> {
    const response = await firstValueFrom(
      this.http.get<{ data: PlagiarismReportWithMatches | null }>(
        `${this.apiUrl}/attempt/${attemptId}`,
      ),
    );
    return response.data;
  }

  async getByTask(taskId: number): Promise<PlagiarismReport[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: PlagiarismReport[] }>(`${this.apiUrl}/task/${taskId}`),
    );
    return response.data;
  }

  async triggerAnalysis(attemptId: number): Promise<PlagiarismReport> {
    const response = await firstValueFrom(
      this.http.post<{ data: PlagiarismReport }>(
        `${this.apiUrl}/analyze/${attemptId}`,
        {},
      ),
    );
    return response.data;
  }

  async getHighRiskReports(threshold = 70): Promise<PlagiarismReport[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: PlagiarismReport[] }>(
        `${this.apiUrl}/high-risk?threshold=${threshold}`,
      ),
    );
    return response.data;
  }
}
