# Test Strategy

## Objective

The OddLot QA automation suite validates critical user and service behavior for an AI-powered odd-lot stock recommendation product.

The goal is to provide fast, maintainable regression coverage that can run locally and in CI while demonstrating practical Senior QA Automation Engineer / SDET skills.

## Scope

In scope:

- Front-end site reachability and recommendation API availability
- AI recommendation API contract validation (latest row, 10 stocks, required fields)
- AI recommendation API authentication error handling (missing apikey → 401)
- Homepage smoke coverage (title, disclaimer, navigation)
- Recommendation cards rendering with key metrics
- Login-gated favorite behavior and "login coming soon" state
- Friendly error UI when the data source is unavailable
- HTML test reporting in CI

Out of scope:

- Verifying exact AI-generated recommendation text
- Financial accuracy of investment recommendations
- Production secrets or private user data
- Full visual regression testing
- Load and performance testing

## Risk-Based Testing

The highest-risk area is the AI recommendation workflow because it combines user input, backend API behavior, AI-generated output, and frontend rendering.

Priority coverage focuses on:

- Service availability (front-end + Supabase API)
- Stable API contract
- Required recommendation fields
- Top 10 recommendation count when the product contract defines it
- Graceful handling of missing/invalid authentication
- User-visible error states and login gating

## Quality Gate

A build is considered regression-ready when:

- All API smoke tests pass
- AI recommendation schema checks pass
- Web smoke tests pass in Chromium
- `reports/report.html` is generated
- No sensitive secrets are committed to the repository

