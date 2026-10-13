import type { Configuration } from "@azure/msal-browser";

const tenantId = import.meta.env.VITE_ENTRA_TENANT_ID as string;
const clientId = import.meta.env.VITE_ENTRA_CLIENT_ID as string;

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: "/",
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
};

// Requests an access token whose audience is this app's own client ID, so
// the backend's require_role() can read the `roles` claim it puts there.
export const loginRequest = {
  scopes: [`api://${clientId}/.default`],
};
