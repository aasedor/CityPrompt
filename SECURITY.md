# Security policy

## Supported branch

Security fixes are applied to `main`. Historical pilot branches are not
supported release lines.

## Reporting

Report suspected vulnerabilities privately to the repository owner. Do not
open a public issue containing credentials, personal data, exploit details, or
private project content.

Include:

- the affected commit or release;
- the smallest reproducible case;
- expected and observed behavior; and
- any evidence needed to assess impact.

## Secret handling

- Store local credentials only in `.env` or an approved secret manager.
- Never commit `.env`, access keys, API keys, passwords, tokens, or exported
  browser/session data.
- Use only placeholder values in documentation and `.env.example`.
- Treat a committed secret as compromised: revoke or rotate it first, then
  remove it from the current tree and separately decide whether Git history
  must be rewritten.
- Never reuse Docker's local development passwords in a shared or deployed
  environment.

The repository previously contained historical cloud-storage credentials in a
setup document. They are absent from the current tree but must be rotated by
the account owner because existing clones and Git history may retain them.

## Student environments

Provide students with scoped, revocable credentials and the minimum provider
access required for the lesson. Do not share instructor or production keys.
Prefer a dedicated class environment with spending limits and monitoring.
