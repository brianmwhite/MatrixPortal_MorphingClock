## ADDED Requirements

### Requirement: User can increment the RTC hour with the up button
The system SHALL increase the DS3231 RTC by exactly one hour when the user performs a distinct press of the MatrixPortal `up` button.

#### Scenario: Increment hour on press
- **WHEN** the user presses and releases the `up` button once
- **THEN** the DS3231 RTC time is advanced by one hour

#### Scenario: Preserve date rollover when incrementing across midnight
- **WHEN** the RTC time is 23:xx:xx and the user presses the `up` button once
- **THEN** the RTC time becomes 00:xx:xx on the next calendar day

### Requirement: User can decrement the RTC hour with the down button
The system SHALL decrease the DS3231 RTC by exactly one hour when the user performs a distinct press of the MatrixPortal `down` button.

#### Scenario: Decrement hour on press
- **WHEN** the user presses and releases the `down` button once
- **THEN** the DS3231 RTC time is moved back by one hour

#### Scenario: Preserve date rollover when decrementing across midnight
- **WHEN** the RTC time is 00:xx:xx and the user presses the `down` button once
- **THEN** the RTC time becomes 23:xx:xx on the previous calendar day

### Requirement: Held buttons do not repeat hour adjustments
The system SHALL apply at most one hour adjustment for each distinct button press, even if the button remains held across multiple loop iterations.

#### Scenario: Hold up button
- **WHEN** the user presses and holds the `up` button
- **THEN** the RTC advances by only one hour until the button is released and pressed again

#### Scenario: Hold down button
- **WHEN** the user presses and holds the `down` button
- **THEN** the RTC moves back by only one hour until the button is released and pressed again
