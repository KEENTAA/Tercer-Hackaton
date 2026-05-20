import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import {
  Attempt,
  AttemptWithDetails,
  CreateAttemptRequest,
  UpdateAttemptStatus,
  PaginatedResponse,
} from '@core/models';

@Injectable({ providedIn: 'root' })
export class AttemptService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${env.apiUrl}/attempts`;

  async list(page = 1, pageSize = 20): Promise<PaginatedResponse<Attempt>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    const response = await firstValueFrom(
      this.http.get<PaginatedResponse<Attempt>>(this.apiUrl, { params }),
    );
    return response;
  }

  async getByStudent(studentId: number): Promise<Attempt[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: Attempt[] }>(`${this.apiUrl}/student/${studentId}`),
    );
    return response.data;
  }

  async getByTask(taskId: number): Promise<Attempt[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: Attempt[] }>(`${this.apiUrl}/task/${taskId}`),
    );
    return response.data;
  }

  async getById(id: number): Promise<AttemptWithDetails> {
    const response = await firstValueFrom(
      this.http.get<{ data: AttemptWithDetails }>(`${this.apiUrl}/${id}`),
    );
    return response.data;
  }

  async create(request: CreateAttemptRequest): Promise<Attempt> {
    const response = await firstValueFrom(
      this.http.post<{ data: Attempt }>(this.apiUrl, request),
    );
    return response.data;
  }

  async uploadCode(attemptId: number, file: File): Promise<Attempt> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await firstValueFrom(
      this.http.post<{ data: Attempt }>(`${this.apiUrl}/${attemptId}/upload`, formData),
    );
    return response.data;
  }

  async updateStatus(id: number, request: UpdateAttemptStatus): Promise<Attempt> {
    const response = await firstValueFrom(
      this.http.patch<{ data: Attempt }>(`${this.apiUrl}/${id}/status`, request),
    );
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/${id}`));
  }
}
