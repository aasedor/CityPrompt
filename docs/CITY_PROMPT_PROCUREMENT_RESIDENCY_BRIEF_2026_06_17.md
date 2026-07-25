# City Prompt — Data-Residency & Procurement Brief (One-Pager + PIA Starter)

**Prepared for:** City of Calgary Mobility — June 17, 2026
**Audience:** the team that ran the M365 Copilot risk assessment + IT Security/Privacy (FOIP/POPA) office
**Purpose:** answer ONE gating question before we invest further in render accuracy — *which image-generation engine can City Prompt run on and still clear Alberta privacy/residency review?* Companion to `CITY_PROMPT_ACCURACY_RESEARCH_2026_06_17.md` §8.

---

## TL;DR (the ask)
City Prompt generates AI street/intersection design renders for public consultation. The render *quality* roadmap depends on which image engine we can use, and that is a **privacy/procurement decision, not an engineering one**. We need a decision (or a "go investigate") on **one of three paths**, in preference order:

1. **Azure OpenAI GPT-image in a Canada region** — preferred (same vendor already cleared for Copilot). **Open question: is the GPT image model available as a true Canada Central/East *regional* deployment, or only Global/Data-Zone?** (Current evidence: image models are not yet in Canada regional deployments — needs confirmation with our Microsoft account team.)
2. **Vertex AI (Gemini/Imagen) in Montréal/Toronto** — text/LLM residency is confirmed, but **no current Gemini/Imagen *image* model is confirmed residency-available in Canada.** Needs confirmation with Google Cloud.
3. **Self-hosted open-weight model on Canadian/on-prem GPU** — the only *confirmed* path to true Canadian-resident image generation today. Clean-licence, clean-origin stack (Stable Diffusion 3.5 + FLUX.1 [schnell]). Higher ops cost; full sovereignty.

A "no personal information is processed" argument (below) likely makes Path 1 acceptable under POPA. That is the fastest route if the Canada-region image model exists.

---

## Why this matters now (context)
- **City precedent (Feb 6, 2026):** Calgary blocked ChatGPT on all networks/devices (US data transfer) **but approved Microsoft 365 Copilot** after a risk assessment. Lesson: *govern AI, don't ban it* — consumer endpoints are out; an enterprise tenant with a completed assessment is the accepted pattern. This is why **Azure is the path of least resistance**.
- **Alberta POPA** (in force June 11, 2025) replaced FOIP's privacy provisions. It **does not mandate Canadian data residency**; it requires *reasonable safeguards* + a **Privacy Impact Assessment**. The **OIPC's mandatory PIA template** (released Mar 26, 2026; mandatory for submissions from May 1, 2026) requires documenting where data is stored, who controls it, and **US CLOUD Act exposure** for US-parented vendors.

## The "low personal-information" argument (likely our fastest clearance)
Street/intersection design renders typically contain **no personal information** — they depict roadway geometry, not identifiable individuals. Inputs are map context + design archetypes + dimensioned diagrams. If we (a) prohibit staff from entering PII/confidential content into prompts, and (b) confirm the vendor's **no-training-on-our-data** commitment, the residual CLOUD-Act risk is **low and arguably acceptable** for the core use case. We should make this argument explicitly in the PIA. We reserve the self-hosted/sovereign path for any future workflow that *would* involve PII.

---

## Specific questions to put to IT Security / Privacy / vendor account teams
1. **Microsoft:** Is `gpt-image-2` (or the current GPT image model) available as a **Canada Central / Canada East regional deployment** in Azure AI Foundry — not Global, not US/EU Data Zone? If not, is it on the roadmap, and what is the in-region storage/processing commitment?
2. **Microsoft/Privacy:** Confirm the Azure OpenAI **no-training, no-human-review, data-stays-in-region** commitments apply to the image model and to our tenant.
3. **Google Cloud:** Is any Gemini 3.x image / current Imagen model available with **data residency at rest and in ML processing** via the Montréal/Toronto regional endpoints? (Imagen 4.0 was the only Canada-available image model and was deprecating ~June 30, 2026 — what replaces it?)
4. **Privacy/Legal:** Given renders carry no PII, does the "low personal-information" framing satisfy POPA's reasonable-safeguards test for a US-hyperscaler-in-Canada deployment, with CLOUD Act exposure documented?
5. **Infra:** If we need the self-hosted fallback, do we have (or can we procure) a **Canadian / on-prem GPU** that can host the full stack (depth model + ControlNet + diffuser + orchestrator) with **no hop leaving the country**?

---

## Engine deployability — current evidence (verify at decision time)
| Path | Deployable today? | Note |
|---|---|---|
| Azure OpenAI GPT-image, Canada Central/East regional | **Verify** | Image models appear Global/Data-Zone only today; best fit *if* a Canada regional deployment exists. |
| Vertex AI Gemini/Imagen image, MTL/TOR regional | **Verify** | Text residency confirmed; no current image model confirmed residency-available in Canada. |
| AWS Bedrock image, ca-central-1 | **No** | No image-gen model found in ca-central-1; Nova Canvas/Titan going Legacy/EOL. |
| Azure US/EU "Data Zones" | **Do not use** | US Data Zone = US storage — the exact thing the City objected to. |
| Self-hosted open-weight on Canadian/on-prem GPU | **Yes** | Only confirmed true-Canadian-resident path. SD3.5 + FLUX.1 [schnell] (clean licence + origin). FLUX `[dev]` needs a paid Black Forest Labs licence. Hold PRC-origin models (Qwen-Image) behind a security-origin clearance. |

> A Canadian-owned text/RAG layer (**Cohere / North**, deployable in SAP/Bell sovereign cloud) can ground the design-standards retrieval and provide a "Canadian AI" narrative — but it does **not** generate images.

---

## POPA PIA starter — sections to draft (against the OIPC Mar 2026 template)
1. **Initiative description:** AI-assisted generation of conceptual street/intersection redesign images for internal review and public engagement.
2. **Personal information inventory:** renders + inputs — assert **no PII collected/processed**; document the prohibition on entering PII into prompts.
3. **Data flow & storage:** map every hop (prompt → model → image → storage). Identify the region of each. **No hop should leave Canada** unless justified.
4. **Jurisdictional analysis / cross-border:** name the vendor's parent jurisdiction; **document US CLOUD Act exposure** if a US hyperscaler; state mitigations (no-training commitment, no PII, in-region storage).
5. **Safeguards:** enterprise tenant, access controls, no-training contract terms, output review/sign-off, content-provenance labelling (C2PA).
6. **Governance:** human-in-the-loop engineer sign-off before any public render; AI-generated-concept labelling; alignment with the City's AI governance process that cleared Copilot.
7. **Residual risk & acceptance:** state the low-PII residual-risk argument and request sign-off.

---

## Recommended decision sequence
1. Send questions 1–3 to the Microsoft and Google account teams **this week** (long lead time).
2. In parallel, start the PIA draft (sections above) so it's ready when the engine answer lands.
3. If Azure Canada-region GPT-image **exists** → that's the engine; finish the PIA and proceed.
4. If it **doesn't** → stand up the self-hosted SD3.5 / FLUX-schnell sovereign stack on a Canadian GPU as the durable path.
