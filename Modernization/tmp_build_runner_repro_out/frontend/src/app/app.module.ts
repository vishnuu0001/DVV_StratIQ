import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { MsalGuard, MsalInterceptor, MsalModule } from '@azure/msal-angular';
import { InteractionType, PublicClientApplication } from '@azure/msal-browser';
import { environment } from '../environments/environment';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { TransactionListComponent } from './features/transactions/transaction-list.component';
import { TransferFormComponent } from './features/transactions/transfer-form.component';

                const redirectUri = typeof window !== 'undefined' ? window.location.origin : '/';
                const protectedResourceMap = new Map<string, string[]>([[`${environment.apiBaseUrl}/**`, [`api://${environment.azureAdClientId}/access_as_user`]]]);
@NgModule({
  declarations: [AppComponent, TransactionListComponent, TransferFormComponent],
  imports: [BrowserModule, HttpClientModule, ReactiveFormsModule, AppRoutingModule,
                        MsalModule.forRoot(new PublicClientApplication({ auth: { clientId: environment.azureAdClientId,
                            authority: environment.azureAdAuthority,
                            redirectUri } }),
      { interactionType: InteractionType.Redirect, authRequest: { scopes: ['openid', 'profile'] } },
      { interactionType: InteractionType.Redirect, protectedResourceMap })],
  providers: [MsalGuard, { provide: HTTP_INTERCEPTORS, useClass: MsalInterceptor, multi: true }],
  bootstrap: [AppComponent],
})
export class AppModule {}
