"""GPIO abstraction; no-op when HARDWARE_ENABLED=false or not on Raspberry Pi."""

import logging
from typing import Literal

logger = logging.getLogger(__name__)

PinMode = Literal["BCM", "BOARD"]


class GPIOAdapter:
    """
    GPIO abstraction. When hardware is disabled (default), all methods are no-ops.
    When enabled on Pi, would delegate to RPi.GPIO or adafruit-blinka.
    """

    def __init__(self, enabled: bool, mode: PinMode = "BCM") -> None:
        self._enabled = enabled
        self._mode = mode
        if not enabled:
            logger.debug("GPIO disabled; all operations are no-ops.")

    def setup(self, channel: int, direction: Literal["in", "out"]) -> None:
        """Configure a channel as input or output. No-op when disabled."""
        if not self._enabled:
            return
        # Would call RPi.GPIO.setup(channel, ...) here
        logger.debug("GPIO setup channel=%s direction=%s (hardware disabled)", channel, direction)

    def output(self, channel: int, value: bool) -> None:
        """Set output channel high (True) or low (False). No-op when disabled."""
        if not self._enabled:
            return
        logger.debug("GPIO output channel=%s value=%s (hardware disabled)", channel, value)

    def input(self, channel: int) -> bool:
        """Read input channel. Returns False when disabled."""
        if not self._enabled:
            return False
        logger.debug("GPIO input channel=%s (hardware disabled)", channel)
        return False

    def cleanup(self) -> None:
        """Release GPIO resources. No-op when disabled."""
        if not self._enabled:
            return
        logger.debug("GPIO cleanup (hardware disabled)")
