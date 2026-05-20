export enum UserRole {
  ESTUDIANTE = 'ESTUDIANTE',
  PROFESOR = 'PROFESOR',
  ADMIN = 'ADMIN',
}

export interface User {
  id_usuario: number;
  codigo_universitario: string;
  nombre: string;
  correo: string;
  rol: UserRole;
}

export interface LoginRequest {
  codigo_universitario: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserCreate {
  codigo_universitario: string;
  nombre: string;
  correo: string;
  rol: string;
  password: string;
}

export interface UserUpdate {
  nombre?: string;
  correo?: string;
  password?: string;
}
