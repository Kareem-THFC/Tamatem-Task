# Backend

Flask API: authentication, the CSV-imported catalogue, and the purchase flow.
Setup, the endpoint list and how to run it are in
[`../README.md`](../README.md); this file is the reasoning behind them.

## Why SQLite

The data is small, relational and read-mostly -- a few hundred products, one
row per purchase, joins and an indexed filter. Among relational engines SQLite
wins on setup cost: it is a file bundled with Python, so a reviewer runs one
migration command instead of installing a server and creating a role. Postgres
or MySQL would be the production answer; neither changes the outcome of a
single-reviewer evaluation.

It costs two things, both handled rather than ignored:

- **No native decimal type.** SQLite stores `Numeric(10, 2)` as a float and
  SQLAlchemy converts back to `Decimal` on read, so money is never *arithmetic*
  on a float, and prices leave the API as strings.
- **One writer at a time.** The purchase path is written as though that were
  not true -- see [Buying](#buying) -- so its correctness rests on constraints,
  not on the engine's write lock.

Nothing is SQLite-specific: switching is a `DATABASE_URL` change and a fresh
`flask --app run db upgrade`.

## Response shape

Success is wrapped in `data`, with a sibling `pagination` on list endpoints:

```json
{
  "data": [{ "id": 1, "title": "Sword", "price": "150.00", "location": "JO" }],
  "pagination": { "page": 1, "page_size": 20, "total": 100, "pages": 5 }
}
```

Errors always take one shape, with `details` only on validation failures:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": [{ "field": "identifier", "message": "Field required" }]
  }
}
```

Both are built by helpers in [`app/utils/responses.py`](app/utils/responses.py),
so routes never call `jsonify` and the contract is defined once. Errors are
raised in routes but rendered in one place,
[`app/errors/handlers.py`](app/errors/handlers.py):

| Cause | Status | Code |
| --- | --- | --- |
| `ApiError` raised in a route | chosen | chosen |
| Pydantic `ValidationError` | `422` | `VALIDATION_ERROR` |
| Non-JSON / malformed body | `415` / `400` | `UNSUPPORTED_MEDIA_TYPE` / `BAD_REQUEST` |
| Unknown route or method | `404` / `405` | `NOT_FOUND` / `METHOD_NOT_ALLOWED` |
| Missing or bad JWT | `401` | `AUTHENTICATION_REQUIRED` / `INVALID_TOKEN` / `TOKEN_EXPIRED` |
| Anything unhandled | `500` | `INTERNAL_SERVER_ERROR` |

Because validation is handled application-wide, routes call
`Schema.model_validate(...)` directly instead of repeating a try/except. The
500 handler logs the real exception and returns a generic message, so stack
traces never reach a client -- except under test and debug, where it re-raises.

## Auth

`register` takes `username`, `email`, `password`; `login` takes `identifier`
(username *or* email) and `password`. Both return an access token and the user,
so signing up needs no second request. Rules live in
[`app/schemas/auth.py`](app/schemas/auth.py):

- A username is 3-80 chars of letters, digits, `.`, `_`, `-`. No `@`, because
  it doubles as a login identifier and would be ambiguous with an email.
- Emails are validated by pydantic's `EmailStr` and stored lower-cased.
  Usernames are stored as typed but compared case-insensitively through a
  unique index on `lower(username)`, so `Buyer` and `buyer` are one account.
- Passwords are 8-128 chars and never whitespace-stripped.
- A `422` lists every failing field at once, so a form shows all its errors
  from one request.

Registration's `409` names the clashing field, because a signup form has to say
what to change -- which does reveal that an address has an account. Login stays
deliberately silent by comparison: bad credentials are `401` either way.

Duplicates are looked up before the insert so the message can name the field,
and `IntegrityError` is caught as a second line of defence: two simultaneous
signups can both pass that lookup, and catching it turns the race into the same
`409` rather than a `500`.

## Products

Browsing is public. Both endpoints read a token *optionally* and add an `owned`
boolean, so the response has one shape whether or not the caller is signed in;
an *invalid* token is still rejected rather than downgraded to anonymous. The
ownership lookup is one query per page, not one per product.

Beyond `page` and `page_size`, `GET /api/products` takes three filters, all
validated by `ProductListQuery` and narrowing together:

| Parameter | Effect |
| --- | --- |
| `location` | Exact match on the upper-cased country code, e.g. `JO` |
| `search` | Case-insensitive substring of title **or** description |
| `sort` | `default` (id), `price_asc`, `price_desc` |

Sending `location` or `search` empty means "no filter", so a cleared dropdown
lists everything instead of matching nothing. `sort` is an `Enum`, so an
unknown value is a `422` naming the options rather than being ignored.

**Search escapes LIKE wildcards** -- an unescaped `%` typed into the box would
otherwise match every product. **Every ordering breaks ties on the primary
key**, because a tied `ORDER BY` lets the database return rows in any order,
which can make a product appear on two pages or on none.

### Pagination

Both list endpoints share one `PaginationQuery`
([`app/schemas/pagination.py`](app/schemas/pagination.py)), so they cannot
drift:

| Parameter | Default | Accepted | Otherwise |
| --- | --- | --- | --- |
| `page` | `1` | integer >= 1 | `422` |
| `page_size` | `20` | 1-100 | `422` |

The cap is rejected rather than clamped: silently returning 100 rows to a
caller that asked for a million would make a client paginating on its own
arithmetic skip most of the catalogue without ever seeing an error. A page
*past* the end is not an error -- it returns an empty `data` with the real
`total`, so a client on a stale page corrects itself instead of having to read
a 404 as both "no such page" and "no such route".

## Buying

`POST /api/orders` takes only `{"product_id": 1}`. The backend loads the
product, charges its stored price, and returns the receipt with the product
nested so a receipt page renders from one request. `gem_balance_after` is
stored on the order -- later purchases move the live balance, and a receipt
must keep describing its own moment -- while `gem_balance_before` is derived
from it, so the two cannot disagree.

| Situation | Status | Code |
| --- | --- | --- |
| Purchased | `201` | -- |
| Balance too low | `409` | `INSUFFICIENT_GEM_BALANCE` |
| Already owned | `409` | `PRODUCT_ALREADY_OWNED` |
| Unknown product | `404` | `PRODUCT_NOT_FOUND` |
| Bad `product_id` | `422` | `VALIDATION_ERROR` |

`409` rather than `422`: the request is valid, it is the account's state that
prevents it. The message names both figures, so a client can explain the
refusal without another request.

**One purchase per product, per account, enforced twice.** The service checks
before charging, so a repeat costs the buyer nothing; `uq_orders_user_product`
catches the case where two simultaneous requests both pass that check, and the
resulting `IntegrityError` becomes the same `409` after a rollback that also
undoes the debit. The debit and the insert share one commit, so an order cannot
exist without the gems having been spent, and
`ck_users_gem_balance_non_negative` is the backstop against two purchases both
reading the balance before either debit lands.

`GET /api/orders` scopes by user id inside the query rather than checking
afterwards, so another account's history cannot come back by accident.

## Configuration

Read from `backend/.env` by `python-dotenv` and collected in
[`app/config.py`](app/config.py). Only the first two must be set --
`create_app()` refuses to start without them, so a misconfigured environment
fails at startup rather than mid-request.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | -- | Flask's signing key |
| `JWT_SECRET_KEY` | -- | Signs and verifies access tokens |
| `DATABASE_URL` | `sqlite:///commerce.db` | SQLAlchemy connection string |
| `CORS_ORIGINS` | `localhost:3000,127.0.0.1:3000` | Origins allowed to call the API from a browser |
| `ACCESS_TOKEN_HOURS` | `12` | Token lifetime |
| `DEMO_USER_PASSWORD` | `demo-password` | Password set by `seed-demo-user` |

Two separate secrets, because rotating the JWT key invalidates every issued
token and that should not force a session-key rotation with it.

### CORS

Flask-Cors covers `/api/*` only, answers the preflight, and allows the
`Authorization` header -- not permitted by default, so without it every
authenticated request would fail preflight. The allowlist is exact rather than
`"*"`, since browsers reject a wildcard once credentials are involved; moving
the token to a cookie later then needs no revisiting here.
`supports_credentials` is off because the token travels in a header. Error
responses carry the headers too: a `401` the frontend cannot read is a `401` it
cannot display.

## Importing products

```powershell
flask --app run import-products ..\items.csv
```

Rows are upserted on the CSV's own `id`, so re-running refreshes rather than
failing on the primary key. Bad rows are skipped and reported individually on
stderr with their line number and field, so one never aborts the import:

```text
  line 4: price: Input should be a valid decimal
  line 7: id: Duplicate id 201 in this file.
```

A header missing a required column is rejected outright with a non-zero exit
code, since no row in it could be imported. Rules live in
[`app/schemas/product.py`](app/schemas/product.py): positive unique `id`,
non-empty `title` and `description`, non-negative `price` with at most two
decimal places, and `location` trimmed and upper-cased so `?location=` can
compare exactly. A price `Numeric(10, 2)` could not store faithfully is
reported as an invalid row rather than silently rounded.

The importer
([`app/services/product_importer.py`](app/services/product_importer.py)) reads
a text stream rather than a path, which keeps it independent of the CLI and
HTTP layers and lets the tests drive it with an in-memory string.

## Schema

Three tables -- `users`, `products`, `orders` -- built by six linear revisions
in [`migrations/versions/`](migrations/versions/). `orders` stores
`total_price` and `gem_balance_after` rather than reading them live, because a
receipt has to keep describing the moment it was issued.

Five constraints carry rules the application also checks, so neither a bug nor
a race can leave a bad row: `uq_orders_user_product`,
`ck_users_gem_balance_non_negative`, `ck_orders_total_price_non_negative`,
`ck_orders_gem_balance_after_non_negative` and
`ck_products_price_non_negative`, plus the unique index on `lower(username)`.

After a model change: `flask --app run db migrate -m "..."`, read what it
produced, then `db upgrade`. Never edit tables by hand -- a schema that exists
only in one local file cannot be rebuilt by the next clone.

`seed-demo-user` is safe to re-run: it resets the demo user's password and
balance instead of failing on the duplicate username, which is also how to top
the wallet back up.
