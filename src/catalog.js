/**
 * Candidate product tax codes from the Stripe Tax Codes API.
 * These are options for the merchant to confirm with a tax advisor.
 * The integration does not choose a legally correct code on its own.
 * Guide: https://docs.stripe.com/tax/tax-codes
 */
export const SERVICE_LINES = {
  game_development: {
    label: "Custom game development",
    candidates: [
      {
        id: "txcd_10203001",
        name: "Downloadable Software - custom - business use",
      },
      {
        id: "txcd_20060000",
        name: "Professional Services",
      },
      {
        id: "txcd_20030000",
        name: "General - Services",
      },
    ],
  },
  industrial_design: {
    label: "Enterprise industrial design",
    candidates: [
      {
        id: "txcd_20060013",
        name: "Engineering Services",
      },
      {
        id: "txcd_20060047",
        name: "Architectural Services",
      },
      {
        id: "txcd_10505001",
        name: "Digital Finished Artwork - downloaded - non subscription - with permanent rights",
      },
      {
        id: "txcd_20060000",
        name: "Professional Services",
      },
    ],
  },
  consulting: {
    label: "Industry consulting",
    candidates: [
      {
        id: "txcd_20060048",
        name: "Consulting Services",
      },
      {
        id: "txcd_20060000",
        name: "Professional Services",
      },
    ],
  },
  ai_services: {
    label: "AI intelligent services",
    candidates: [
      {
        id: "txcd_10105002",
        name: "Artificial Intelligence as a Service (AIaaS) - Cloud Based - Business Use",
      },
      {
        id: "txcd_20060048",
        name: "Consulting Services",
      },
      {
        id: "txcd_20060000",
        name: "Professional Services",
      },
    ],
  },
};

const TEMPLATE_ENV = {
  game_development: "INVOICE_TEMPLATE_GAME_DEVELOPMENT",
  industrial_design: "INVOICE_TEMPLATE_INDUSTRIAL_DESIGN",
  consulting: "INVOICE_TEMPLATE_CONSULTING",
  ai_services: "INVOICE_TEMPLATE_AI_SERVICES",
};

export function listServiceLines() {
  return Object.entries(SERVICE_LINES).map(([id, line]) => ({
    id,
    label: line.label,
    candidateTaxCodes: line.candidates,
    templateEnv: TEMPLATE_ENV[id],
  }));
}

export function assertTaxCode(serviceLine, taxCode) {
  const line = SERVICE_LINES[serviceLine];
  if (!line) {
    const error = new Error(
      `Unknown serviceLine. Use one of: ${Object.keys(SERVICE_LINES).join(", ")}`,
    );
    error.statusCode = 400;
    throw error;
  }
  if (!line.candidates.some((candidate) => candidate.id === taxCode)) {
    const error = new Error(
      `taxCode ${taxCode} is not a candidate for ${serviceLine}. Confirm a code from the candidate list with your tax advisor. See https://docs.stripe.com/tax/tax-codes`,
    );
    error.statusCode = 400;
    throw error;
  }
  return line;
}

export function templateIdFor(serviceLine, env = process.env) {
  const name = TEMPLATE_ENV[serviceLine];
  const value = env[name];
  return value && value.trim() ? value.trim() : null;
}
