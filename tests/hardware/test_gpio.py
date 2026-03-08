"""Tests for GPIO adapter."""

import pytest

from src.hardware.gpio import GPIOAdapter


def test_gpio_disabled_setup_no_op() -> None:
    """When disabled, setup() does not raise and has no effect."""
    adapter = GPIOAdapter(enabled=False)
    adapter.setup(17, "out")
    adapter.setup(27, "in")


def test_gpio_disabled_output_no_op() -> None:
    """When disabled, output() does not raise."""
    adapter = GPIOAdapter(enabled=False)
    adapter.output(17, True)
    adapter.output(17, False)


def test_gpio_disabled_input_returns_false() -> None:
    """When disabled, input() returns False."""
    adapter = GPIOAdapter(enabled=False)
    assert adapter.input(17) is False


def test_gpio_disabled_cleanup_no_op() -> None:
    """When disabled, cleanup() does not raise."""
    adapter = GPIOAdapter(enabled=False)
    adapter.cleanup()


def test_gpio_enabled_accepts_mode() -> None:
    """Adapter accepts BCM or BOARD mode (no-op when enabled but not on Pi)."""
    adapter = GPIOAdapter(enabled=True, mode="BOARD")
    adapter.setup(11, "out")
    adapter.cleanup()
