import express from "express";
import { listServiceLines } from "./catalog.js";
import { createCustomer, createMilestoneInvoice } from "./invoices.js";
import { createLedger } from "./ledger.js";
import { taxReadiness } from "./tax.js";
import { applyStripeEvent } from "./webhooks.js";

export function createApp({ stripe, ledger, webhookSecret }) {
  const app = express();
  app.disable("x-powered-by");

  app.post(
    "/webhooks",
    express.raw({ type: "application/json" }),
    (request, response) => {
      if (!webhookSecret) {
        response.status(500).json({ error: "STRIPE_WEBHOOK_SECRET is not set" });
        return;
      }
      let event;
      try {
        event = stripe.webhooks.constructEvent(
          request.body,
          request.header("stripe-signature"),
          webhookSecret,
        );
      } catch (error) {
        response.status(400).json({ error: `Webhook signature verification failed: ${error.message}` });
        return;
      }
      const result = applyStripeEvent(event, ledger);
      response.json({ received: true, ...result });
    },
  );

  app.use(express.json({ limit: "32kb" }));

  app.get("/health", (_request, response) => {
    response.json({ ok: true });
  });

  app.get("/service-lines", (_request, response) => {
    response.json({ serviceLines: listServiceLines() });
  });

  app.get("/tax/readiness", async (_request, response, next) => {
    try {
      response.json(await taxReadiness(stripe));
    } catch (error) {
      next(error);
    }
  });

  app.get("/ledger", (_request, response) => {
    response.json(ledger.snapshot());
  });

  app.post("/customers", async (request, response, next) => {
    try {
      response.status(201).json(await createCustomer(stripe, request.body));
    } catch (error) {
      next(error);
    }
  });

  app.post("/invoices", async (request, response, next) => {
    try {
      response.status(201).json(await createMilestoneInvoice(stripe, request.body));
    } catch (error) {
      next(error);
    }
  });

  app.use((error, _request, response, _next) => {
    const status = error.statusCode || error.status || 500;
    response.status(status).json({
      error: status === 500 ? "Stripe request failed" : error.message,
      code: error.code || null,
    });
  });

  return app;
}

export function createRuntime({ stripe, ledgerPath, webhookSecret }) {
  return createApp({
    stripe,
    ledger: createLedger(ledgerPath),
    webhookSecret,
  });
}
