# Intelligent Reality billing

Stripe integration for [Intelligent Reality](https://IntelligentReality.com): custom game development, enterprise industrial design, industry consulting, and AI services.

Customers are businesses. Each bill is a one-time project milestone, paid on a Stripe-hosted invoice. There is no existing payments integration in this repository to review.

## Plan

`stripe_implementation_planner` (`iguide_61VkORuHkQaaroG0F41CezIlubkXb`) selected:

| Decision | Choice |
| --- | --- |
| Processor | Stripe only, in a web browser |
| Managed Payments | No. The business sells services, not digital goods only |
| Payments | Hosted Invoice Page. Cards, bank transfer, and 3D Secure stay on Stripe’s page |
| Invoice creation | Invoicing API when a milestone is reached, with an idempotency key |
| Presentation | One Dashboard invoice rendering template per service line, applied with `rendering.template` |
| Collection | No card on file. `collection_method=send_invoice`, `auto_advance=true`, then send |
| Reconciliation | Webhooks into this app. Bank-transfer cash that does not auto-match is flagged for a person |
| Tax | `automatic_tax` only after the head office is active and a registration is already on the account |

Also left on, by omitting `payment_method_types`: dynamic payment methods, so Link and Adaptive Pricing stay configurable in the Dashboard.

Bank transfer for USD and GBP is turned on under Dashboard → Settings → Billing → Invoices → Default payment methods. That avoids passing `payment_method_types` on each invoice. ACH that does not match an invoice stays in the customer cash balance until someone applies it. `invoice.paid` does not mean the cash has settled.

## Sandbox

This integration was built against a claimable sandbox, not live mode.

- Account: `acct_1Ub06aCezIlubkXb`
- Expires: 19 November 2026 (Asia/Shanghai calendar date follows the sandbox `expires_at` of 2026-11-19)
- Claim: `https://dashboard.stripe.com/onboard_sandbox/YWNjdF8xVWIwNmFDZXpJbHVia1hiLDE3OTUxMDQyNTYv100bqqELZOb` or `stripe sandboxes claim`

The sandbox API key is a claimable key (`rkcs_test_…`). It is not in git. Put it in `.env` as `STRIPE_SECRET_KEY`. After you claim the sandbox, replace it with a restricted key that can read Tax settings, write invoices, and read customers. Do not use a secret key (`sk_`).

The unclaimed key cannot read Tax settings. Until that read succeeds, this service refuses to set `automatic_tax`.

## Run

```bash
cp .env.example .env
npm install
npm test
npm start
```

Create a customer, then an invoice. `taxCode` must be one of the candidates from `GET /service-lines`. Confirm the code with a tax advisor before using it. Codes come from the [Tax Codes API](https://docs.stripe.com/api/tax_codes). Quoted amounts are tax-exclusive (`tax_behavior=exclusive`).

```bash
curl -s localhost:3000/service-lines
curl -s -X POST localhost:3000/customers \
  -H 'content-type: application/json' \
  -d '{"name":"Northwind Studios","email":"ap@northwind.example","idempotencyKey":"cust-1","address":{"country":"US","line1":"1 Market St","city":"San Francisco","state":"CA","postal_code":"94105"}}'
curl -s -X POST localhost:3000/invoices \
  -H 'content-type: application/json' \
  -d '{"customerId":"cus_...","serviceLine":"consulting","taxCode":"txcd_20060048","projectCode":"IR-14","milestone":"discovery","description":"Discovery workshop","amount":250000,"idempotencyKey":"IR-14-discovery"}'
```

`amount` is in the smallest currency unit. The response includes `hostedInvoiceUrl`.

Forward webhooks:

```bash
stripe listen --forward-to localhost:3000/webhooks
```

Put the signing secret in `STRIPE_WEBHOOK_SECRET`. The handler verifies the signature, then records `invoice.paid`, `invoice.payment_failed`, `charge.refunded`, `credit_note.created`, `cash_balance.funds_available`, and `customer_cash_balance_transaction.created`.

## Tax still needs a person

Do not add a tax registration in Stripe until the business is registered with that tax authority. This repo does not guess a head office or a jurisdiction.

1. Dashboard → Tax → Settings: set the real head office. Tax settings stay `pending` until that address exists.
2. Record each existing registration in Dashboard → Tax → Locations, or with the Tax Registrations API.
3. `GET /tax/readiness` returns `canCollect: true` only after both are in place. The next milestone invoice then sets `automatic_tax.enabled=true`.
4. Sandbox registrations do not carry into live mode. Add live registrations before the first real charge. Threshold monitoring ignores sandbox payments.

A missing registration does not raise an error. Stripe would collect zero tax. That is why automatic tax stays off until readiness passes.

Invoice rendering templates are created in the Dashboard (the API cannot create them). One template per service line, then set `INVOICE_TEMPLATE_GAME_DEVELOPMENT`, `INVOICE_TEMPLATE_INDUSTRIAL_DESIGN`, `INVOICE_TEMPLATE_CONSULTING`, and `INVOICE_TEMPLATE_AI_SERVICES`.

## Dashboard checklist

- Branding: logo, color, and footer under Settings → Branding.
- Invoice reminders: Settings → Billing.
- Bank transfer on USD/GBP invoices: Settings → Billing → Invoices.
- Payment methods: leave dynamic payment methods on so Link can appear. Do not hardcode a method list in code.
- Webhook endpoint for the six events above, plus a signing secret in the host’s secrets store.
- Restricted API key for this service only. Rotate the claimable sandbox key after the sandbox is claimed.
