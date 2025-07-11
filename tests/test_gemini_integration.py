"""Tests for Gemini integration module."""

from unittest.mock import Mock, patch

import pytest

from gemini_mcp.gemini_integration import GeminiIntegration, get_integration


class TestGeminiIntegration:
    """Test cases for GeminiIntegration class."""

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
        assert integration.detect_uncertainty("I'm not sure about this") is True
        assert integration.detect_uncertainty("This might be wrong") is True
        assert integration.detect_uncertainty("Perhaps we should") is True

        # Test certain statements
        assert integration.detect_uncertainty("This is correct") is False
        assert integration.detect_uncertainty("The answer is 42") is False

    def test_detect_uncertainty_disabled(self) -> None:
        """Test uncertainty detection when disabled."""
        config = {"auto_consult": False}
        integration = GeminiIntegration(config)

        assert integration.detect_uncertainty("I'm not sure") is False

    @pytest.mark.asyncio
    async def test_consult_gemini_disabled(self) -> None:
        """Test consultation when integration is disabled."""
        config = {"enabled": False}
        integration = GeminiIntegration(config)

        result = await integration.consult_gemini("test query")

        assert result["status"] == "error"
        assert "disabled" in result["error"]

    @pytest.mark.asyncio
    async def test_rate_limiting(self) -> None:
        """Test rate limiting between consultations."""
        integration = GeminiIntegration({"rate_limit_delay": 0.1})

        # Mock the subprocess call
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout=b"Test response", stderr=b"", returncode=0
            )

            # First consultation
            result1 = await integration.consult_gemini("test1")
            assert result1["status"] == "success"

            # Second consultation should be rate limited
            result2 = await integration.consult_gemini("test2")
            assert result2["status"] == "error"
            assert "rate limit" in result2["error"]

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
