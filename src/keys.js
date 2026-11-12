const ACCOUNT_TOKEN = /^(?:pk|sk|rk|rkcs)_(?:test|live)_(51[A-Za-z0-9]{15})/;

export function stripeAccountToken(key) {
  if (typeof key !== "string") return null;
  const match = key.match(ACCOUNT_TOKEN);
  return match ? match[1] : null;
}

export function publishableKeyConfig(publishableKey, secretKey) {
  const publishableAccount = stripeAccountToken(publishableKey);
  const secretAccount = stripeAccountToken(secretKey);
  return {
    publishableKey: publishableKey || null,
    publishableKeyAccount: publishableAccount,
    secretKeyAccount: secretAccount,
    accountsMatch: Boolean(
      publishableAccount && secretAccount && publishableAccount === secretAccount,
    ),
  };
}
