![](docs/midiori_packing_label.svg?sanitize=true)

# Installation

1. Remove a cover plate from a free x68000 expansion slot.
2. Slide card into expansion plate until it seats. It will take some force.
3. Install 3d printed cover plate.
4. Attach OUT connector to MIDI in of your synthesizer.
5. (optional) Run LINE OUT from the x68000 to the LINE IN of your synthesizer's internal mixer.

# Differences from midiori v1

- MIDI IN and THRU ports are not implemented.
- FIFO-Rx and FIFO-IRx are not implemented.
- FIFO-ITx is not implemented.
- Tx idle detection is not implemented.
- IC is not implemented.
- Midi clock source is not implemented.
- SYNC and CLICK are not implemented.
- Sequencer is not implemented.
- GPIO is not implemented.
- Address is locked to 0xeafa00.
- IRQ is locked to slot+2.
- Baud rate is locked to 31250 bps, 8n1.
- CLKM divider is locked to 1MHz mode.
- 68k bus is implemented natively and timings are generally faster.
