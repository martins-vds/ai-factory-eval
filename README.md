# AI Factory Swarm: eval repository

This repository holds the end-to-end eval for the [AI Factory Swarm](https://github.com/martins-vds/ai-factory-swarm)
harness (agent-topology plan, phase 1). Each eval case runs on its own branch, created from a pinned commit of the
pilot or synthetic target. A Copilot session works the case, and the harness's `afs-eval` grades the resulting PR.

`main` holds only this README and CODEOWNERS. Nothing from the eval cases is ever merged here.

Workflow runs on Copilot PRs here run without approval. This is the one exception to ADR-0039, taken with its
mitigations: no read tokens for sources or billing, a write token scoped to this repository only, read-only
default workflow permissions, a ruleset on `main`, and CODEOWNERS for `.github/` and `.migration/harness/`.
