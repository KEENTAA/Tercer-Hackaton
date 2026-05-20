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
  token: string;
  user: User;
}

export type CreateUserRequest = Omit<User, 'id_usuario'> & { password: string };
export type UpdateUserRequest = Partial<CreateUserRequest>;
