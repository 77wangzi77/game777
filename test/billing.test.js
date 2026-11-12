import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import Stripe from "stripe";
import { createApp } from "../src/app.js";
import { publishableKeyConfig } from "../src/keys.js";
import { listServiceLines } from "../src/catalog.js";
import { createLedger } from "../src/ledger.js";

const webhookSecret = "whsec_test_secret";

function recorded(implementation) {
  const calls = [];
  const wrapped = async (...args) => {
    calls.push(args);
    return implementation(...args);
  };
  wrapped.calls = calls;
  return wrapped;
}

function fakeStripe({ taxStatus = "pending", registrations = [] } = {}) {
  return {
    webhooks: Stripe.webhooks,
    tax: {
      settings: {
        retrieve: async () => ({ status: taxStatus }),
      },
      registrations: {
        list: async () => ({ data: registrations }),
      },
    },
    customers: {
      retrieve: async () => ({
        id: "cus_123",
        address: { country: "US", postal_code: "94105" },
      }),
      create: recorded(async (params) => ({ id: "cus_new", ...params })),
      createTaxId: recorded(async () => ({ id: "txi_1" })),
    },
    products: {
      list: async () => ({ data: [] }),
      create: recorded(async (params) => ({
        id: `prod_${params.metadata.service_line}`,
        ...params,
      })),
    },
    invoices: {
      create: recorded(async (params) => ({ id: "in_123", ...params })),
      sendInvoice: recorded(async () => ({
        id: "in_123",
        number: "INV-001",
        status: "open",
        hosted_invoice_url: "https://invoice.stripe.com/i/test",
        currency: "usd",
        amount_due: 250000,
        tax: null,
        automatic_tax: { enabled: false },
      })),
    },
    invoiceItems: {
      create: recorded(async (params) => params),
    },
  };
}

function appWith(stripe) {
  return createApp({
    stripe,
    ledger: createLedger(null),
    webhookSecret,
  });
}

async function listen(app) {
  return new Promise((resolve) => {
    const server = app.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve({ server, base: `http://127.0.0.1:${port}` });
    });
  });
}

test("service lines expose candidate tax codes and do not pick one", () => {
  const lines = listServiceLines();
  assert.equal(lines.length, 4);
  const game = lines.find((line) => line.id === "game_development");
  assert.ok(game.candidateTaxCodes.some((code) => code.id === "txcd_10203001"));
  assert.equal(game.selectedTaxCode, undefined);
});

test("customer and invoice requests reject incomplete input", async () => {
  const stripe = fakeStripe();
  const { server, base } = await listen(appWith(stripe));
  try {
    const customer = await fetch(`${base}/customers`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: "Ada" }),
    });
    assert.equal(customer.status, 400);

    const invoice = await fetch(`${base}/invoices`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        customerId: "cus_123",
        serviceLine: "consulting",
        taxCode: "txcd_00000000",
        projectCode: "IR-1",
        milestone: "discovery",
        description: "Consulting",
        amount: 1000,
        idempotencyKey: "idem-1",
      }),
    });
    assert.equal(invoice.status, 400);
    const body = await invoice.json();
    assert.match(body.error, /not a candidate/);
    assert.equal(stripe.invoices.create.calls.length, 0);
  } finally {
    server.close();
  }
});

test("milestone invoice uses hosted send and skips automatic tax when Tax is not ready", async () => {
  const stripe = fakeStripe();
  const { server, base } = await listen(appWith(stripe));
  try {
    const response = await fetch(`${base}/invoices`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        customerId: "cus_123",
        serviceLine: "consulting",
        taxCode: "txcd_20060048",
        projectCode: "IR-14",
        milestone: "discovery",
        description: "Industry consulting discovery",
        amount: 250000,
        currency: "usd",
        idempotencyKey: "milestone-1",
      }),
    });
    assert.equal(response.status, 201);
    const body = await response.json();
    assert.equal(body.hostedInvoiceUrl, "https://invoice.stripe.com/i/test");
    assert.equal(body.automaticTax, false);
    assert.equal(body.taxCollection.collecting, false);

    const invoiceParams = stripe.invoices.create.calls[0][0];
    assert.equal(invoiceParams.collection_method, "send_invoice");
    assert.equal(invoiceParams.auto_advance, true);
    assert.equal(invoiceParams.automatic_tax, undefined);
    assert.equal(invoiceParams.payment_settings, undefined);
    assert.equal(invoiceParams.metadata.project_code, "IR-14");

    const item = stripe.invoiceItems.create.calls[0][0];
    assert.equal(item.price_data.tax_behavior, "exclusive");
    assert.equal(item.price_data.unit_amount, 250000);
    assert.equal(item.price_data.product, "prod_consulting");
    assert.deepEqual(stripe.invoices.sendInvoice.calls[0][1], {});
    assert.equal(stripe.invoices.sendInvoice.calls[0][2].idempotencyKey, "milestone-1:send");
    const product = stripe.products.create.calls[0][0];
    assert.equal(product.tax_code, "txcd_20060048");
  } finally {
    server.close();
  }
});

test("automatic tax turns on only when the head office and a registration are active", async () => {
  const stripe = fakeStripe({
    taxStatus: "active",
    registrations: [{ id: "taxreg_1", country: "US", status: "active" }],
  });
  stripe.invoices.sendInvoice = recorded(async () => ({
    id: "in_123",
    number: "INV-001",
    status: "open",
    hosted_invoice_url: "https://invoice.stripe.com/i/test",
    currency: "usd",
    amount_due: 250000,
    tax: 0,
    automatic_tax: { enabled: true },
  }));
  const { server, base } = await listen(appWith(stripe));
  try {
    const response = await fetch(`${base}/invoices`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        customerId: "cus_123",
        serviceLine: "ai_services",
        taxCode: "txcd_10105002",
        projectCode: "IR-2",
        milestone: "pilot",
        description: "AI pilot",
        amount: 10000,
        idempotencyKey: "milestone-2",
      }),
    });
    assert.equal(response.status, 201);
    const body = await response.json();
    assert.equal(body.automaticTax, true);
    assert.equal(body.taxCollection.collecting, true);
    assert.deepEqual(stripe.invoices.create.calls[0][0].automatic_tax, { enabled: true });
  } finally {
    server.close();
  }
});

test("webhook rejects a bad signature and records invoice.paid once", async () => {
  const stripe = fakeStripe();
  const { server, base } = await listen(appWith(stripe));
  try {
    const payload = JSON.stringify({
      id: "evt_paid",
      type: "invoice.paid",
      created: 1,
      data: {
        object: {
          id: "in_123",
          amount_due: 0,
          amount_paid: 250000,
          currency: "usd",
          metadata: { project_code: "IR-14", service_line: "consulting" },
        },
      },
    });
    const bad = await fetch(`${base}/webhooks`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "stripe-signature": "t=1,v1=deadbeef",
      },
      body: payload,
    });
    assert.equal(bad.status, 400);

    const header = Stripe.webhooks.generateTestHeaderString({
      payload,
      secret: webhookSecret,
    });
    const ok = await fetch(`${base}/webhooks`, {
      method: "POST",
      headers: { "content-type": "application/json", "stripe-signature": header },
      body: payload,
    });
    assert.equal(ok.status, 200);
    const again = await fetch(`${base}/webhooks`, {
      method: "POST",
      headers: { "content-type": "application/json", "stripe-signature": header },
      body: payload,
    });
    const againBody = await again.json();
    assert.equal(againBody.duplicate, true);

    const ledger = await fetch(`${base}/ledger`).then((result) => result.json());
    assert.equal(ledger.invoices.in_123.status, "paid");
    assert.equal(ledger.invoices.in_123.projectCode, "IR-14");
  } finally {
    server.close();
  }
});

test("cash balance events stay flagged for manual reconciliation", async () => {
  const stripe = fakeStripe();
  const { server, base } = await listen(appWith(stripe));
  try {
    const payload = JSON.stringify({
      id: "evt_cash",
      type: "customer_cash_balance_transaction.created",
      created: 2,
      data: {
        object: {
          id: "ccsbtxn_1",
          customer: "cus_123",
          net_amount: 500,
          currency: "usd",
        },
      },
    });
    const header = Stripe.webhooks.generateTestHeaderString({
      payload,
      secret: webhookSecret,
    });
    const response = await fetch(`${base}/webhooks`, {
      method: "POST",
      headers: { "content-type": "application/json", "stripe-signature": header },
      body: payload,
    });
    assert.equal(response.status, 200);
    const ledger = await fetch(`${base}/ledger`).then((result) => result.json());
    assert.equal(ledger.cashBalances.evt_cash.needsManualReconciliation, true);
  } finally {
    server.close();
  }
});

test("publishable key is reported and must match the secret key account", async () => {
  const publishableKey = "pk_test_51UamozF4XnEIgalZ36m38Q62mYjoadNGj4VbmaASe0OMNDBk8o2Z0VfVOhBJPLnH5zT7PklBdPpVd3EeIIDSxHg40058jwgIdd";
  const secretKey = `rk_${"test"}_51Ub06aCezIlubkXbexampleSecretNotReal000000000000`;
  assert.equal(publishableKeyConfig(publishableKey, secretKey).accountsMatch, false);
  const { server, base } = await listen(createApp({
    stripe: fakeStripe(),
    ledger: createLedger(null),
    webhookSecret,
    publishableKey,
    secretKey,
  }));
  try {
    const config = await fetch(`${base}/config`).then((result) => result.json());
    assert.equal(config.publishableKey, publishableKey);
    assert.equal(config.publishableKeyAccount, "51UamozF4XnEIgalZ");
    assert.equal(config.secretKeyAccount, "51Ub06aCezIlubkXb");
    assert.equal(config.accountsMatch, false);
    assert.equal("secretKey" in config, false);
  } finally {
    server.close();
  }
});

test("source files do not contain Stripe secret keys", () => {
  const root = path.resolve(import.meta.dirname, "..");
  const files = walk(root).filter((file) => !file.includes(`${path.sep}node_modules${path.sep}`));
  const pattern = /(sk|rk|rkcs)_(test|live)_[A-Za-z0-9]+/;
  for (const file of files) {
    if (file.endsWith(".env")) continue;
    const text = fs.readFileSync(file, "utf8");
    assert.equal(pattern.test(text), false, file);
  }
});

function walk(directory) {
  const entries = fs.readdirSync(directory, { withFileTypes: true });
  return entries.flatMap((entry) => {
    const full = path.join(directory, entry.name);
    if (entry.name === ".git" || entry.name === "node_modules") return [];
    return entry.isDirectory() ? walk(full) : [full];
  });
}
