"""Tests for built-in component code sync in the update endpoints.

Flows persist the component source at save time; the custom_component_update
endpoint executes that frozen snapshot. _sync_builtin_component_code replaces
snapshots of registered built-in components with the live implementation so
fixes to built-in components reach existing flows.
"""

import langflow.api.v1.endpoints as endpoints_module
import pytest
from langflow.api.v1.endpoints import _sync_builtin_component_code
from lfx.interface.components import component_cache

SNAPSHOT_HEADER = "from lfx.custom.custom_component.component import Component\n\n\n"


@pytest.fixture(autouse=True)
def reset_code_index(monkeypatch):
    """Each test starts with a cold class-name index."""
    monkeypatch.setattr(endpoints_module, "_builtin_code_by_class", None)


@pytest.fixture
def registry(monkeypatch):
    """Patch the component cache with a small fake registry."""
    fake_registry = {
        "models_and_agents": {
            "MCPTools": {
                "template": {
                    "code": {
                        "value": SNAPSHOT_HEADER + "class MCPToolsComponent(ComponentWithCache):\n    CURRENT = True\n"
                    }
                }
            }
        }
    }
    monkeypatch.setattr(component_cache, "all_types_dict", fake_registry)
    return fake_registry


@pytest.mark.usefixtures("registry")
def test_stale_snapshot_replaced_with_current_implementation():
    stale = SNAPSHOT_HEADER + "class MCPToolsComponent(ComponentWithCache):\n    OLD = True\n"

    synced = _sync_builtin_component_code(stale)

    assert "CURRENT = True" in synced
    assert "OLD = True" not in synced


def test_matching_code_returned_unchanged(registry):
    current = registry["models_and_agents"]["MCPTools"]["template"]["code"]["value"]

    assert _sync_builtin_component_code(current) == current


@pytest.mark.usefixtures("registry")
def test_unknown_class_returned_unchanged():
    custom = SNAPSHOT_HEADER + "class MyCustomThing(Component):\n    pass\n"

    assert _sync_builtin_component_code(custom) == custom


@pytest.mark.usefixtures("registry")
def test_empty_code_returned_unchanged():
    assert _sync_builtin_component_code("") == ""


def test_unpopulated_registry_returns_code_unchanged(monkeypatch):
    monkeypatch.setattr(component_cache, "all_types_dict", None)
    stale = SNAPSHOT_HEADER + "class MCPToolsComponent(ComponentWithCache):\n    OLD = True\n"

    assert _sync_builtin_component_code(stale) == stale


def test_never_raises_on_registry_errors(monkeypatch):
    boom_error = RuntimeError("boom")

    class Boom:
        def values(self):
            raise boom_error

    monkeypatch.setattr(component_cache, "all_types_dict", {"cat": Boom()})
    stale = SNAPSHOT_HEADER + "class MCPToolsComponent(ComponentWithCache):\n    OLD = True\n"

    assert _sync_builtin_component_code(stale) == stale
