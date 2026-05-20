import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { User, LoginRequest, LoginResponse, CreateUserRequest, UpdateUserRequest } from '@core/models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${env.apiUrl}/auth`;
  private readonly TOKEN_KEY = 'frog_token';

  private userSignal = signal<User | null>(this.loadUserFromStorage());
  private tokenSignal = signal<string | null>(this.loadTokenFromStorage());

  currentUser = this.userSignal.asReadonly();
  isLoggedIn = computed(() => this.tokenSignal() !== null);
  userRole = computed(() => this.userSignal()?.rol ?? null);

  private loadTokenFromStorage(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private loadUserFromStorage(): User | null {
    const raw = localStorage.getItem('frog_user');
    return raw ? JSON.parse(raw) : null;
  }

  async login(request: LoginRequest): Promise<User> {
    const response = await firstValueFrom(
      this.http.post<LoginResponse>(`${this.apiUrl}/login`, request),
    );
    localStorage.setItem(this.TOKEN_KEY, response.token);
    localStorage.setItem('frog_user', JSON.stringify(response.user));
    this.tokenSignal.set(response.token);
    this.userSignal.set(response.user);
    return response.user;
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('frog_user');
    this.tokenSignal.set(null);
    this.userSignal.set(null);
  }

  getToken(): string | null {
    return this.tokenSignal();
  }

  async register(request: CreateUserRequest): Promise<User> {
    const response = await firstValueFrom(
      this.http.post<{ data: User }>(`${this.apiUrl}/register`, request),
    );
    return response.data;
  }

  async updateUser(id: number, request: UpdateUserRequest): Promise<User> {
    const response = await firstValueFrom(
      this.http.put<{ data: User }>(`${this.apiUrl}/users/${id}`, request),
    );
    return response.data;
  }
}
