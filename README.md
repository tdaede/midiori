![](docs/midiori_packing_label.svg?sanitize=true)

# Installation

1. Remove a cover plate from a free x68000 expansion slot.
2. Slide card into expansion plate until it seats. It will take some force.
3. Install 3d printed cover plate.
4. Attach OUT connector to MIDI in of your synthesizer.
5. (optional) Run LINE OUT from the x68000 to the LINE IN of your synthesizer's internal mixer.

# Compatibility

A list of tested games is available [here](docs/GAMES.md).

# Changelog

See [here](docs/CHANGELOG.md).

# Differences from midiori v1

- MIDI IN and THRU ports are not implemented.
- FIFO-Rx and FIFO-IRx are not implemented.
- FIFO-ITx start/stop/clock messages are not implemented.
- SYNC and CLICK are not implemented.
- Sequencer is not implemented.
- GPIO is not implemented.
- Address is locked to 0xeafa00.
- IRQ is locked to slot+2.
- Baud rate is locked to 31250 bps, 8n1.
- 32-byte, null terminated version string, readable by writing
  the index (0-31) to 0xF4 and reading the current byte from 0xF5.
- 68k bus is implemented natively and timings are generally faster.
