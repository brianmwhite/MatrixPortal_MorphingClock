## 1. Button Input Setup

- [x] 1.1 Identify the correct MatrixPortal `up` and `down` button pin constants and initialize them as digital inputs in `code.py`
- [x] 1.2 Add edge-triggered button state tracking so each press is handled once until release

## 2. RTC Adjustment

- [x] 2.1 Add a helper that reads the current DS3231 datetime, applies a plus-or-minus one hour adjustment, and writes the updated datetime back to the RTC
- [x] 2.2 Ensure the adjustment logic preserves correct day rollover when incrementing from 23:xx:xx and decrementing from 00:xx:xx
- [x] 2.3 Call the RTC adjustment helper from the `up` and `down` button handlers without changing the existing display, temperature, humidity, or brightness behavior

## 3. Validation

- [x] 3.1 Verify on hardware that one `up` press advances the clock by one hour and one `down` press moves it back by one hour
- [x] 3.2 Verify that holding either button does not repeat adjustments until the button is released and pressed again
- [x] 3.3 Verify that midnight crossings update both hour and date correctly in both directions
