export interface ApiResponse {
  success: boolean;
  error?: string;
}

// i types di questa cartella rappresentano le interfacce di comunicazione con l'API
// sono il contratto tra frontend e backend
// non rappresentano i types dello stato interno dei componenti React,
// che sono invece specificati all'interno dei file delle cartelle specifiche in components
