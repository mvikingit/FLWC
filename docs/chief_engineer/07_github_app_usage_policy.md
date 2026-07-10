# FLWC GitHub App Usage Policy

GitHub, CI, push-gate output, GitHub App, and `@codex` review are evidence channels. They are not final authority.

GitHub App use is escalation only. Use it when local artifact evidence is insufficient, contradictory, too broad for local inspection, or when Commander / Chief Engineer explicitly requests independent repo-grounded evidence.

Chief Engineer verdict is required for node closure. A passing CI check, clean push-gate, GitHub App comment, or remote SHA match does not by itself ACCEPT a node.

P620 push must use the accepted SSH alias route:

```text
github.com-p620-lsdserv443
```

No HTTPS token path is authorized. Do not print, migrate, inspect, or store tokens, credentials, browser sessions, or SSH private keys in Git, logs, prompts, screenshots, or LLM context.

No git remote configuration mutation is authorized unless a named node explicitly opens it.
