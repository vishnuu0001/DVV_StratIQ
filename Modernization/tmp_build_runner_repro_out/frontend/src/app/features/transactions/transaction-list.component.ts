import { Component } from '@angular/core';
import { Observable, catchError, of } from 'rxjs';
import { TransactionResponse } from '../../core/models/transaction.model';
import { TransactionService } from '../../core/services/transaction.service';
@Component({ selector: 'app-transaction-list', templateUrl: './transaction-list.component.html', styleUrls: ['./transaction-list.component.css'] })
export class TransactionListComponent {
  readonly transactions$: Observable<TransactionResponse[]>;
  constructor(private readonly service: TransactionService) {
    this.transactions$ = this.service.getTransactions().pipe(catchError(() => of([])));
  }
}
