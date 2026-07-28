import { Component } from '@angular/core';
import { MsalService } from '@azure/msal-angular';

@Component({ selector: 'app-root', templateUrl: './app.component.html', styleUrls: ['./app.component.css'] })
export class AppComponent {
  constructor(private readonly msal: MsalService) {}
  get isAuthenticated(): boolean { return this.msal.instance.getAllAccounts().length > 0; }
  login(): void { this.msal.loginRedirect(); }
  logout(): void { this.msal.logoutRedirect(); }
}
