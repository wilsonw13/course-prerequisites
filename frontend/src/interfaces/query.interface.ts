export type QueryValue = string | number | boolean;

export interface Query {
  [key: string]: QueryValue;
}

export interface QueryOption {
  id: string;
  display_name: string;
  description: string;
  value_type: 'string' | 'number' | 'boolean';
  default_value: QueryValue;
  input_placeholder?: string;
  input_validation?: string;
  character_limit?: number;
}
