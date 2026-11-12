/**
 * Stripe Tax collects nothing until the head office is set and at least one
 * registration is active. Enabling automatic_tax without that returns no error
 * and collects zero tax, so this check refuses to turn it on.
 */
export async function taxReadiness(stripe) {
  try {
    const settings = await stripe.tax.settings.retrieve();
    const registrations = await stripe.tax.registrations.list({
      limit: 100,
      status: "active",
    });
    const activeRegistrations = (registrations.data || []).map((registration) => ({
      id: registration.id,
      country: registration.country,
      status: registration.status,
    }));
    const headOfficeActive = settings.status === "active";
    return {
      settingsStatus: settings.status,
      headOfficeActive,
      activeRegistrations,
      canCollect: headOfficeActive && activeRegistrations.length > 0,
      blockedReason: headOfficeActive
        ? activeRegistrations.length > 0
          ? null
          : "No active tax registration. automatic_tax would collect no tax. Add a registration only for a jurisdiction where the business is already registered with the tax authority."
        : "Stripe Tax head office address is not active. Set it in Dashboard > Tax > Settings before collecting tax. This integration does not invent a head office address.",
    };
  } catch (error) {
    return {
      settingsStatus: null,
      headOfficeActive: false,
      activeRegistrations: [],
      canCollect: false,
      blockedReason: `Could not read Stripe Tax settings (${error.code || error.type || "error"}). automatic_tax stays off. Claim the sandbox for a full key, then set the head office and record existing registrations.`,
    };
  }
}
