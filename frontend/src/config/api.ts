// Frontend Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    ME: '/api/auth/me',
  },
  SUBMISSIONS: {
    SUBMIT: '/api/submissions',
    HISTORY: '/api/submissions/history',
    GET: (id: string) => `/api/submissions/${id}`,
  },
  ASSIGNMENTS: {
    LIST: '/api/assignments',
    GET: (id: string) => `/api/assignments/${id}`,
    CREATE: '/api/assignments',
    UPDATE: (id: string) => `/api/assignments/${id}`,
  },
  GRADES: {
    GET: (submissionId: string) => `/api/grades/${submissionId}`,
  },
  PLAGIARISM: {
    GET: (submissionId: string) => `/api/plagiarism/${submissionId}`,
  },
  AUDIT: {
    LOGS: '/api/audit/logs',
  },
};

export const SERVICE_PORTS = {
  GATEWAY: 8000,
  AUTH: 8001,
  USER: 8002,
  ASSIGNMENT: 8003,
  SUBMISSION: 8004,
  EXECUTION: 8005,
  GRADING: 8006,
  PLAGIARISM: 8007,
  AUDIT: 8008,
  LMS: 8009,
};
