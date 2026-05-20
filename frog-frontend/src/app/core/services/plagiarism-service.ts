import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { PlagiarismReport, PlagiarismReportWithMatches } from '@core/models';

@Injectable({ providedIn: 'root' })
export class PlagiarismService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.plagiarismBaseUrl;

  async getByAttempt(attemptId: number): Promise<PlagiarismReportWithMatches | null> {
    return firstValueFrom(
      this.http.get<PlagiarismReportWithMatches | null>(
        `${this.apiUrl}/resultado/${attemptId}`,
      ),
    );
  }

  async getByTask(taskId: number): Promise<PlagiarismReport[]> {
    return firstValueFrom(
      this.http.get<PlagiarismReport[]>(
        `${env.apiBaseUrl}/api/plagiarism/task/${taskId}`,
      ),
    );
  }

  async triggerAnalysis(attemptId: number): Promise<{ message: string; id_intento: number }> {
    return firstValueFrom(
      this.http.post<{ message: string; id_intento: number }>(
        `${this.apiUrl}/analizar`,
        { id_intento: attemptId },
      ),
    );
  }

  async getHighRiskReports(threshold = 70): Promise<PlagiarismReport[]> {
    const params = new HttpParams().set('threshold', threshold.toString());
    return firstValueFrom(
      this.http.get<PlagiarismReport[]>(
        `${env.apiBaseUrl}/api/plagiarism/high-risk`,
        { params },
      ),
    );
  }
}
