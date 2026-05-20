export interface Course {
  id_curso: number;
  codigo_curso: string;
  nombre: string;
  gestion: string;
  id_profesor: number;
}

export interface CourseCreate {
  codigo_curso: string;
  nombre: string;
  gestion: string;
  id_profesor: number;
}

export interface CourseUpdate {
  nombre?: string;
  gestion?: string;
}
