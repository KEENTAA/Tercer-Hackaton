import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { Task, TaskCreate, TaskUpdate } from '@core/models';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.apiBaseUrl;

  async getByCourse(courseId: number, skip = 0, limit = 50): Promise<Task[]> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return firstValueFrom(
      this.http.get<Task[]>(`${this.apiUrl}/api/profesor/cursos/${courseId}/tareas`, { params }),
    );
  }

  async getTasksByCourseStudent(courseId: number, skip = 0, limit = 50): Promise<Task[]> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return firstValueFrom(
      this.http.get<Task[]>(`${this.apiUrl}/api/estudiante/tareas/${courseId}`, { params }),
    );
  }

  async create(request: TaskCreate): Promise<Task> {
    return firstValueFrom(
      this.http.post<Task>(`${this.apiUrl}/api/profesor/tareas`, request),
    );
  }

  async update(id: number, request: TaskUpdate): Promise<Task> {
    return firstValueFrom(
      this.http.put<Task>(`${this.apiUrl}/api/profesor/tareas/${id}`, request),
    );
  }

  async delete(id: number): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/api/profesor/tareas/${id}`));
  }
}
