import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { Attempt, AttemptCreate } from '@core/models';

@Injectable({ providedIn: 'root' })
export class AttemptService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.apiBaseUrl;

  async getByStudent(skip = 0, limit = 50): Promise<Attempt[]> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return firstValueFrom(
      this.http.get<Attempt[]>(`${this.apiUrl}/api/estudiante/intentos`, { params }),
    );
  }

  async create(request: AttemptCreate): Promise<Attempt> {
    return firstValueFrom(
      this.http.post<Attempt>(`${this.apiUrl}/api/estudiante/intentos`, request),
    );
  }

  async updateUrl(id: number, nuevaUrl: string): Promise<Attempt> {
    const params = new HttpParams().set('nueva_url', nuevaUrl);
    return firstValueFrom(
      this.http.put<Attempt>(`${this.apiUrl}/api/estudiante/intentos/${id}`, null, { params }),
    );
  }

  async delete(id: number): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/api/estudiante/intentos/${id}`));
  }
}
