export type QueryFormValue = string | boolean;

export interface QueryForm {
  courses: string;
  departments: string;
  show_direct_prerequisites: boolean;
  show_transitive_prerequisites: boolean;
  show_disconnected_courses: boolean;
}

export interface Query {
  courses: string[];
  departments: string[];
  show_direct_prerequisites: boolean;
  show_transitive_prerequisites: boolean;
  show_disconnected_courses: boolean;
}