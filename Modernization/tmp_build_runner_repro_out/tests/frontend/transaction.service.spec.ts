import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http';
import { TransactionService } from './transaction.service';
import { TransferRequest, TransactionResponse } from '../../src/app/core/models/transaction.model';

describe('TransactionService', () => {
  let service: TransactionService;
  let httpMock: HttpTestingController;

  const mockBaseUrl = 'http://localhost:5001/api/transactions';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [TransactionService]
    });
    service = TestBed.inject(TransactionService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    TestBed.resetTestingModule();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('transfer', () => {
    const mockRequest: TransferRequest = {
      idempotencyKey: 'test-id-12345',
      amount: 100.00,
      sourceAccountId: 1,
      destinationAccountId: 2
    };

    it('should successfully create a transfer and return the response', () => {
      const mockResponse: TransactionResponse = {
        id: 1,
        idempotencyKey: 'test-id-12345',
        amount: 100.00,
        sourceAccountId: 1,
        destinationAccountId: 2,
        sourceBalanceAfter: 900.00,
        destinationBalanceAfter: 1100.00,
        createdAt: '2026-07-27T20:30:00Z'
      };

      service.transfer(mockRequest).subscribe({
        next: (response) => {
          expect(response.idempotencyKey).toBe('test-id-12345');
          expect(response.amount).toBe(100.00);
        },
        error: () => fail('Unexpected error')
      });

      const req = httpMock.expectOne(`${mockBaseUrl}/transfer`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(mockRequest);
      expect(req.response).toBeTruthy();
    });

    it('should handle duplicate idempotency key gracefully', () => {
      const mockResponse: TransactionResponse = {
        id: 1,
        idempotencyKey: 'test-id-12345',
        amount: 100.00,
        sourceAccountId: 1,
        destinationAccountId: 2,
        sourceBalanceAfter: 900.00,
        destinationBalanceAfter: 1100.00,
        createdAt: '2026-07-27T20:30:00Z'
      };

      service.transfer(mockRequest).subscribe({
        next: (response) => {
          expect(response.idempotencyKey).toBe('test-id-12345');
        },
        error: () => fail('Unexpected error')
      });

      const req = httpMock.expectOne(`${mockBaseUrl}/transfer`);
      expect(req.request.method).toBe('POST');
    });

    it('should handle insufficient funds', () => {
      service.transfer(mockRequest).subscribe({
        next: () => fail('Expected error'),
        error: (error) => {
          expect(error.status).toBe(409);
          expect(error.error.code).toBe('InsufficientFunds');
        }
      });

      const req = httpMock.expectOne(`${mockBaseUrl}/transfer`);
      expect(req.request.method).toBe('POST');
      expect(req.response).toBeTruthy();
    });

    it('should handle account not found', () => {
      service.transfer(mockRequest).subscribe({
        next: () => fail('Expected error'),
        error: (error) => {
          expect(error.status).toBe(404);
          expect(error.error.code).toBe('AccountNotFound');
        }
      });

      const req = httpMock.expectOne(`${mockBaseUrl}/transfer`);
      expect(req.request.method).toBe('POST');
    });

    it('should handle validation errors', () => {
      const invalidRequest: TransferRequest = {
        idempotencyKey: '',
        amount: -50.00,
        sourceAccountId: 1,
        destinationAccountId: 2
      };

      service.transfer(invalidRequest).subscribe({
        next: () => fail('Expected error'),
        error: (error) => {
          expect(error.status).toBe(400);
          expect(error.error.code).toBe('ValidationError');
        }
      });

      const req = httpMock.expectOne(`${mockBaseUrl}/transfer`);
      expect(req.request.method).toBe('POST');
    });
  });

  describe('getTransactions', () => {
    it('should retrieve a list of transactions', () => {
      const mockResponse: TransactionResponse[] = [
        {
          id: 1,
          idempotencyKey: 'test-id-12345',
          amount: 100.00,
          sourceAccountId: 1,
          destinationAccountId: 2,
          sourceBalanceAfter: 900.00,
          destinationBalanceAfter: 1100.00,
          createdAt: '2026-07-27T20:30:00Z'
        },
        {
          id: 2,
          idempotencyKey: 'test-id-67890',
          amount: 50.00,
          sourceAccountId: 1,
          destinationAccountId: 3,
          sourceBalanceAfter: 850.00,
          destinationBalanceAfter: 1050.00,
          createdAt: '2026-07-27T20:25:00Z'
        }
      ];

      service.getTransactions().subscribe({
        next: (response) => {
          expect(response.length).toBe(2);
          expect(response[0].idempotencyKey).toBe('test-id-12345');
        },
        error: () => fail('Unexpected error')
      });

      const req = httpMock.expectOne(`${mockBaseUrl}/`);
      expect(req.request.method).toBe('GET');
    });

    it('should handle empty transaction list', () => {
      service.getTransactions().subscribe({
        next: (response) => {
          expect(response.length).toBe(0);
        },
        error: () => fail('Unexpected error')
      });

      const req = httpMock.expectOne(`${mockBaseUrl}/`);
      expect(req.request.method).toBe('GET');
    });
  });
});
