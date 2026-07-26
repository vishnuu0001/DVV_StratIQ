# Incident: SolManID# 7000050171 — NAFTA: Cannot Reverse Goods Issue (OSS Note: 265589/2026)

## Summary
A physical shortage of 8 PCA for delivery 149608268 led the user to request a PGI (Post Goods Issue) reversal. The reversal was not possible because the goods receipt had already been posted and handling units (HUs) were involved.

## Analysis
- There was a physical shortage of **8 PCA** for delivery **149608268**.
- The user requested a **PGI reversal** to correct the shortage.
- However, the **goods receipt (GR) had already been posted**, making a direct GR reversal impossible.
- The presence of **handling units (HUs)** further prevented reversing the goods receipt through standard means.
- This is consistent with the known SAP limitation documented in **OSS Note 265589/2026**.

## Root Cause
The GR was already posted and handling units were involved, which blocks the standard PGI/GR reversal process in SAP.

## Resolution
1. A **new delivery 149653758** was created via **transfer posting** to account for the missing 8 PCA.
2. The stock was moved back to the original storage location **UXHR / HU05**.
3. With this stock correction in place, the discrepancy was resolved and the ticket was closed.

## Keywords
- Cannot reverse goods issue
- PGI reversal blocked
- GR already posted
- Handling units HU reversal
- Physical shortage PCA
- Transfer posting
- Delivery reversal SAP
- NAFTA
- OSS Note 265589
- SolManID 7000050171
