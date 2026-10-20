# Publish this MVP with GitHub Pages

This folder is the complete static site. Put its **contents** at the root of the branch you want to publish, then configure GitHub Pages to deploy that branch from `/(root)`.

Included files:

- `index.html` — presentation and browser-side Living Archive.
- `cvp-genesis.json` — unsigned namespace/descriptor linking the parts of the MVP.
- `AI-AGENT-INSTRUMENT.json` — draft definition separating the declared base model, agent, agency policy, memory, and optional fine-tuning.
- `HERMES-CVP-AGENT-ARCHITECTURE.md` — maps Hermes Agent, model inference, gateway, local memory, tools, and CVP provenance into separate roles.
- `LINUX-AI-STAR-DISTRIBUTION-INSTRUMENT.json` — local ISO byte reference with SHA-512, CIDv1 raw/SHA2-512, and inspection limits.
- `cvp-dictionary.json` — valid JSON packaging of the supplied dictionary source and selected vector definitions.
- `cvp-ministry-trust-source.json` — valid JSON packaging of the trust-source text; gateway/API credentials are redacted.
- `cvp-mvp.json` — machine-readable MVP manifest.
- `documents/` — three PDFs and their CID/digest/vector catalog.
- `assets/` — supplied presentation image.
- `CVP-KYBALION-LINUX-AI-STAR.md` — CVP/agent integration proposal and verification plan for the supplied Linux-AI ISO.
- `HOG-CVP-DEPLOYMENT-TOPOLOGY.md` — proposed HOG gateway placement and security boundaries, based on the linked HOG documentation.
- `HOG-CVP-TOPOLOGY.json` — machine-readable, non-deployed topology descriptor; not a HOG configuration file.

The user-supplied `linux-ai-1.0-star-cinnamon-amd64.iso` is 13,740,867,584 bytes and is not copied into this bundle. Its SHA-512 and CID are recorded in the distribution instrument. Its ISO9660/boot-image marker is recognized, but the ISO has not been boot-tested; its origin, contents, model weights, and base OS are not verified. The AI-agent instrument is an unsigned declaration, not an installed or enforced AI agent. The base-model weights and inference runtime remain unidentified.

The supplied source files are left unchanged. The local feature branch is prepared for review and publication by its owner; it has not been pushed.

The branch also sanitizes the access token in a trust-copy file inherited from the repository's base branch. Originals on the source project and the base branch are not changed.

The observer section on the home page distinguishes public site files, a visitor's browser-local records/key, and an optional upload to a user-operated local IPFS node.

The descriptor and catalog are unsigned. The local archive can sign browser-created records, but this demo is not a globally ordered registry and does not establish identity, trusted time, patents, ownership, legal enforceability, or jurisdiction. A CID verifies content against a reference when the content is available; it does not guarantee continued availability.
