# LLM-Agnostic Harness Mode

## Goal

Run OpenViking as a local context and skill substrate without requiring an API key or an OpenViking-owned language model.

The active host — for example Hermes, OpenCode, Codex, Claude Code, Eve, or another harness — owns reasoning. OpenViking owns durable context, local retrieval, skill packages, metadata, and provenance.

## Existing model-less substrate

OpenViking already provides most of the required foundation:

- local AGFS/RAGFS storage;
- a local GGUF dense embedder as the default embedding configuration;
- `find()` and `/skills/find` semantic retrieval without session intent analysis;
- `retrieval.enable_intent=false` to make `search()` use the raw query rather than an LLM query planner;
- local full-text indexing / grep support;
- skill packages with content-addressed integrity manifests;
- `processing_mode=vectors_only` for resource ingestion without VLM semantic extraction.

Harness mode should preserve those paths rather than replace them.

## Model ownership

The context engine must not require a VLM, query-planner LLM, or remote reranker.

When host-model judgment is useful, the host receives candidates and evidence, reasons over them, and may write an explicit decision back through normal OpenViking APIs.

```text
host model / harness
        |
        v
skill/context tools
        |
        v
OpenViking local core
  - filesystem
  - local embeddings
  - lexical search
  - metadata
  - provenance
  - graph data
```

## Skill routing metadata

A skill may add routing metadata to standard SKILL.md frontmatter:

```yaml
---
name: meta-wearables-thermal
description: Audit runtime thermal handling for Meta Wearables.
principle: Thermal limits are runtime correctness requirements.
family: meta-wearables
domains:
  - thermal
  - runtime
intents:
  - audit
  - implementation
aliases:
  - temperature handling
relations:
  required_for_audit:
    - session-lifecycle
  co_audit_with:
    - streaming
  alternative_to:
    - another-thermal-workflow
---
```

The fields are deliberately descriptive rather than a rigid ontology:

- `description`: what the skill covers;
- `principle`: the short invariant or idea it protects;
- `family`: a broad skill family used for grouping;
- `domains`: subject areas;
- `intents`: tasks for which the skill is useful;
- `aliases`: alternate user language;
- `relations`: typed edges. Relation names remain extensible.

The deterministic L0 representation includes these fields so local semantic retrieval can use them without asking another LLM to summarize the skill.

L1 remains authoritative skill content when no VLM is configured. L2 remains the complete SKILL.md package and auxiliary files.

## Host-side resolver policy

The host model, not OpenViking, decides activation.

A recommended policy is:

- exact or clearly dominant match: activate without asking;
- required dependency: include automatically;
- compatible/complementary skills: compose when useful;
- materially different alternatives: ask one consolidated question;
- conflicts: resolve before execution;
- weakly related skills: do not inflate context.

The relation graph is evidence for the host, not an automatic execution engine.

## Context budget

Retrieval may be broad, but prompt inclusion should be narrow.

Use progressive disclosure:

1. retrieve candidate L0 metadata;
2. inspect only relevant L1 content;
3. load complete L2 skill packages only after activation;
4. follow required graph edges;
5. avoid loading weakly related branches.

## Evaluation

Use an existing eval substrate rather than a custom judge framework.

Promptfoo is the intended first eval runner. It can execute deterministic assertions and model-based graders through CLI/provider adapters. Eve sandboxes can supply isolated trial environments. Eval cases decide what evidence a grader receives: outcome, repository state, trajectory, retrieval trace, or combinations of those.

The context harness itself should be evaluated for:

- skill recall and ranking;
- ambiguity handling;
- required dependency recall;
- conflict handling;
- hallucinated-skill rate;
- grounding/provenance;
- context tokens consumed;
- retrieval latency.

## Remaining work

This first slice only makes the skill path model-less and routing-aware.

Follow-up work should address:

1. host-driven or deterministic memory extraction instead of mandatory VLM extraction;
2. model-less summaries for arbitrary resources where L0/L1 are desired;
3. folder/family-aware skill storage and navigation;
4. explicit graph persistence and graph query tools;
5. hybrid lexical + dense fusion benchmarks;
6. host adapters for Hermes, OpenCode, Eve, Codex/Claude CLIs, and MCP;
7. Promptfoo eval suites before changing retrieval ranking defaults.
