import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { AuditLog, PaginatedResponse } from '@core/models';

@Injectable({ providedIn: 'root' })
export class AuditService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${env.apiUrl}/audit`;

  async list(page = 1, pageSize = 50): Promise<PaginatedResponse<AuditLog>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    const response = await firstValueFrom(
      this.http.get<PaginatedResponse<AuditLog>>(this.apiUrl, { params }),
    );
    return response;
  }

  async getByAttempt(attemptId: number): Promise<AuditLog[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: AuditLog[] }>(`${this.apiUrl}/attempt/${attemptId}`),
    );
    return response.data;
  }

  async getByDateRange(from: string, to: string): Promise<AuditLog[]> {
    const params = new HttpParams()
      .set('from', from)
      .set('to', to);
    const response = await firstValueFrom(
      this.http.get<{ data: AuditLog[] }>(`${this.apiUrl}/range`, { params }),
    );
    return response.data;
  }

  async getByUser(userId: number): Promise<AuditLog[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: AuditLog[] }>(`${this.apiUrl}/user/${userId}`),
    );
    return response.data;
  }
}
