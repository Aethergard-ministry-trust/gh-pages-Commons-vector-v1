# Hermes Agent as a CVP entity

## Identity and status

The project-specific agent is declared as `kyballion-CVP-IPFS-tri-vector-Intelligence Agent`, implemented conceptually on the **Hermes Agent** framework described in the supplied local-first deployment notes.

The notes are an architecture reference, not proof that Hermes is installed in `linux-ai-1.0-star-cinnamon-amd64.iso`. The installed Hermes version, base model, inference backend, enabled tools, profile configuration, and gateway exposure have not been inspected. The proposed entity is described in [`AI-AGENT-INSTRUMENT.json`](./AI-AGENT-INSTRUMENT.json).

## Keep the entities distinct

```text
CVP namespace + dictionary + rule vector
                 │ describes
                 ▼
CVP Hermes agent definition (name, profile, tools, approval policy)
                 │ runs through
                 ▼
Hermes Agent loop ───── Hermes Gateway (optional channel/API entry point)
        │                             │
        ├─ local inference backend    └─ enabled channels; may use external networks
        ├─ local model
        ├─ project-scoped tools
        └─ profile memory and sessions
                 │ explicit user-approved actions
                 ▼
files / selected APIs / local Kubo / CVP record export
```

Hermes is the agent framework and tool-dispatch loop, not the model itself and not the CVP provenance archive. Ollama or `llama.cpp` can be selected as local inference backends, but a locally hosted model does not make every enabled tool, channel, auxiliary task, or network request local.

## Who serves whom; who remembers what?

| Component | Serves | State/location | Important boundary |
|---|---|---|---|
| Local model backend | Hermes inference requests | Model weights and runtime on the selected machine, if confirmed | A model name is not proof that the corresponding weights are installed or that inference remains local. |
| Hermes Agent | The user through a selected project profile | Tool configuration, session state, and memory files in that profile | Tool access gives the agent capability; restrict OS permissions and require user approval for consequential actions. |
| Hermes Gateway | Enabled messaging channels or HTTP clients | Gateway process/configuration; session behavior depends on the actual installation | Bind local APIs to loopback by default. A channel such as Telegram or Slack can send content outside the device. |
| CVP archive | People who create, export, or verify instruments | In this MVP, browser local storage and IndexedDB; exported JSON can be kept elsewhere | Hermes memory is not automatically a signed CVP history. Export or explicitly register selected records. |
| HOG, if later deployed | Authenticated ingress to separately hosted services | Proxy/session configuration and any selected session state provider | HOG is optional and distinct from the Hermes Gateway; neither should expose Kubo's administrative API. |
| IPFS/Kubo | Users or applications retrieving/pinning addressed content | Pinned blocks on the user's configured node and possibly other peers | A CID is an address, not a storage guarantee. Publishing may make content retrievable by others. |

“Stateless location” can describe a HOG replica or a request-serving process, not a system with no memory anywhere. Hermes sessions and profile memory are stateful files. CVP can preserve selected history as separate, portable provenance instruments, without claiming that every internal thought or private session is recorded.

## Suggested local-first policy

- Start with a project-specific Hermes profile so configuration, skills, memory, tools, and gateway port are separated from other projects.
- Configure the primary model backend explicitly. Configure auxiliary vision, summarization, compression, and search providers explicitly as well; do not allow an undocumented cloud fallback.
- Keep web search, browser automation, code execution, messaging channels, and scheduled jobs disabled until needed. Enable capabilities per project and document which ones make network calls.
- Limit filesystem tools to a dedicated workspace. Do not grant access to SSH/GPG keys, cloud credentials, private key stores, or unrelated personal directories.
- Require explicit confirmation before file writes/deletion, shell or code execution, outbound network calls, sending messages, model downloads, IPFS retrieval/pinning, signing/registering instruments, OS changes, or GitHub publication.
- Treat Hermes memory as working memory controlled by the user. Create CVP provenance records only for deliberately selected events or artifacts; never record sensitive prompts or files automatically.
- If memory or model fine-tuning is exported as an artifact, give it its own version and digest/CID, record dataset/license provenance, and leave the base model unchanged.

These are design requirements, not controls proven to exist in the provided ISO. Verify the installed Hermes version's actual configuration, profile isolation, tool permissions, network behavior, and failure/fallback policy before relying on them.

## Hermes Gateway versus HOG

Hermes Gateway connects Hermes to enabled chat channels and its own HTTP API. HOG, if added, is a separate ingress/authentication layer for a hosted site or backend. A possible remote path is:

```text
User → HTTPS ingress → HOG → protected Hermes Gateway/API
                                └─ Hermes Agent → explicitly selected tools
```

Keep Hermes Gateway bound to loopback/private networking unless remote access is deliberately required. If HOG is used, configure its trusted proxies to the immediate ingress addresses, protect any shared session key, and keep OIDC secrets only in the session-terminating workload. Do not publish the Hermes HTTP API or Kubo admin API directly.

## CVP instrument lifecycle for the agent

1. **Agent definition:** declare Hermes framework/version, project profile, selected model/backend, enabled toolsets, approval policy, and CVP dictionary/rule-vector reference.
2. **Input instrument:** the user explicitly selects a file or prompt worth recording; compute its content digest/CID locally when possible.
3. **Action declaration:** record the requested action, tools permitted, and whether the user approved it. Keep secrets and sensitive prompt bodies out of public records.
4. **Output instrument:** record a digest/CID for the produced output and link it to the input and agent-definition instruments.
5. **Memory/fine-tuning distinction:** working memory is not a model change. If weights are tuned, produce a distinct model artifact with new provenance and an approval step.

Cryptographic links can make these declarations tamper-evident after signing and publication. They do not prove which software actually ran, that its output is true, that a human is legally identified, or that the referenced data will remain available.
