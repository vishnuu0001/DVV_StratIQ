import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MsalGuard } from '@azure/msal-angular';
import { TransactionListComponent } from './features/transactions/transaction-list.component';
import { TransferFormComponent } from './features/transactions/transfer-form.component';

const routes: Routes = [
  { path: 'transactions', component: TransactionListComponent, canActivate: [MsalGuard] },
  { path: 'transfer', component: TransferFormComponent, canActivate: [MsalGuard] },
  { path: '', redirectTo: 'transactions', pathMatch: 'full' },
];

@NgModule({ imports: [RouterModule.forRoot(routes)], exports: [RouterModule] })
export class AppRoutingModule {}
