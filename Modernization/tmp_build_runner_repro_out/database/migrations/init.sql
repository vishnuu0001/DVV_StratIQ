CREATE TABLE IF NOT EXISTS Accounts (
    Id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    AccountNumber VARCHAR(50)   NOT NULL UNIQUE,
    Balance       DECIMAL(18,2) NOT NULL,
    Currency      VARCHAR(3)    NOT NULL,
    CreatedAt     TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS Transactions (
    Id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    IdempotencyKey          VARCHAR(255)   NOT NULL UNIQUE,
    Amount                  DECIMAL(18,2)  NOT NULL CHECK (Amount > 0),
    SourceAccountId         INTEGER        NOT NULL REFERENCES Accounts(Id),
    DestinationAccountId    INTEGER        NOT NULL REFERENCES Accounts(Id),
    SourceBalanceAfter      DECIMAL(18,2)  NOT NULL,
    DestinationBalanceAfter DECIMAL(18,2)  NOT NULL,
    CreatedAt               TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS IX_Transactions_IdempotencyKey
    ON Transactions(IdempotencyKey);

INSERT INTO Accounts (AccountNumber, Balance, Currency)
VALUES ('ACC-1001', 5000.00, 'USD')
ON CONFLICT (AccountNumber) DO NOTHING;

INSERT INTO Accounts (AccountNumber, Balance, Currency)
VALUES ('ACC-1002', 2500.00, 'USD')
ON CONFLICT (AccountNumber) DO NOTHING;

INSERT INTO Accounts (AccountNumber, Balance, Currency)
VALUES ('ACC-1003', 10000.00, 'USD')
ON CONFLICT (AccountNumber) DO NOTHING;
