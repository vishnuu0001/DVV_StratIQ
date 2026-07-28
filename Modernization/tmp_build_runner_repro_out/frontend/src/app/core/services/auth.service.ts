import { Injectable } from '@angular/core';
import { MsalService } from '@azure/msal-angular';
import { AccountInfo } from '@azure/msal-browser';

// Thin wrapper over MsalService — MSAL owns token acquisition and the token
// cache. Never read/write a token to localStorage here: MsalInterceptor
// attaches it to outgoing requests directly, and a hand-rolled token store
// here would silently disagree with the one MSAL actually uses.
@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(private msalService: MsalService) {}

  isAuthenticated(): boolean {
    return this.msalService.instance.getAllAccounts().length > 0;
  }

  getActiveAccount(): AccountInfo | null {
    return this.msalService.instance.getActiveAccount();
  }

  logout(): void {
    this.msalService.logoutRedirect();
  }
}
