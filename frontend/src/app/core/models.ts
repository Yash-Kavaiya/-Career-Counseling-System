// Shared API types mirrored from the backend Pydantic schemas.

export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  consent_given: boolean;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  consent_given: boolean;
}
