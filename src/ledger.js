import fs from "node:fs";
import path from "node:path";

export function createLedger(filePath) {
  const state = filePath && fs.existsSync(filePath)
    ? JSON.parse(fs.readFileSync(filePath, "utf8"))
    : { events: {}, invoices: {}, cashBalances: {} };

  function persist() {
    if (!filePath) return;
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    const temporary = `${filePath}.tmp`;
    fs.writeFileSync(temporary, JSON.stringify(state, null, 2));
    fs.renameSync(temporary, filePath);
  }

  return {
    snapshot() {
      return structuredClone(state);
    },
    hasEvent(eventId) {
      return Boolean(state.events[eventId]);
    },
    record(event, patch) {
      state.events[event.id] = {
        type: event.type,
        created: event.created,
        ...patch,
      };
      persist();
    },
    updateInvoice(invoiceId, patch) {
      state.invoices[invoiceId] = {
        ...(state.invoices[invoiceId] || {}),
        ...patch,
      };
      persist();
    },
    recordCashBalance(key, patch) {
      state.cashBalances[key] = {
        ...(state.cashBalances[key] || {}),
        ...patch,
      };
      persist();
    },
  };
}
