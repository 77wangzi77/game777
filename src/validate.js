const COUNTRIES_NEEDING_FULL_ADDRESS = new Set(["US", "CA", "IN"]);

export function requireString(body, field) {
  const value = body?.[field];
  if (typeof value !== "string" || value.trim() === "") {
    const error = new Error(`${field} is required`);
    error.statusCode = 400;
    throw error;
  }
  return value.trim();
}

export function requireAddress(address) {
  if (!address || typeof address !== "object") {
    const error = new Error("address is required");
    error.statusCode = 400;
    throw error;
  }
  const country = requireString(address, "country").toUpperCase();
  if (!/^[A-Z]{2}$/.test(country)) {
    const error = new Error("address.country must be a two-letter country code");
    error.statusCode = 400;
    throw error;
  }
  const normalized = {
    country,
    line1: optionalString(address.line1),
    line2: optionalString(address.line2),
    city: optionalString(address.city),
    state: optionalString(address.state),
    postal_code: optionalString(address.postal_code),
  };
  if (COUNTRIES_NEEDING_FULL_ADDRESS.has(country)) {
    for (const field of ["line1", "city", "state", "postal_code"]) {
      if (!normalized[field]) {
        const error = new Error(
          `address.${field} is required when address.country is ${country}`,
        );
        error.statusCode = 400;
        throw error;
      }
    }
  }
  return Object.fromEntries(
    Object.entries(normalized).filter(([, value]) => value),
  );
}

export function requireAmount(value) {
  if (!Number.isInteger(value) || value <= 0) {
    const error = new Error("amount must be a positive integer in the smallest currency unit");
    error.statusCode = 400;
    throw error;
  }
  return value;
}

function optionalString(value) {
  if (value == null || value === "") return undefined;
  if (typeof value !== "string") {
    const error = new Error("address fields must be strings");
    error.statusCode = 400;
    throw error;
  }
  return value.trim();
}
