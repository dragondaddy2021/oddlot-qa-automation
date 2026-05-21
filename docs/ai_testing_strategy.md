# AI Testing Strategy

## Principle

AI output should not be tested as a fixed answer. Recommendation text may vary between model versions, prompts, market conditions, and cache states.

The automation suite validates deterministic quality signals around the AI system instead.

## What We Validate

- Response status code
- JSON schema shape (`date`, `stocks[]`)
- Recommendation list exists
- Required fields are present
- `symbol`, `name`, and `reason` are non-empty strings
- Numeric fields (`price`, `yield_rate`, `pe_ratio`) are sane
- Top 10 result count when that is the product contract
- Requests without an API key return `401`
- UI renders recommendation cards, gates favorites behind login, and shows a friendly error state when the data source is unavailable

## What We Do Not Validate

- Exact recommendation order unless explicitly defined
- Exact AI explanation wording
- Specific stock picks
- Model-specific phrasing
- Financial correctness of AI advice

## Cache Behavior

If the product uses caching, tests should validate behavior that users and systems depend on:

- Repeated equivalent requests return a valid schema
- Cached responses remain compatible with the public contract
- Cache misses do not break response shape
- Cache failures fall back to a friendly error message

Cache tests should avoid assuming identical AI text unless the API contract explicitly guarantees it.

## Error Handling

AI services can fail because of upstream model errors, timeout, quota limits, invalid input, or network issues.

The suite validates that those failures are converted into predictable API responses and user-friendly UI messages.

