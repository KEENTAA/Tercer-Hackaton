export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, string[]>;
}

/** @deprecated Backend uses skip/limit pagination, not page-based */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}
