import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { env } from '../../../environments/environment';
import { User, LoginRequest, LoginResponse, UserCreate, UserUpdate } from '@core/models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = env.apiBaseUrl;
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

  async login(request: LoginRequest): Promise<void> {
    const response = await firstValueFrom(
      this.http.post<LoginResponse>(`${this.apiUrl}/api/auth/login`, request),
    );
    localStorage.setItem(this.TOKEN_KEY, response.access_token);
    this.tokenSignal.set(response.access_token);
  }

  async getMe(): Promise<User> {
    const response = await firstValueFrom(
      this.http.get<User>(`${this.apiUrl}/api/auth/me`),
    );
    localStorage.setItem('frog_user', JSON.stringify(response));
    this.userSignal.set(response);
    return response;
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

  async register(request: UserCreate): Promise<User> {
    const response = await firstValueFrom(
      this.http.post<User>(`${this.apiUrl}/api/auth/registro`, request),
    );
    return response;
  }

  async updateMe(request: UserUpdate): Promise<User> {
    const response = await firstValueFrom(
      this.http.put<User>(`${this.apiUrl}/api/auth/me`, request),
    );
    localStorage.setItem('frog_user', JSON.stringify(response));
    this.userSignal.set(response);
    return response;
  }
}
