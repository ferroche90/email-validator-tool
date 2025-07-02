export interface ValidationResult {
  email: string;
  status: string;
  details?: string | null;
}

export interface ValidateRequest {
  emails: string[];
  enable_smtp: boolean;
  enable_catch_all: boolean;
}

export interface ValidateResponse {
  results: ValidationResult[];
}
