# CVP Kybalion Linux-AI 1.0 “Star”

## Status

The project owner has supplied a file named `linux-ai-1.0-star-cinnamon-amd64.iso` (13,740,867,584 bytes). A file-signature utility recognizes it as an ISO 9660 CD-ROM filesystem with a DOS/MBR boot sector and labels the image bootable. This checks the file's format markers, not whether it successfully boots or what software it contains. The ISO is a local input asset, not included in this repository or its GitHub Pages bundle. Its SHA-512 and CID have been computed locally and are recorded in [`LINUX-AI-STAR-DISTRIBUTION-INSTRUMENT.json`](./LINUX-AI-STAR-DISTRIBUTION-INSTRUMENT.json). Those identifiers match the exact bytes checked; they do not authenticate the builder or certify the image contents or behavior. Its build contents, origin, security, model availability, and Cinnamon integration have not yet been independently inspected or tested.

This document describes a proposed CVP integration and agent policy. Do not read it as evidence that the CVP agent is already installed in, or bundled with, the supplied ISO.

The intended experience is a portable, local-first creative and provenance workstation: a person can inspect project files, choose what to record, create and verify CVP instruments, and optionally use locally installed AI tools. The named AI agent is `actofzero-0x13-CVD-Mentalism-minestry — kyballion-CVP-IPFS-tri-vector-Intelligence Agent`; the base model, weights, inference runtime, and current presence in the ISO are not yet identified.

## Observer model: what happens to a file?

The existing web MVP demonstrates one selected payload at a time:

1. **Origin** — the user’s file starts in a location on their device. Selecting it lets the browser read its bytes; selection alone does not upload or relocate it.
2. **Content reference** — the browser computes SHA-512 and, when it has the bytes, derives a CIDv1 raw/SHA2-512 address. A pasted CID is treated as a reference and is not fetched or matched to the bytes by this prototype.
3. **Instrument** — the page builds a record with the CID/digest, vectors, self-reported metadata, a timestamp, and its chain links. The browser signs the canonical record using its local Ed25519 key.
4. **Local persistence** — the record is kept in browser local storage; the non-extractable private signing key is kept in IndexedDB. The key is not included in the exported chain.
5. **Export** — JSON export includes records and signatures, not the original file bytes. A recipient can check the record’s hash, signature against its included public key, and chain links; this alone does not prove a legal identity or a trusted clock.
6. **Optional storage** — an explicit upload action can send payload bytes to a user-configured loopback Kubo node. The current web app does not upload to Pinata. A content address does not guarantee that anyone continues to host the bytes.
7. **Publication** — files copied into the GitHub Pages bundle are public website assets. They are distinct from the visitor’s local browser records, private key, and any content on the visitor’s own IPFS node.

The demo verifies the internal cryptographic structure. It does not make a global first-writer-wins registry, independently retrieve every payload during chain verification, or establish authorship, patent rights, ownership, legal effect, or jurisdiction.

## AI model, agent, agency, and learning

Treat these as separately addressable artifacts and responsibilities:

- **Base model** — the named model and its exact weight files, licenses, runtime requirements, and content CIDs. The supplied ISO name does not by itself identify the model or prove that its weights are included.
- **Agent definition** — the CVP instrument that declares the project-specific Hermes Agent profile, model reference, selected dictionary, instructions/rule vector, enabled capabilities, and approval policy. It is described in [`AI-AGENT-INSTRUMENT.json`](./AI-AGENT-INSTRUMENT.json) and [`HERMES-CVP-AGENT-ARCHITECTURE.md`](./HERMES-CVP-AGENT-ARCHITECTURE.md).
- **Runtime and tools** — the inference engine and any filesystem, terminal, network, IPFS, or publishing integrations. Record their versions and hashes separately before claiming reproducibility.
- **Learning and memory** — separate append-only interaction/curation records from changes to model weights. If local fine-tuning is later enabled, it creates a distinct model artifact with a new digest/CID, dataset provenance, explicit consent, and an approval step; it does not silently overwrite the referenced base model.
- **Agency** — default to local reading and drafts. Require an explicit human approval before file writes, shell/code execution, model downloads, network calls, IPFS publication, updates, or GitHub actions. No automatic scanning/signing of all system activity.

This is a proposed policy, not an assurance of current software enforcement. Until the application implements and tests these controls, OS permissions and user supervision remain the actual safeguards. An AI instrument can attest to the declared model/tool references and the agent's own record sequence; it cannot by itself prove that a model was trained as claimed, that its answers are true, or that a human has a particular legal identity.

Hermes profiles are the proposed boundary for isolating each project's model configuration, tools, skills, memory, sessions, and gateway port. Hermes memory remains working state; selected records can be deliberately exported into CVP. Enabling a Hermes tool or channel can still create filesystem or network effects, so each capability needs explicit configuration and testing.

The draft [`AI-AGENT-INSTRUMENT.json`](./AI-AGENT-INSTRUMENT.json) records the exact agent name supplied by the project owner and references the distribution instrument. It intentionally leaves the model weights, inference runtime, and agent definition CID blank until those artifacts are identified and the definition bytes are finalized. The ISO's exact SHA-512/CID identify the complete image bytes, but do not say which AI model, if any, is inside it.

## Proposed system layout

The supplied image is named as an amd64 Cinnamon ISO. Its actual base OS and build recipe have not been inspected. Identify those first; do not assume Fedora Silverblue or any other base. An immutable desktop is one possible future direction because an OS image can be separated from ordinary user data and app state; immutability does not, by itself, make the system secure, private, offline, or legally sovereign.

| Layer | Proposal | Boundary |
|---|---|---|
| Base operating system | Inspect the supplied ISO to identify its actual Linux base and release | Record the distro/release, package sources, build recipe, and update trust chain before making further claims. |
| Desktop experience | ISO filename declares Cinnamon; verify by inspecting/booting the image | Do not infer desktop integration or capability from the filename alone. |
| CVP archive client | User-launched local application with signing, inspection, verification, and export | Do not silently monitor or sign every file, edit, or system event. Recording is explicit and reviewable. |
| Optional network gateway | HOG in front of separately hosted authenticated CVP/API services, if needed | The current static Pages site and browser-local archive do not require HOG. See the [HOG/CVP topology proposal](./HOG-CVP-DEPLOYMENT-TOPOLOGY.md). |
| Genesis and vocabulary | Bundle the public dictionary view and genesis descriptors as versioned data | A bundled copy is a reference, not proof that its declared CID matches the source unless independently verified. |
| Signing key | Generate per-user keys and protect private-key operations using appropriate OS facilities | Show backup/recovery trade-offs; never publish private keys or treat a public key alone as a civil identity. |
| Local AI | Optional model runner and user-selected model stored on local disk | “Local” depends on the chosen software/model and must be demonstrated; downloading models requires a network unless separately supplied. |
| Content storage | User-selected local folder or an explicitly configured local IPFS node | Make every upload, remote retrieval, and pin action visible; do not bundle gateway/API secrets. |
| Updates and audit | Signed builds, source/release hashes, an SBOM, reproducible-build goals, and documented upgrade/rollback procedures | Hashes help detect byte changes; provenance still depends on who signed and how release keys are protected. |

## Bootable USB: staged path

The supplied ISO should be inspected and tested before treating it as a release. Keep the original ISO unchanged, verify the recorded digest against the original file, inspect its contents in a disposable environment, and test boot/install behavior in a virtual machine before writing any USB device.

1. **Keep the current web MVP** as the functional baseline and document its exact local-storage, key, network, and export behavior.
2. **Make a desktop client prototype** that opens selected files, previews the metadata to be signed, writes an exportable record, and requires a clear confirmation before any upload.
3. **Test on a live atomic desktop** in a virtual machine first. Verify startup, persistence, key permissions, export/import, offline behavior, and update/rollback before attempting USB media.
4. **Build a live image** from a documented build recipe. Keep user records and keys on a separate, explicitly chosen persistent volume; a default live session should not imply that data persists after shutdown.
5. **Publish verifiable releases** with checksums, signed release metadata, source and licenses, an SBOM, and instructions for independently checking the image before writing it to USB.
6. **Only then call it “1.0”** after hardware-compatibility, security, recovery, accessibility, and update testing on supported devices.

## Presentation name and trust vocabulary

“CVP Kybalion Linux-AI 1.0 ‘Star’” and “The Mentalism Ministry Trust” can be presented as the creator’s project names and declared framework. The archive can preserve those declarations as signed, content-addressed records. A CID or signature demonstrates a relationship between bytes and a key; it does not independently establish the asserted trust, a patent, an enforceable legal jurisdiction, or the truth of a legal claim.

The source materials mention an IPFS gateway. A gateway is a retrieval endpoint, not the content itself and not a legal jurisdiction. Publicly published PDFs, a public dictionary, private trust instruments, and user-held keys should be treated as separate assets with separate access and disclosure choices.

## Current implementation checklist

- [x] Browser-side archive prototype and local chain verification.
- [x] PDF and presentation bundle with CID/digest/vector catalog.
- [x] Observer-facing description of file movement, storage, and visibility.
- [ ] Desktop application packaging and OS key-storage integration.
- [ ] Local AI model choice, licensing, hardware requirements, and offline evaluation.
- [ ] Inspect the supplied ISO; establish its base OS, build source, licenses, AI model/runtime contents, and network behavior.
- [ ] Immutable-image build pipeline, release signing, SBOM, and rollback tests for a future CVP-integrated image.
