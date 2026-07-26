# Strat.iQ Tower Consolidation Studio — React Frontend

This React/Vite frontend converts the Excel Tower Consolidation model into a web UI.

## Included Modules

1. Executive Dashboard
2. Assumption Manager
3. Tower Consolidation Studio
4. Transformation Reinvestment Engine
5. Transition Roadmap

## Formula Mapping

The calculation logic is in:

`src/calculations.js`

Core formulas:

```js
addressableSpend = currentSpend * consolidationScope

rateSavings = addressableSpend * rateCompression

productivitySavings = addressableSpend * productivityImprovement

vendorMgmtSavings =
  addressableSpend * vendorMgmtOverhead * vendorMgmtReduction

grossAnnualCapacity =
  rateSavings + productivitySavings + vendorMgmtSavings

transitionCost = addressableSpend * transitionCost

netYear1Capacity = grossAnnualCapacity - transitionCost
```

## Run Locally

```bash
npm install
npm run dev
```

Then open the local Vite URL.

## Production Integration

Replace `src/data.js` with API calls to your backend.

Suggested API endpoints:

- `GET /api/towers`
- `PUT /api/towers/:id`
- `GET /api/assumptions`
- `PUT /api/assumptions`
- `POST /api/scenario/calculate`
- `GET /api/reinvestment`
- `PUT /api/reinvestment`

## Backend Recommendation

- Azure SQL for persistent model data
- FastAPI or .NET API for calculation service
- Azure App Service / Static Web Apps for deployment
