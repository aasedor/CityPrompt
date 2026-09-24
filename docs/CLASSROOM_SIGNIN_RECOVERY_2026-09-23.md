# Classroom sign-in checkpoint — 2026-09-23

Google and Microsoft OAuth now issue an opaque, ten-minute state record in
Redis, bind it to an HttpOnly browser cookie and consume it atomically before
any provider exchange or account lookup. A different browser, expired state,
replay, wrong provider or unavailable Redis cannot complete the callback.
The redirect origin comes from the issued allowlisted record.

The existing JSON authorization-URL endpoint is retained. It now points to a
top-level API `/start` navigation, which sets the cookie before redirecting to
the provider. This supports separate frontend/API sites without relying on
third-party cookies. Production uses a Secure, SameSite=Lax, host-only cookie.
The configured provider callback URL determines the start origin and must be
the public HTTPS API origin; reverse-proxy and provider configuration still
require hosted verification.

Verification: 16 focused unit/API/configuration tests passed; the additional
real-Redis test also passed on the existing local recovery Redis with isolated
expiring keys. Twelve simultaneous attempts to consume one issued state produced
one success and eleven rejections. Wrong-browser/provider requests did not
consume the legitimate state; expiry and service failure were rejected.
No database was flushed, account created or live provider sign-in performed.

Remaining classroom gates: actual hosted Google/Microsoft flows, account roles,
project/media isolation, invitations/revocation and instructor/student recovery.
Existing local password sign-in is unchanged.
