import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuditService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.apiBaseUrl;

  async list(skip = 0, limit = 50): Promise<unknown[]> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return firstValueFrom(
      this.http.get<unknown[]>(`${this.apiUrl}/api/profesor/auditoria`, { params }),
    );
  }
}
