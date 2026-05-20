import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { PlagiarismReport, PlagiarismReportWithMatches } from '@core/models';

@Injectable({ providedIn: 'root' })
export class PlagiarismService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.apiBaseUrl;

  async getByAttempt(attemptId: number): Promise<PlagiarismReportWithMatches | null> {
    return firstValueFrom(
      this.http.get<PlagiarismReportWithMatches | null>(
        `${this.apiUrl}/api/plagiarism/attempt/${attemptId}`,
      ),
    );
  }

  async getByTask(taskId: number): Promise<PlagiarismReport[]> {
    return firstValueFrom(
      this.http.get<PlagiarismReport[]>(`${this.apiUrl}/api/plagiarism/task/${taskId}`),
    );
  }

  async triggerAnalysis(attemptId: number): Promise<PlagiarismReport> {
    return firstValueFrom(
      this.http.post<PlagiarismReport>(
        `${this.apiUrl}/api/plagiarism/analyze/${attemptId}`,
        {},
      ),
    );
  }

  async getHighRiskReports(threshold = 70): Promise<PlagiarismReport[]> {
    return firstValueFrom(
      this.http.get<PlagiarismReport[]>(
        `${this.apiUrl}/api/plagiarism/high-risk?threshold=${threshold}`,
      ),
    );
  }
}
