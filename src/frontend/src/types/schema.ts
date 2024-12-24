import { ApiResponse } from "./api";

// metadato associato alla colonna
export interface Column {
  name: string;
  type: string;
  nullable: boolean;
  isPrimaryKey: boolean;
}

// relazioni delle tabelle
export interface Relationship {
  fromColumns: string[];
  toTable: string;
  toColumns: string[];
}

// info per le tabelle
export interface Table {
  name: string;
  columns: Column[];
  relationships: Relationship[];
}

// tabelle dello schema
export interface SchemaMetadata {
  tables: Table[];
}

export interface SchemaResponse extends ApiResponse {
  data?: SchemaMetadata;
}
