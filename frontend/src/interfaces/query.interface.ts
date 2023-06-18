export type QueryValue = string | string[] | number | boolean;

export interface Query {
  [key: string]: QueryValue;
}
