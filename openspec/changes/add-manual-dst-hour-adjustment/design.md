## Context

The project is a CircuitPython clock application for MatrixPortal hardware. The current runtime in `code.py` owns RTC setup, display updates, ambient brightness adjustment, and sensor reads in a single loop. The MatrixPortal includes `up` and `down` buttons that are currently unused, and the DS3231 RTC is the active time source for the device.

This change adds a small, device-local control path for daylight saving time correction. The desired behavior is one hour of RTC adjustment per distinct button press, with no other change to display, sensor, or brightness features.

## Goals / Non-Goals

**Goals:**
- Allow the user to increment the current RTC time by one hour with the `up` button.
- Allow the user to decrement the current RTC time by one hour with the `down` button.
- Preserve correct calendar date when the hour change crosses midnight in either direction.
- Prevent repeated adjustments while a button remains held.
- Fit into the existing `code.py` loop with minimal disruption.

**Non-Goals:**
- Redesign the main clock loop or split the application into additional modules.
- Add UI feedback beyond the display naturally reflecting the new time after RTC adjustment.
- Support minute-level or second-level manual correction.
- Introduce automatic DST detection or timezone rules.

## Decisions

### Use button presses to write directly to the DS3231 RTC
The implementation should update the RTC itself rather than maintaining a display-only offset. This keeps the clock state authoritative and persistent across redraws and reboots.

Alternative considered:
- Maintain an in-memory display offset. Rejected because it diverges from the RTC, complicates date changes at midnight, and creates surprising behavior after restart.

### Treat adjustments as edge-triggered events with debounce
Each button press should produce exactly one hour change. The loop should detect a press transition rather than continuously adjusting while the button remains active. A small debounce window or release-based re-arming is sufficient for this use case.

Alternative considered:
- Repeat while held. Rejected because the primary use case is DST correction, where accidental multiple-hour changes would be more harmful than helpful.

### Perform datetime arithmetic before writing the updated RTC value
Hour adjustment should be applied to the full current datetime, not just the `tm_hour` field, so day/month/year rollover remains correct when crossing midnight.

Alternative considered:
- Clamp or wrap only the hour field. Rejected because `23 -> 00` and `00 -> 23` also require a date change.

### Keep button handling inside `code.py`
The existing application is intentionally small and centralized. Adding a small input polling path in the current loop is lower risk than introducing new abstraction solely for two buttons.

Alternative considered:
- Create a dedicated input controller module. Rejected for now because it adds structure without reducing meaningful complexity for this narrow feature.

## Risks / Trade-offs

- Button pin naming may vary by MatrixPortal hardware or library version -> Confirm the correct CircuitPython board constants during implementation and keep the integration localized so pin fixes are easy.
- Debounce that is too permissive may still allow double-adjustment on noisy presses -> Prefer simple edge detection with explicit re-arming on release.
- Writing the RTC immediately on press means accidental presses change real device time -> This is acceptable for the DST-focused use case, and one-hour-per-press limits blast radius.
- Polling buttons in the main loop slightly increases loop responsibilities -> The added work is minimal compared with existing display and sensor operations.
