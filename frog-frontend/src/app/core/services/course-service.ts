import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import {
  Course,
  CourseEnrollment,
  CreateCourseRequest,
  UpdateCourseRequest,
  EnrollStudentRequest,
  PaginatedResponse,
} from '@core/models';

@Injectable({ providedIn: 'root' })
export class CourseService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${env.apiUrl}/courses`;

  async list(page = 1, pageSize = 20): Promise<PaginatedResponse<Course>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    const response = await firstValueFrom(
      this.http.get<PaginatedResponse<Course>>(this.apiUrl, { params }),
    );
    return response;
  }

  async getById(id: number): Promise<Course> {
    const response = await firstValueFrom(
      this.http.get<{ data: Course }>(`${this.apiUrl}/${id}`),
    );
    return response.data;
  }

  async create(request: CreateCourseRequest): Promise<Course> {
    const response = await firstValueFrom(
      this.http.post<{ data: Course }>(this.apiUrl, request),
    );
    return response.data;
  }

  async update(id: number, request: UpdateCourseRequest): Promise<Course> {
    const response = await firstValueFrom(
      this.http.put<{ data: Course }>(`${this.apiUrl}/${id}`, request),
    );
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/${id}`));
  }

  async getEnrollments(courseId: number): Promise<CourseEnrollment[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: CourseEnrollment[] }>(`${this.apiUrl}/${courseId}/enrollments`),
    );
    return response.data;
  }

  async enrollStudent(courseId: number, request: EnrollStudentRequest): Promise<CourseEnrollment> {
    const response = await firstValueFrom(
      this.http.post<{ data: CourseEnrollment }>(`${this.apiUrl}/${courseId}/enrollments`, request),
    );
    return response.data;
  }

  async unenrollStudent(courseId: number, studentId: number): Promise<void> {
    await firstValueFrom(
      this.http.delete(`${this.apiUrl}/${courseId}/enrollments/${studentId}`),
    );
  }

  async getMyCourses(studentId: number): Promise<Course[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: Course[] }>(`${this.apiUrl}/student/${studentId}`),
    );
    return response.data;
  }
}
