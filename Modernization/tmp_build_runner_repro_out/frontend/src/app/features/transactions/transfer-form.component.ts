import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { TransferRequest } from '../../core/models/transaction.model';
import { TransactionService } from '../../core/services/transaction.service';
@Component({ selector: 'app-transfer-form', templateUrl: './transfer-form.component.html', styleUrls: ['./transfer-form.component.css'] })
export class TransferFormComponent {
  isSubmitting = false;
  readonly transferForm: FormGroup;
  constructor(private readonly fb: FormBuilder, private readonly service: TransactionService) {
    this.transferForm = this.fb.nonNullable.group({ idempotencyKey: ['', Validators.required], amount: [0, Validators.min(0.01)], sourceAccountId: [0, Validators.required], destinationAccountId: [0, Validators.required] });
  }
  async onSubmit(): Promise<void> {
    if (this.transferForm.invalid || this.isSubmitting) return;
    this.isSubmitting = true;
    try { await firstValueFrom(this.service.transfer(this.transferForm.getRawValue() as TransferRequest)); this.transferForm.reset(); }
    finally { this.isSubmitting = false; }
  }
}
