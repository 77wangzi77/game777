const HANDLED = new Set([
  "invoice.paid",
  "invoice.payment_failed",
  "charge.refunded",
  "credit_note.created",
  "cash_balance.funds_available",
  "customer_cash_balance_transaction.created",
]);

export function applyStripeEvent(event, ledger) {
  if (ledger.hasEvent(event.id)) {
    return { duplicate: true };
  }

  if (!HANDLED.has(event.type)) {
    ledger.record(event, { disposition: "ignored" });
    return { duplicate: false, disposition: "ignored" };
  }

  if (event.type === "invoice.paid" || event.type === "invoice.payment_failed") {
    const invoice = event.data.object;
    ledger.updateInvoice(invoice.id, {
      status: event.type === "invoice.paid" ? "paid" : "payment_failed",
      amountDue: invoice.amount_due,
      amountPaid: invoice.amount_paid,
      currency: invoice.currency,
      projectCode: invoice.metadata?.project_code || null,
      serviceLine: invoice.metadata?.service_line || null,
      lastEvent: event.type,
    });
  }

  if (event.type === "charge.refunded") {
    const charge = event.data.object;
    const invoiceId = charge.invoice || charge.metadata?.invoice_id || null;
    if (invoiceId) {
      ledger.updateInvoice(invoiceId, {
        refunded: true,
        amountRefunded: charge.amount_refunded,
        lastEvent: event.type,
      });
    }
  }

  if (event.type === "credit_note.created") {
    const note = event.data.object;
    ledger.updateInvoice(note.invoice, {
      creditNoteId: note.id,
      creditNoteAmount: note.amount,
      lastEvent: event.type,
    });
  }

  if (
    event.type === "cash_balance.funds_available" ||
    event.type === "customer_cash_balance_transaction.created"
  ) {
    const object = event.data.object;
    ledger.recordCashBalance(event.id, {
      type: event.type,
      customer: object.customer || null,
      amount: object.amount ?? object.net_amount ?? null,
      currency: object.currency || null,
      needsManualReconciliation: true,
    });
  }

  ledger.record(event, { disposition: "applied" });
  return { duplicate: false, disposition: "applied" };
}
