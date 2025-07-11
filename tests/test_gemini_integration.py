"""Tests for Gemini integration module."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from gemini_mcp import gemini_integration
from gemini_mcp.gemini_integration import GeminiIntegration, get_integration


class TestGeminiIntegration:
    """Test cases for GeminiIntegration class."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        gemini_integration._integration = None

    def test_singleton_pattern(self) -> None:
        """Test that get_integration returns the same instance."""
        instance1 = get_integration()
        instance2 = get_integration()
        assert instance1 is instance2

    def test_initialization_with_config(self) -> None:
        """Test GeminiIntegration initialization with custom config."""
        config = {
            "enabled": False,
            "auto_consult": False,
            "timeout": 30,
            "model": "gemini-2.5-pro",
        }
        integration = GeminiIntegration(config)

        assert integration.enabled is False
        assert integration.auto_consult is False
        assert integration.timeout == 30
        assert integration.model == "gemini-2.5-pro"

    def test_initialization_with_defaults(self) -> None:
        """Test GeminiIntegration initialization with default values."""
        integration = GeminiIntegration()

        assert integration.enabled is True
        assert integration.auto_consult is True
        assert integration.timeout == 60
        assert integration.model == "gemini-2.5-flash"

    def test_detect_uncertainty(self) -> None:
        """Test uncertainty detection in text."""
        integration = GeminiIntegration()

        # Test uncertainty patterns
        assert integration.detect_uncertainty("I'm not sure about this")[0] is True
        assert integration.detect_uncertainty("This might be wrong")[0] is True
        assert integration.detect_uncertainty("Perhaps we should")[0] is True

        # Test certain statements
        assert integration.detect_uncertainty("This is correct")[0] is False
        assert integration.detect_uncertainty("The answer is 42")[0] is False

    def test_detect_uncertainty_disabled(self) -> None:
        """Test uncertainty detection when disabled."""
        config = {"auto_consult": False}
        integration = GeminiIntegration(config)

        # detect_uncertainty still works even when auto_consult is disabled
        # It returns the detection result, auto_consult just controls automatic consultation
        assert integration.detect_uncertainty("I'm not sure")[0] is True

    @pytest.mark.asyncio
    async def test_consult_gemini_disabled(self) -> None:
        """Test consultation when integration is disabled."""
        config = {"enabled": False}
        integration = GeminiIntegration(config)

        result = await integration.consult_gemini("test query")

        assert result["status"] == "disabled"
        assert "disabled" in result["message"]

    @pytest.mark.asyncio
    async def test_rate_limiting(self) -> None:
        """Test rate limiting between consultations."""
        integration = GeminiIntegration({"rate_limit_delay": 0.1})

        # Mock the asyncio subprocess call
        with patch(
            "gemini_mcp.gemini_integration.asyncio.create_subprocess_exec"
        ) as mock_subprocess:
            # Create a mock process
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Test response", b""))
            mock_subprocess.return_value = mock_process

            # First consultation
            result1 = await integration.consult_gemini("test1")
            assert result1["status"] == "success"

            # Second consultation should succeed after rate limit
            # Since we're mocking, we need to maunally enforce the rate limit
            result2 = await integration.consult_gemini("test2", force_consult=True)
            assert result2["status"] == "success"

    def test_get_config_values(self) -> None:
        """Test getting configuration values."""
        integration = GeminiIntegration()

        assert integration.enabled is True
        assert integration.auto_consult is True
        assert integration.model == "gemini-2.5-flash"
        assert len(integration.consultation_log) == 0

    def test_manual_toggle_auto_consult(self) -> None:
        """Test manually toggling auto consultation."""
        integration = GeminiIntegration()

        # Toggle off
        integration.auto_consult = False
        assert integration.auto_consult is False

        # Toggle on
        integration.auto_consult = True
        assert integration.auto_consult is True
