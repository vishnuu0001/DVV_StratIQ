export interface TransferRequest {
  idempotencyKey: string;
  amount: number;
  sourceAccountId: number;
  destinationAccountId: number;
}

export interface TransactionResponse {
  id: number;
  idempotencyKey: string;
  amount: number;
  sourceAccountId: number;
  destinationAccountId: number;
  sourceBalanceAfter: number;
  destinationBalanceAfter: number;
  createdAt: string;
}
