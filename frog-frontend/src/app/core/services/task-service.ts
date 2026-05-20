import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import {
  Task,
  GradingCriterion,
  CreateTaskRequest,
  UpdateTaskRequest,
  CreateCriterionRequest,
  UpdateCriterionRequest,
  PaginatedResponse,
} from '@core/models';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${env.apiUrl}/tasks`;

  async list(page = 1, pageSize = 20): Promise<PaginatedResponse<Task>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    const response = await firstValueFrom(
      this.http.get<PaginatedResponse<Task>>(this.apiUrl, { params }),
    );
    return response;
  }

  async getByCourse(courseId: number): Promise<Task[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: Task[] }>(`${this.apiUrl}/course/${courseId}`),
    );
    return response.data;
  }

  async getById(id: number): Promise<Task> {
    const response = await firstValueFrom(
      this.http.get<{ data: Task }>(`${this.apiUrl}/${id}`),
    );
    return response.data;
  }

  async create(request: CreateTaskRequest): Promise<Task> {
    const response = await firstValueFrom(
      this.http.post<{ data: Task }>(this.apiUrl, request),
    );
    return response.data;
  }

  async update(id: number, request: UpdateTaskRequest): Promise<Task> {
    const response = await firstValueFrom(
      this.http.put<{ data: Task }>(`${this.apiUrl}/${id}`, request),
    );
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/${id}`));
  }

  async getCriteria(taskId: number): Promise<GradingCriterion[]> {
    const response = await firstValueFrom(
      this.http.get<{ data: GradingCriterion[] }>(`${this.apiUrl}/${taskId}/criteria`),
    );
    return response.data;
  }

  async createCriterion(taskId: number, request: CreateCriterionRequest): Promise<GradingCriterion> {
    const response = await firstValueFrom(
      this.http.post<{ data: GradingCriterion }>(`${this.apiUrl}/${taskId}/criteria`, request),
    );
    return response.data;
  }

  async updateCriterion(
    taskId: number,
    criterionId: number,
    request: UpdateCriterionRequest,
  ): Promise<GradingCriterion> {
    const response = await firstValueFrom(
      this.http.put<{ data: GradingCriterion }>(
        `${this.apiUrl}/${taskId}/criteria/${criterionId}`,
        request,
      ),
    );
    return response.data;
  }

  async deleteCriterion(taskId: number, criterionId: number): Promise<void> {
    await firstValueFrom(
      this.http.delete(`${this.apiUrl}/${taskId}/criteria/${criterionId}`),
    );
  }
}
