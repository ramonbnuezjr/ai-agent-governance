"""Hardware abstraction; GPIO when HARDWARE_ENABLED=true on Pi."""

from src.hardware.gpio import GPIOAdapter

__all__ = ["GPIOAdapter"]
