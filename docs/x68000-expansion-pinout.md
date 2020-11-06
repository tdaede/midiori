# X68000 Expansion Pinout
As described by [_Outside X68000_](https://archive.org/stream/OutsideX680001993/Outside_X68000_1993#page/n51/mode/2up). Translated by Google.

| Pin # | Description | I/O | Comment |
|-------|-------------|-----|---------|
|A1     | GND         | ... | Ground  |
|A2     | 20MHz       | O   | 20MHz clock |
|A3     | GND         | ... | Ground  |
|A4     | DB0         | I/O | Data bus |
|A5     | DB1         | I/O | Data bus |
|A6     | DB2         | I/O | Data bus |
|A7     | DB3         | I/O | Data bus |
|A8     | DB4         | I/O | Data bus |
|A9     | DB5         | I/O | Data bus |
|A10    | DB6         | I/O | Data bus |
|A11    | GND         | ... | Ground  |
|A12    | DB7         | I/O | Data bus |
|A13    | DB8         | I/O | Data bus |
|A14    | DB9         | I/O | Data bus |
|A15    | DB10        | I/O | Data bus |
|A16    | DB11        | I/O | Data bus |
|A17    | DB12        | I/O | Data bus |
|A18    | DB13        | I/O | Data bus |
|A19    | DB14        | I/O | Data bus |
|A20    | DB15        | I/O | Data bus |
|A21    | GND         | ... | Ground   |
|A22    | +12V        | O   | +12V DC power supply |
|A23    | +12V        | O   | +12V DC power supply |
|A24    | FC0         | I/O | Function code |
|A25    | FC1         | I/O | Function code |
|A26    | FC2         | I/O | Function code |
|A27    | ~AS         | I/O | Address strobe |
|A28    | ~LDS        | I/O | Lower data strobe |
|A29    | ~UDS        | I/O | Upper data strobe |
|A30    | R/~W        | I/O | Read/write ("L" = Write) |
|A31    | ---         | ... | Unused (key?) |
|A32    | -12V        | O   | -12V DC power supply |
|A33    | -12V        | O   | -12V DC power supply |
|A34    | ~VMA        | O   | Address bus enabled |
|A35    | -EXVPA      | I   | 6800-series peripheral device access signal |
|A36    | ~DTACK      | I/O | Data transfer completed |
|A37    | ~EXRESET    | O   | External reset |
|A38    | ~HALT       | I/O | CPU halt request |
|A39    | ~EXBERR     | I/O | Bus error |
|A40    | ~EXPWON     | I   | Soft-power ON request |
|A41    | GND         | ... | Ground |
|A42    | Vcc2        | O   | +5V standby power (always on) |
|A43    | Vcc2        | O   | +5V standby power (always on) |
|A44    | SELEN       | O   | Row/column address switching |
|A45    | CASRDEN     | O   | Main memory CAS signal (when reading) |
|A46    | CASWRL      | O   | CAS signal for writing lower data |
|A47    | CASWRU      | O   | CAS signal for writing upper data |
|A48    | INH2        | O   | Refresh cycle display signal |
|A49    | Vcc1        | O   | +5V DC power supply |
|A50    | Vcc1        | O   | +5V DC power supply |
