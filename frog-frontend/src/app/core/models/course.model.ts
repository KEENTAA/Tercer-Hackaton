export interface Course {
  id_curso: number;
  codigo_curso: string;
  nombre: string;
  gestion: string;
  id_profesor: number;
}

export interface CourseEnrollment {
  id_curso: number;
  id_estudiante: number;
  fecha_inscripcion: string;
}

export type CreateCourseRequest = Omit<Course, 'id_curso'>;
export type UpdateCourseRequest = Partial<CreateCourseRequest>;
export type EnrollStudentRequest = Omit<CourseEnrollment, 'fecha_inscripcion'>;
