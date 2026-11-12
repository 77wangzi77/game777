import { assertTaxCode, templateIdFor } from "./catalog.js";
import { requireAddress, requireAmount, requireString } from "./validate.js";
import { taxReadiness } from "./tax.js";

export async function createCustomer(stripe, body) {
  const name = requireString(body, "name");
  const email = requireString(body, "email");
  const address = requireAddress(body.address);
  const idempotencyKey = requireString(body, "idempotencyKey");
  const customer = await stripe.customers.create(
    {
      name,
      email,
      address,
      metadata: {
        business: "intelligent-reality",
      },
    },
    { idempotencyKey },
  );

  if (body.taxId) {
    const type = requireString(body.taxId, "type");
    const value = requireString(body.taxId, "value");
    await stripe.customers.createTaxId(
      customer.id,
      { type, value },
      { idempotencyKey: `${idempotencyKey}:tax-id` },
    );
  }

  return {
    id: customer.id,
    email: customer.email,
    name: customer.name,
  };
}

export async function createMilestoneInvoice(stripe, body, env = process.env) {
  const customerId = requireString(body, "customerId");
  const serviceLine = requireString(body, "serviceLine");
  const taxCode = requireString(body, "taxCode");
  const projectCode = requireString(body, "projectCode");
  const milestone = requireString(body, "milestone");
  const description = requireString(body, "description");
  const idempotencyKey = requireString(body, "idempotencyKey");
  const amount = requireAmount(body.amount);
  const currency = (body.currency || "usd").toLowerCase();
  const daysUntilDue = body.daysUntilDue ?? 30;
  if (!Number.isInteger(daysUntilDue) || daysUntilDue < 1) {
    const error = new Error("daysUntilDue must be a positive integer");
    error.statusCode = 400;
    throw error;
  }
  assertTaxCode(serviceLine, taxCode);

  const customer = await stripe.customers.retrieve(customerId);
  if (!customer.address?.country) {
    const error = new Error(
      "Customer needs a billing address before an invoice can be taxed. Create the customer with an address.",
    );
    error.statusCode = 400;
    throw error;
  }

  const readiness = await taxReadiness(stripe);
  const product = await findOrCreateProduct(stripe, {
    serviceLine,
    taxCode,
    idempotencyKey,
  });
  const template = templateIdFor(serviceLine, env);
  const metadata = {
    service_line: serviceLine,
    project_code: projectCode,
    milestone,
    tax_code: taxCode,
  };

  const invoice = await stripe.invoices.create(
    {
      customer: customerId,
      collection_method: "send_invoice",
      days_until_due: daysUntilDue,
      auto_advance: true,
      description,
      metadata,
      ...(readiness.canCollect ? { automatic_tax: { enabled: true } } : {}),
      ...(template ? { rendering: { template } } : {}),
    },
    { idempotencyKey },
  );

  await stripe.invoiceItems.create(
    {
      customer: customerId,
      invoice: invoice.id,
      description,
      quantity: 1,
      price_data: {
        currency,
        product: product.id,
        unit_amount: amount,
        tax_behavior: "exclusive",
      },
      metadata,
    },
    { idempotencyKey: `${idempotencyKey}:item` },
  );

  const sent = await stripe.invoices.sendInvoice(
    invoice.id,
    {},
    { idempotencyKey: `${idempotencyKey}:send` },
  );

  return {
    id: sent.id,
    number: sent.number,
    status: sent.status,
    hostedInvoiceUrl: sent.hosted_invoice_url,
    customerId,
    serviceLine,
    projectCode,
    milestone,
    currency: sent.currency,
    amountDue: sent.amount_due,
    tax: sent.tax,
    automaticTax: Boolean(sent.automatic_tax?.enabled),
    renderingTemplate: template,
    taxCollection: readiness.canCollect
      ? { collecting: true }
      : { collecting: false, reason: readiness.blockedReason },
  };
}

async function findOrCreateProduct(stripe, { serviceLine, taxCode, idempotencyKey }) {
  const existing = await stripe.products.list({ limit: 100, active: true });
  const match = existing.data.find(
    (product) =>
      product.metadata?.service_line === serviceLine &&
      product.metadata?.tax_code === taxCode,
  );
  if (match) return match;

  return stripe.products.create(
    {
      name: `Intelligent Reality — ${serviceLine.replaceAll("_", " ")}`,
      tax_code: taxCode,
      metadata: {
        service_line: serviceLine,
        tax_code: taxCode,
        business: "intelligent-reality",
      },
    },
    { idempotencyKey: `${idempotencyKey}:product:${serviceLine}:${taxCode}` },
  );
}
