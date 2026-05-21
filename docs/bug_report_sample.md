# Bug Report Sample

## Title

AI recommendation API returns stocks without required `reason` field

## Severity

High

## Environment

- Application: OddLot (龍爹地的零股投資學習平台)
- Front-end: `https://dragondaddy2021.github.io/oddlot/`
- API base URL: `https://mmcoqujhhrltdaozfkwj.supabase.co`
- Endpoint: `GET /rest/v1/ai_recommendations?select=*&order=date.desc&limit=1`
- Browser: Chromium
- Test suite: Pytest API regression

## Steps to Reproduce

1. Send the latest-recommendation request with the publishable apikey header:

```bash
curl "https://mmcoqujhhrltdaozfkwj.supabase.co/rest/v1/ai_recommendations?select=*&order=date.desc&limit=1" \
  -H "apikey: <publishable_key>" -H "Authorization: Bearer <publishable_key>"
```

2. Inspect each item in the `stocks` array of the response body.

## Actual Result

At least one recommendation item does not include the `reason` field.

```json
{
  "symbol": "2330",
  "name": "TSMC"
}
```

## Expected Result

Every recommendation item should include non-empty `symbol`, `name`, and `reason` fields.

```json
{
  "symbol": "2330",
  "name": "TSMC",
  "reason": "Strong long-term fundamentals and stable demand outlook."
}
```

## Impact

Users cannot understand why a stock was recommended. This reduces trust in the AI recommendation feature and may break frontend rendering if the UI expects `reason`.

## Suggested Fix

Update the recommendation response mapper or prompt post-processing layer to enforce the required schema before returning the API response.

