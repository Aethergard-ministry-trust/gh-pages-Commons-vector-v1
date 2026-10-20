# HOG and CVP deployment topology

## Status and scope

This document reformats the HOG [deployment topology documentation](https://paulopiriquito.github.io/hog/architecture/deployment/) supplied for this project into a proposed CVP deployment model. That documentation describes stateless replicas, trusted-proxy filtering, two session modes, separate login/verification configurations, container stages, and optional OTLP export. HOG source code, image definitions, configuration schema, and implementation tests are not present in this repository. The architecture below follows the published documentation; it does not independently verify a particular HOG build. It is **not a runnable `hog.yaml` or Docker Compose deployment**.

The proposal treats HOG as an optional HTTP gateway around networked CVP services. It does not replace the current static GitHub Pages site or the browser-local archive, and it does not create a global archive, a consensus protocol, or legal jurisdiction.

## Proposed request paths

```text
Public reader
  └─ HTTPS → GitHub Pages
       └─ static presentation, PDFs, public JSON; no HOG required

Authenticated CVP user
  └─ HTTPS → TLS ingress / load balancer
       └─ private HTTP hop → N × HOG frontend replicas
            ├─ OIDC login and browser session
            └─ private service network → CVP API / optional Hermes Gateway
                                              └─ Hermes Agent → chosen local model/tools

CVP API / approved local service
  └─ private network → local Kubo API
       └─ explicit retrieval or pin request only

HOG API verification replicas (separate configuration)
  └─ HTTPS → API client with Bearer access token
       └─ TLS ingress → N × HOG verification-only replicas
            └─ private hop → protected backend
```

The static Pages MVP remains independently usable. Add HOG only if a separately hosted API, login flow, or private archive needs an authenticated ingress. Hermes Gateway is a different component that connects Hermes to enabled chat channels and HTTP clients; HOG can optionally protect a remote Hermes API, but HOG does not replace Hermes Gateway or its agent loop. Do not expose the Kubo administrative API directly to the Internet or browser.

The machine-readable, non-executable counterpart is [`HOG-CVP-TOPOLOGY.json`](./HOG-CVP-TOPOLOGY.json).

## Replica and session model

- Run identical HOG replicas behind the chosen ingress if the actual HOG implementation supports this topology. Do not assume that this description guarantees coordination-free behavior without checking its source and release documentation.
- The supplied design describes a sealed stateless cookie by default. Replicas that accept the same cookies must share a strong session key, protected outside source control and rotated using a documented plan. Stateless application replicas still share a cryptographic trust root.
- If silent token refresh is required, an opt-in state provider introduces a shared session dependency. Use a supported encrypted/TTL state-store plugin only after checking its implementation, failure behavior, backup/retention policy, and handling of refresh tokens. Fail closed if session state cannot be read.
- If refresh is not required, prefer no server-side session store. Public static content requires neither HOG sessions nor an identity provider.

## Trusted proxy and transport rules

1. Terminate public TLS at a maintained ingress/load balancer. Forward to HOG over a private, access-controlled network. If the ingress-to-HOG network is not trusted, use TLS or mutual TLS on that hop rather than assuming a private network makes cleartext safe.
2. Keep `trustedProxies` empty unless the exact source CIDRs/IPs of the immediate upstream proxy are known. Do not configure `"*"` in production. The setting trusts the connecting peer to supply forwarding headers; it does not validate every network hop behind that peer.
3. Ensure the ingress removes client-supplied forwarding headers and writes its own canonical `X-Forwarded-*` values. Restrict direct access to HOG so untrusted clients cannot bypass the ingress.
4. With no trusted proxy, forwarded headers should be treated as untrusted/stripped: HOG sees its direct peer, not the original browser address. Configure only the proxy's actual egress addresses to expose the projected client IP/scheme.
5. Do not rely on forwarding headers as user identity or authorization evidence. Use validated OIDC/Bearer credentials and explicit backend authorization.

## Separate login from API verification

If the HOG implementation supports the two roles described in the supplied design, deploy them as distinct configurations and workloads:

| Workload | Responsibility | Credentials |
|---|---|---|
| Frontend/session gateway | OIDC authorization-code flow, browser cookie, logout, and any configured refresh | Only this workload receives the OIDC client secret and redirect configuration it needs. |
| API verification gateway | Validate inbound Bearer access tokens and forward only authenticated identity | Verification-only issuer/client configuration; no login routes, redirect URL, or client secret. |

The backend must validate the expected issuer, audience, signature/allowed algorithm, expiry, and relevant claims, either in HOG or again at the service boundary. Any identity assertion forwarded from HOG must be accepted only from an authenticated, private gateway-to-backend hop; a public caller must not be able to forge the same headers.

## CVP, AI agency, and IPFS boundaries

- The CVP browser archive remains client-side: its current records and private signing key are stored in that browser profile. HOG does not automatically centralize or synchronize them.
- Treat an optional API or Hermes Gateway/agent service as a separate workload. Gateway authentication is not a substitute for per-action capability checks, explicit user approval, or an audit record.
- Require user approval before an agent writes files, executes code, calls external networks, retrieves/pins IPFS data, changes the OS, or publishes an instrument. Keep private signing keys and gateway/session secrets out of model prompts, logs, and exported CVP records.
- Permit Kubo API access only from the intended local/private services. Expose public IPFS retrieval through a separate read-only gateway if needed; do not confuse that with the privileged Kubo API.
- A successful local record or a set of stateless gateway replicas does not give the archive global ordering, first-writer-wins semantics, or universal persistence. Those properties require separate protocols and infrastructure.

## Container and observability notes

The supplied HOG description names `hog-runtime`, `hog-static`, and `hog-builder`, a non-root UID/GID 10001, a read-only runtime, port 8080, and optional OTLP export. These are **claims from the supplied design text**, not verified image tags or build instructions in this repository. Before deployment, inspect the actual HOG source/release, pin image digests, review the Dockerfile and build stages, verify supported Go/Alpine versions, and test the read-only/non-root configuration.

Keep telemetry local unless an OTLP collector is explicitly configured. If exporting, document which fields leave the host and prevent credentials, cookies, tokens, private keys, and sensitive payloads from entering logs/traces.

## Deployment checklist

- [ ] Obtain and inspect the HOG source repository and versioned config schema.
- [ ] Confirm which topology, OIDC, session, proxy, and telemetry features the selected HOG version really implements.
- [ ] Decide whether this deployment needs login at all; leave public GitHub Pages static and independent.
- [ ] Document ingress egress CIDRs; strip incoming forwarding headers; configure only trusted immediate peers.
- [ ] Store OIDC secrets and shared session keys in a secret manager, not Git or container image layers.
- [ ] Choose stateless cookie or state provider based on an explicit refresh requirement.
- [ ] Isolate HOG, CVP API, Hermes Gateway/agent, and Kubo on deliberately scoped network paths.
- [ ] Test token validation, spoofed forwarding headers, session-key rotation, state-store failure, and unauthorized agent actions.
- [ ] Pin image digests, run as non-root, use read-only filesystems where supported, and inspect the SBOM.
- [ ] Add a real Compose/config only after the HOG source and schema can be validated.
