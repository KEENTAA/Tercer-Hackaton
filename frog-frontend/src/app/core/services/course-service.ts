import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { Course, CourseCreate, CourseUpdate, User } from '@core/models';

@Injectable({ providedIn: 'root' })
export class CourseService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.apiBaseUrl;

  async list(skip = 0, limit = 100): Promise<Course[]> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return firstValueFrom(
      this.http.get<Course[]>(`${this.apiUrl}/api/profesor/cursos`, { params }),
    );
  }

  async create(request: CourseCreate): Promise<Course> {
    return firstValueFrom(
      this.http.post<Course>(`${this.apiUrl}/api/profesor/cursos`, request),
    );
  }

  async update(id: number, request: CourseUpdate): Promise<Course> {
    return firstValueFrom(
      this.http.put<Course>(`${this.apiUrl}/api/profesor/cursos/${id}`, request),
    );
  }

  async delete(id: number): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/api/profesor/cursos/${id}`));
  }

  async getStudents(skip = 0, limit = 100): Promise<User[]> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return firstValueFrom(
      this.http.get<User[]>(`${this.apiUrl}/api/profesor/estudiantes`, { params }),
    );
  }
}
