"""Unit tests for MCP component flow reload behavior.

Validates that tool selection persists when navigating away and back to a flow:
- Cold cache (initial load) must NOT be treated as a server change
- Saved tool options and value must be preserved on initial load
- UUID override must only happen on genuine server changes
"""

from typing import Any
from uuid import UUID, uuid4

import pytest
from lfx.base.agents.utils import safe_cache_get, safe_cache_set
from lfx.components.models_and_agents.mcp_component import MCPToolsComponent

from tests.base import ComponentTestBaseWithoutClient


class TestMCPComponentFlowReload(ComponentTestBaseWithoutClient):
    """Tests for tool selection persistence across flow navigation."""

    @pytest.fixture
    def component_class(self):
        return MCPToolsComponent

    @pytest.fixture
    def file_names_mapping(self):
        return []

    @pytest.fixture
    def default_kwargs(self):
        return {
            "mcp_server": {"name": "test_server", "config": {"command": "uvx test-mcp-server"}},
            "tool": "saved_tool",
            "use_cache": False,
        }

    @pytest.fixture
    def saved_flow_build_config(self):
        """Simulates build_config from a saved flow with tool already selected."""
        return {
            "mcp_server": {"value": {"name": "test_server"}},
            "tool": {
                "show": True,
                "options": ["saved_tool", "other_tool"],
                "value": "saved_tool",
                "placeholder": "Select a tool",
            },
            "tool_placeholder": {"tool_mode": False},
            "tools_metadata": {"show": False},
        }

    async def component_setup(self, component_class: type[Any], default_kwargs: dict[str, Any]) -> MCPToolsComponent:
        component_instance = await super().component_setup(component_class, default_kwargs)
        component_instance._user_id = str(uuid4())
        # The shared component cache service is None in unit tests, which turns
        # safe_cache_set/get into silent no-ops — every test then runs with a
        # permanently cold cache and cannot exercise warm-cache branches.
        # Install a dict-backed cache so last_selected_server actually persists.
        from lfx.services.cache.utils import CacheMiss

        cache_dict: dict = {}

        class MockCache:
            def get(self, key):
                return cache_dict.get(key, CacheMiss())

            def set(self, key, value):
                cache_dict[key] = value
                return value

        component_instance._shared_component_cache = MockCache()
        return component_instance

    @pytest.mark.asyncio
    async def test_should_preserve_tool_options_when_cache_is_cold(
        self, component_class, default_kwargs, saved_flow_build_config
    ):
        """Cold cache on initial flow load must not clear saved tool options.

        Bug: navigating away and back to a flow clears tool.options because the
        backend treats cold cache (_last_selected_server="") as a server change.
        """
        # Arrange — ensure cold cache (no previous server selection)
        component = await self.component_setup(component_class, default_kwargs)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "")
        build_config = saved_flow_build_config.copy()
        server_value = {"name": "test_server"}

        # Act — simulate initial load (cold cache, no last_selected_server)
        updated_config = await component.update_build_config(build_config, server_value, "mcp_server")

        # Assert — saved options must be preserved
        assert updated_config["tool"]["options"] == ["saved_tool", "other_tool"]
        assert updated_config["tool"]["show"] is True

    @pytest.mark.asyncio
    async def test_should_preserve_tool_value_when_cache_is_cold(
        self, component_class, default_kwargs, saved_flow_build_config
    ):
        """Cold cache on initial flow load must not override saved tool value with UUID."""
        # Arrange — ensure cold cache
        component = await self.component_setup(component_class, default_kwargs)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "")
        build_config = saved_flow_build_config.copy()
        server_value = {"name": "test_server"}

        # Act
        updated_config = await component.update_build_config(build_config, server_value, "mcp_server")

        # Assert — value must remain the saved tool name, not a UUID
        tool_value = updated_config["tool"]["value"]
        assert tool_value == "saved_tool"
        assert not isinstance(tool_value, UUID)

    @pytest.mark.asyncio
    async def test_should_override_tool_value_with_uuid_when_server_genuinely_changes(
        self, component_class, default_kwargs, saved_flow_build_config
    ):
        """When user switches to a different server, tool value must be reset."""
        # Arrange
        component = await self.component_setup(component_class, default_kwargs)
        build_config = saved_flow_build_config.copy()

        # Simulate previous server was set (warm cache)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "old_server")

        new_server_value = {"name": "new_server"}

        # Act
        updated_config = await component.update_build_config(build_config, new_server_value, "mcp_server")

        # Assert — value must be a UUID (forced refresh)
        assert isinstance(updated_config["tool"]["value"], UUID)

    @pytest.mark.asyncio
    async def test_should_set_last_selected_server_in_cache_on_initial_load(
        self, component_class, default_kwargs, saved_flow_build_config
    ):
        """Initial load must populate the cache with the current server name."""
        # Arrange — ensure cold cache
        component = await self.component_setup(component_class, default_kwargs)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "")
        build_config = saved_flow_build_config.copy()
        server_value = {"name": "test_server"}

        # Act
        await component.update_build_config(build_config, server_value, "mcp_server")

        # Assert
        cached_server = safe_cache_get(component._shared_component_cache, "last_selected_server", "")
        assert cached_server == "test_server"

    @pytest.mark.asyncio
    async def test_should_clear_tool_options_when_server_genuinely_changes(
        self, component_class, default_kwargs, saved_flow_build_config
    ):
        """When user switches server, old tool options must be cleared."""
        # Arrange
        component = await self.component_setup(component_class, default_kwargs)
        build_config = saved_flow_build_config.copy()

        # Simulate previous server was set (warm cache)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "old_server")

        new_server_value = {"name": "new_server"}

        # Act
        updated_config = await component.update_build_config(build_config, new_server_value, "mcp_server")

        # Assert — options must be cleared (new server has different tools)
        assert updated_config["tool"]["options"] == []
        # The placeholder depends on how the server lookup fails:
        # - file-based config source: user lookup errors -> "Error on MCP Server"
        # - agent_platform source: clean "server not found" early return keeps
        #   the default "Select a tool" placeholder set before the fetch.
        assert updated_config["tool"]["placeholder"] in (
            "Error on MCP Server",
            "Timeout on MCP server",
            "Select a tool",
        )

    @pytest.fixture
    def saved_flow_build_config_with_schema_input(self):
        """Simulates build_config from a saved flow where a tool with schema inputs is selected."""
        return {
            "mcp_server": {"value": {"name": "test_server"}},
            "tool": {
                "show": True,
                "options": ["saved_tool", "other_tool"],
                "value": "saved_tool",
                "placeholder": "Select a tool",
            },
            "tool_placeholder": {"tool_mode": False},
            "tools_metadata": {"show": False},
            "use_cache": {"value": False},
            # Schema inputs of the selected tool (e.g. base64_encode's "text" param)
            "text": {"value": "hello world", "show": True, "display_name": "文本"},
        }

    @pytest.mark.asyncio
    async def test_should_preserve_schema_inputs_on_flow_reload_with_warm_cache(
        self, component_class, default_kwargs, saved_flow_build_config_with_schema_input
    ):
        """Flow reload (same server, warm cache, use_cache=False) must keep tool schema inputs.

        Bug: re-opening a flow removed the selected tool's parameter fields (e.g.
        the "文本" input of base64_encode) because the mcp_server branch dropped
        non-default keys whenever use_cache was disabled, even though the user
        never switched servers.
        """
        # Arrange — warm cache: backend saw this server in a previous session
        component = await self.component_setup(component_class, default_kwargs)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "test_server")
        build_config = saved_flow_build_config_with_schema_input.copy()
        server_value = {"name": "test_server"}

        # Act — simulate the mount-time mcp_server update
        updated_config = await component.update_build_config(build_config, server_value, "mcp_server")

        # Assert — the schema input must survive with its saved value
        assert "text" in updated_config
        assert updated_config["text"]["value"] == "hello world"
        assert updated_config["tool"]["value"] == "saved_tool"

    @pytest.mark.asyncio
    async def test_should_clear_schema_inputs_when_server_genuinely_changes(
        self, component_class, default_kwargs, saved_flow_build_config_with_schema_input
    ):
        """When the user switches servers, the old tool's schema inputs must be removed."""
        # Arrange — warm cache with a different server
        component = await self.component_setup(component_class, default_kwargs)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "old_server")
        build_config = saved_flow_build_config_with_schema_input.copy()

        # Act
        updated_config = await component.update_build_config(build_config, {"name": "new_server"}, "mcp_server")

        # Assert — old tool's schema inputs are gone
        assert "text" not in updated_config

    @pytest.mark.asyncio
    async def test_should_tolerate_missing_tools_metadata_key(
        self, component_class, default_kwargs, saved_flow_build_config_with_schema_input
    ):
        """Non-tool-mode templates have no tools_metadata key; updates must not crash.

        Bug: update_build_config accessed build_config["tools_metadata"]["show"]
        directly, raising KeyError for non-tool-mode saved templates and failing
        the whole request with a 400.
        """
        # Arrange — warm cache, same server
        component = await self.component_setup(component_class, default_kwargs)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "test_server")
        build_config = saved_flow_build_config_with_schema_input.copy()
        del build_config["tools_metadata"]

        # Act — must not raise
        updated_config = await component.update_build_config(build_config, {"name": "test_server"}, "mcp_server")

        # Assert — template still functional, schema input preserved
        assert updated_config["tool"]["value"] == "saved_tool"
        assert "text" in updated_config

    # ---------------------------------------------------------------------------
    # Self-heal: flows saved while the reload bug was active lost the selected
    # tool's schema inputs (e.g. base64_encode's "text") but kept tool.value.
    # Reloading such a flow must regenerate the missing parameter fields.
    # ---------------------------------------------------------------------------

    @pytest.fixture
    def fake_tool(self):
        """A StructuredTool stand-in whose args_schema declares a "text" input."""
        from pydantic import BaseModel

        class FakeToolArgs(BaseModel):
            text: str

        class FakeTool:
            name = "saved_tool"
            args_schema = FakeToolArgs

        return FakeTool()

    def _mock_tool_fetch(self, component, fake_tool):
        """Make update_tool_list return the fake tool without touching the network."""
        from unittest.mock import AsyncMock

        component.update_tool_list = AsyncMock(return_value=([fake_tool], {"name": "test_server", "config": {}}))

    @pytest.mark.asyncio
    async def test_should_regenerate_missing_schema_inputs_on_reload(self, component_class, default_kwargs, fake_tool):
        """A saved flow that lost the tool's schema inputs must get them back on reload."""
        # Arrange — warm cache, same server; template WITHOUT the text input
        component = await self.component_setup(component_class, default_kwargs)
        self._mock_tool_fetch(component, fake_tool)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "test_server")
        build_config = {
            "mcp_server": {"value": {"name": "test_server"}},
            "tool": {
                "show": True,
                "options": ["saved_tool"],
                "value": "saved_tool",
                "placeholder": "Select a tool",
            },
            "tool_placeholder": {"tool_mode": False},
            "tools_metadata": {"show": False},
            "use_cache": {"value": False},
        }

        # Act
        updated_config = await component.update_build_config(build_config, {"name": "test_server"}, "mcp_server")

        # Assert — the schema input was regenerated
        assert "text" in updated_config
        assert updated_config["tool"]["value"] == "saved_tool"

    @pytest.mark.asyncio
    async def test_should_keep_schema_input_values_through_self_heal(
        self, component_class, default_kwargs, saved_flow_build_config_with_schema_input, fake_tool
    ):
        """Self-heal must not clobber existing schema input values."""
        # Arrange — warm cache, same server; template WITH the text input and a value
        component = await self.component_setup(component_class, default_kwargs)
        self._mock_tool_fetch(component, fake_tool)
        safe_cache_set(component._shared_component_cache, "last_selected_server", "test_server")
        build_config = saved_flow_build_config_with_schema_input.copy()

        # Act
        updated_config = await component.update_build_config(build_config, {"name": "test_server"}, "mcp_server")

        # Assert
        assert "text" in updated_config
        assert updated_config["text"]["value"] == "hello world"

    @pytest.mark.asyncio
    async def test_should_leave_template_untouched_when_tool_missing_from_list(self, component_class, default_kwargs):
        """If the saved tool no longer exists on the server, keep the template as saved."""
        from unittest.mock import AsyncMock

        from pydantic import BaseModel

        class OtherToolArgs(BaseModel):
            other: str

        class OtherTool:
            name = "other_tool"
            args_schema = OtherToolArgs

        # Arrange — warm cache, same server; server only offers a different tool
        component = await self.component_setup(component_class, default_kwargs)
        component.update_tool_list = AsyncMock(return_value=([OtherTool()], {"name": "test_server", "config": {}}))
        safe_cache_set(component._shared_component_cache, "last_selected_server", "test_server")
        build_config = {
            "mcp_server": {"value": {"name": "test_server"}},
            "tool": {
                "show": True,
                "options": ["saved_tool"],
                "value": "saved_tool",
                "placeholder": "Select a tool",
            },
            "tool_placeholder": {"tool_mode": False},
            "tools_metadata": {"show": False},
            "use_cache": {"value": False},
        }

        # Act
        updated_config = await component.update_build_config(build_config, {"name": "test_server"}, "mcp_server")

        # Assert — no schema inputs injected, selection untouched
        assert "text" not in updated_config
        assert "other" not in updated_config
        assert updated_config["tool"]["value"] == "saved_tool"
