# Frontend

React SPA for the commerce assignment: browse, sign in, buy with gems, read the
receipt. Setup and how to run it are in [`../README.md`](../README.md); this
file is the reasoning behind it.

Requires Node 20.19+, and a running API -- the frontend is a client and has
nothing to show without one.

## Stack

React 19 + TypeScript on Vite, React Router 7, Tailwind 4. Data fetching is
`fetch` through one wrapper ([`src/api/client.ts`](src/api/client.ts)) and a
hook per resource -- no data-fetching library. Zod validates forms *and*
generates the request types via `z.infer`, so there is no hand-written
duplicate. React Context holds the signed-in user and nothing else; everything
else is owned by the page showing it, and a state library would be more
machinery than this app has state.

The only runtime dependencies are `react`, `react-dom`, `react-router-dom`,
`zod` and `react-hot-toast`: no component library, no icon package, no
animation library, no form library, no images.

## Routes

| Path | Auth | Page |
| --- | --- | --- |
| `/login`, `/register` | guests only | Sign in / create an account |
| `/products` | public | Paginated, filterable catalogue |
| `/products/:id` | public | Details and the purchase action |
| `/orders`, `/orders/:id` | required | History and one receipt |

`RequireAuth` is a convenience, not security -- the API rejects an unauthorised
order regardless. It only spares the user a page that could not work, and
remembers where they were headed so they land there after signing in.

## Structure

```text
src/
├── api/          # one typed function per endpoint, all on client.ts
├── components/   # ui primitives, layout, brand, auth, products, orders
├── context/      # AuthProvider, the one piece of global state
├── hooks/        # one per resource: useProducts, useProduct, useOrders, useOrder
├── lib/          # cn, format, storage, toast, validate-form
├── pages/        # one component per route
├── schemas/      # Zod request schemas, mirroring backend/app/schemas/
└── types/api.ts  # TypeScript mirrors of the API's JSON
```

## Scripts and environment

```powershell
npm run dev       # dev server with HMR, port 3000
npm run build     # tsc -b, then build to dist/
npm run preview   # serve the production build
npm run lint      # oxlint
```

One variable, in `.env.local`: `VITE_API_BASE_URL`, defaulting to
`http://127.0.0.1:5000`. Only `VITE_`-prefixed variables reach client code --
a guard, not a secret store, since everything here is readable in the bundle.

## Decisions worth explaining

**Money is never a number.** Prices arrive as decimal strings and stay that
way -- parsing them into JS floats would reintroduce exactly the rounding the
backend avoids. They are formatted in `lib/format.ts` and never used in
arithmetic; the one exception, disabling a button the user cannot afford, is a
hint only, and the server still answers `409` if the hint is wrong.

**Validation is one schema, not two implementations.** Each Zod schema in
`src/schemas/` validates, normalises (trimming, lower-casing) as part of
parsing, and is the source of the request type -- so adding a field changes the
API signature too and the two cannot drift. Forms use `safeParse`: invalid
input is an expected branch, not an exception. One subtlety: `z.email().trim()`
checks format *before* trimming, so the email field normalises in a string
schema and pipes into `z.email()`. Passwords are never trimmed.

**Toasts are for events; inline messages are for state.** A failed sign-in or
purchase is feedback on a click, so it is a toast. Field errors belong under
their input, and the "sign in to buy" notice has to persist or the buy panel
reads as unexplained. Toasts are raised from handlers, never during render --
calling `toast()` while rendering fires again on every re-render, and twice on
mount under `StrictMode`.

**An owned item is never offered for sale again.** The product endpoints return
an `owned` boolean, so the grid badges owned items and the detail page swaps the
buy panel for a link to the receipt. Still a convenience: the API refuses a
repeat with `409 PRODUCT_ALREADY_OWNED`, and the page refetches so a stale flag
corrects itself rather than offering a purchase that cannot succeed.

**Pagination and filters live in the URL**, so a view is shareable and the back
button steps through filters. One helper merges a change into the query string
and applies the two rules every caller would forget: an empty value removes its
parameter, and changing a filter returns to page one. The search box is the
exception -- writing on every keystroke would leave a history entry per letter,
so it debounces 300ms and pushes with `replace: true`.

**Every request can be cancelled.** Each hook creates an `AbortController` and
returns `controller.abort` as its cleanup, so changing page or navigating away
cannot let a stale response overwrite a newer one. That is why there is a hook
per resource rather than one generic helper: each owns the exact dependency
list that should re-trigger and therefore cancel it.

**The token is in `localStorage`.** It survives a reload and is readable by any
script on the origin, which is why an `httpOnly` cookie is the production
answer. It is confined to `lib/storage.ts`, so swapping it touches one file.

## Departures from the mockup

The canvas is a visual concept, so parts of it describe commerce features this
API does not have. Those were dropped rather than faked -- nothing on screen is
invented data. Cut: the quantity stepper (one order is one item), rarity tiers,
stock counts, SKU and delivery tiles, collector XP, receipt tax and discount
rows, and city regions (the CSV carries country codes, so the chips read Jordan
and Saudi Arabia). Prices are gems, not JD, matching the backend.

Everything else is implemented: the split-screen login, the listing with its
hero band, region chips, numbered pagination and all three states, the detail
page, and the achievement-style receipt.

## Known gaps

- The canvas draws no registration screen, so that page extends the same shell.
- No automated frontend tests -- the suite for this assignment is in the
  backend, and the UI was verified by hand against the running API.
