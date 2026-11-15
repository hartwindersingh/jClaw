# Security Policy

**Developer:** Hartwinder Singh

## Reporting a vulnerability
Please do not publish credentials, Gateway tokens, private project files, or exploit details in a public issue. Open a private GitHub Security Advisory for this repository if the feature is available, or contact the maintainer through the GitHub profile.

## Credential handling
- jClaw does not ask users to paste OpenClaw Gateway tokens into its UI.
- Gateway authentication is delegated to the locally installed OpenClaw CLI and its configured credential store.
- Never put Gateway tokens in URLs, screenshots, issue reports or logs.
- Treat the configured OpenClaw agent's tool permissions as privileged access.

## Safe use
Only connect to a Gateway you trust. Use least-privilege OpenClaw agents and workspace restrictions. Test execution can run arbitrary repository code; inspect projects before running tests.
