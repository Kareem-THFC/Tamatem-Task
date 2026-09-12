# Tamatem Commerce Assignment

Browse a catalogue of game items imported from CSV, sign in, buy an item with
gems, and read the receipt.

| Part | Stack | Detail |
| --- | --- | --- |
| [`backend/`](backend/) | Python 3.12, Flask, SQLAlchemy, JWT, pytest | [backend/README.md](backend/README.md) |
| [`frontend/`](frontend/) | React 19, TypeScript, Vite, Tailwind | [frontend/README.md](frontend/README.md) |

Requires Python 3.12 and Node 20.19+. No database to install — SQLite is a
file. Commands are PowerShell.

## Setup

```powershell
# 1. Dependencies
uv venv .venv --python 3.12          # or: python -m venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install --python .\.venv\Scripts\python.exe -r backend\requirements.txt

# 2. Secrets — replace the two placeholder values in the copy
Copy-Item backend\.env.example backend\.env

# 3. Database, catalogue, demo account
Set-Location backend
flask --app run db upgrade
flask --app run import-products ..\items.csv
flask --app run seed-demo-user
Set-Location ..

# 4. Frontend
Set-Location frontend
npm install
Copy-Item .env.example .env.local
Set-Location ..
```

## Running

Two terminals — the API first.

```powershell
.\.venv\Scripts\Activate.ps1; Set-Location backend; python run.py   # :5000
Set-Location frontend; npm run dev                                  # :3000
```

Open <http://localhost:3000> and sign in as **`demo` / `demo-password`**
(500 gems). Re-run `seed-demo-user` to top the wallet back up, or register a
new account.

Vite is pinned to port 3000 because the API's CORS allowlist defaults to it.

## API

Interactive documentation, with a working **Try it out**, at
<http://127.0.0.1:5000/api/docs> — Swagger UI over
[`openapi.json`](backend/app/static/openapi.json), which is also what you would
hand to Postman or a client generator.

| Method | Endpoint | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register` | — | Create an account and sign in |
| `POST` | `/api/auth/login` | — | Sign in, returning a JWT |
| `GET` | `/api/products` | optional | Paginated, filterable catalogue |
| `GET` | `/api/products/<id>` | optional | One product |
| `POST` | `/api/orders` | JWT | Buy one product |
| `GET` | `/api/orders` | JWT | The caller's own orders |
| `GET` | `/api/orders/<id>` | JWT | One receipt |

## Tests

```powershell
Set-Location backend; pytest
```

178 tests over the routes, services, models, CSV importer, error envelope, CORS
and the OpenAPI spec, against a throwaway in-memory database. The frontend has
no automated tests — a known gap; it was verified by hand against the API.

## Design decisions

**Money is never a float.** `Numeric(10, 2)` in the database, `Decimal` in the
service layer, strings (`"150.00"`) on the wire — JSON numbers would invite the
client to parse them back into floats.

**The client is a convenience; the server is the guard.** Every rule the UI
appears to enforce is enforced again by the API. A disabled buy button still
meets `409 INSUFFICIENT_GEM_BALANCE` if the client is wrong.

**A purchase request carries only a product id.** The price is read from the
database, so nothing in the request can change what an item costs.

**Concurrency correctness lives in the database.** A unique constraint rules
out a duplicate order and a check constraint a negative balance; the debit and
the insert share one transaction.

## Assumptions

- **Gems, not currency.** CSV prices carry no unit, so they are an in-app
  balance (500 to start) that a purchase debits. It makes the purchase flow
  able to succeed *and* be refused without inventing a payment integration.
- **An account may own a product once**; a repeat purchase is refused rather
  than charged. Ownership is per account.
- **Browsing is public, buying is not.** The product endpoints read a token
  *optionally* — so the store works signed-out, and a signed-in caller gets an
  `owned` flag in the same request — while every state-changing endpoint
  requires one.
- **Registration is included** though only login was required, so a reviewer
  can reach a fresh account without touching the database.
- **The token is in `localStorage`**, not an `httpOnly` cookie. Confined to one
  file; the trade-off is in the frontend README.
