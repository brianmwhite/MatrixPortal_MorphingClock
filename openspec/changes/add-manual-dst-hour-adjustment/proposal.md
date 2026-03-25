## Why

The clock currently depends on external time-setting methods when the hour needs to shift for daylight saving time changes. The MatrixPortal already has unused `up` and `down` buttons, so adding direct hour adjustment on-device makes seasonal time correction faster and less error-prone.

## What Changes

- Add manual hour adjustment using the MatrixPortal `up` and `down` buttons.
- Update the DS3231 RTC when a button is pressed so the clock's source of truth changes, not just the display.
- Apply one hour of adjustment per distinct button press, with debounce to prevent repeated changes while a button is held.
- Handle hour rollover across midnight so the date remains correct when incrementing or decrementing past day boundaries.
- Leave the existing clock display, temperature/humidity display, and brightness behavior unchanged.

## Capabilities

### New Capabilities
- `manual-hour-adjustment`: Allow the device user to change the RTC time by exactly one hour per `up` or `down` button press.

### Modified Capabilities

## Impact

- Affected code: [code.py](/Users/bmw/code/MatrixPortal_MorphingClock/code.py), potentially [timesetter.py](/Users/bmw/code/MatrixPortal_MorphingClock/timesetter.py) only if shared RTC adjustment helpers are introduced during implementation.
- Hardware integration: MatrixPortal button inputs and DS3231 RTC writes.
- Dependencies: existing Adafruit CircuitPython libraries for board pin access and digital input handling.
