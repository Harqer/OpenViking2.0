# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0

from types import SimpleNamespace

import pytest
import yaml

from openviking.core.skill_loader import SkillLoader
from openviking.utils.skill_processor import SkillProcessor


_SKILL = """---
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
tags:
  - android
---

# Thermal handling

Inspect thermal state and degradation behavior.
"""


def test_skill_loader_round_trips_routing_metadata():
    parsed = SkillLoader.parse(_SKILL)

    assert parsed["principle"] == "Thermal limits are runtime correctness requirements."
    assert parsed["family"] == "meta-wearables"
    assert parsed["domains"] == ["thermal", "runtime"]
    assert parsed["intents"] == ["audit", "implementation"]
    assert parsed["aliases"] == ["temperature handling"]
    assert parsed["relations"]["required_for_audit"] == ["session-lifecycle"]

    reparsed = SkillLoader.parse(SkillLoader.to_skill_md(parsed))
    for field in ("principle", "family", "domains", "intents", "aliases", "relations"):
        assert reparsed[field] == parsed[field]


def test_skill_abstract_contains_routing_metadata():
    parsed = SkillProcessor._normalize_skill_dict(SkillLoader.parse(_SKILL))
    abstract = yaml.safe_load(SkillProcessor._build_skill_abstract(parsed))

    assert abstract["name"] == "meta-wearables-thermal"
    assert abstract["principle"] == "Thermal limits are runtime correctness requirements."
    assert abstract["family"] == "meta-wearables"
    assert abstract["domains"] == ["thermal", "runtime"]
    assert abstract["intents"] == ["audit", "implementation"]
    assert abstract["aliases"] == ["temperature handling"]
    assert abstract["relations"]["co_audit_with"] == ["streaming"]


def test_skill_relations_accept_scalar_or_list_targets():
    normalized = SkillProcessor._normalize_skill_dict(
        {
            "name": "workflow",
            "description": "Workflow",
            "relations": {
                "variant_of": "automated-workflow",
                "co_audit_with": ["verification", "security"],
            },
        }
    )

    assert normalized["relations"]["variant_of"] == ["automated-workflow"]
    assert normalized["relations"]["co_audit_with"] == ["verification", "security"]


@pytest.mark.asyncio
async def test_skill_overview_falls_back_to_authoritative_content_without_vlm():
    processor = SkillProcessor(vikingdb=None)
    config = SimpleNamespace(vlm=SimpleNamespace(is_available=lambda: False))
    skill = {
        "name": "model-less-skill",
        "description": "Runs without a configured VLM.",
        "content": "# Procedure\n\nUse the host harness for reasoning.",
    }

    overview = await processor._generate_overview(skill, config)

    assert overview == skill["content"]
