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
|B1     | GND         | ... | Ground |
|B2     | 10MHz       | O   | 10MHz clock signal |
|B3     | ~10MHz      | O   | 10MHz clock signal (inverted) |
|B4     | E           | O   | 6800-series peripheral device clock |
|B5     | AB1         | I/O | Address bus |
|B6     | AB2         | I/O | Address bus |
|B7     | AB3         | I/O | Address bus |
|B8     | AB4         | I/O | Address bus |
|B9     | AB5         | I/O | Address bus |
|B10    | AB6         | I/O | Address bus |
|B11    | GND         | ... | Ground |
|B12    | AB7         | I/O | Address bus |
|B13    | AB8         | I/O | Address bus |
|B14    | AB9         | I/O | Address bus |
|B15    | AB10        | I/O | Address bus |
|B16    | AB11        | I/O | Address bus |
|B17    | AB12        | I/O | Address bus |
|B18    | AB13        | I/O | Address bus |
|B19    | AB14        | I/O | Address bus |
|B20    | AB15        | I/O | Address bus |
|B21    | GND         | ... | Ground |
|B22    | AB16        | I/O | Address bus |
|B23    | AB17        | I/O | Address bus |
|B24    | AB18        | I/O | Address bus |
|B25    | AB19        | I/O | Address bus |
|B26    | AB20        | I/O | Address bus |
|B27    | AB21        | I/O | Address bus |
|B28    | AB22        | I/O | Address bus |
|B29    | AB23        | I/O | Address bus |
|B30    | IDDIR       | O   | Data bus buffer direction control |
|B31    | ---         | ... | Unused (key?) |
|B32    | HSYNC       | O   | Horizontal sync signal |
|B33    | VSYNC       | O   | Vertical sync signal |
|B34    | ~DONE       | O   | DMA block transfer complete |
|B35    | ~DTC        | I   | DMA data transfer completed |
|B36    | ~EXREQ      | I/O | DMA data transfer request |
|B37    | ~EXACK      | O   | DMA data transfer permission |
|B38    | ~EXPCL      | I/O | DMA general purpose I/O signal |
|B39    | ~EXOWN      | I/O | Bus release operation signal |
|B40    | ~EXNMI      | I   | NMI request signal |
|B41    | GND         | ... | Ground |
|B42    | ~IRQ2-n     | O   | Level 2 interrupt request |
|B43    | ~IRQ4-n     | O   | Level 4 interrupt request |
|B44    | ~IACK2-n    | O   | Level 2 interrupt acknowledge |
|B45    | ~IACK4-n    | O   | Level 4 interrupt acknowledge |
|B46    | ~BR-n       | O   | Bus request |
|B47    | ~BG-n       | O   | Bus ground |
|B48    | ~BGACK      | O   | Bus ground acknowledge |
|B49    | Vcc1        | O   | +5V DC power supply |
|B50    | Vcc1        | O   | +5V DC power supply |


