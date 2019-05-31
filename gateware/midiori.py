#!/usr/bin/env python3

from migen import *
from migen.fhdl import verilog
from migen.genlib.fifo import *
import midiori_platform

base_addr = Constant(0xeafa00 >> 1)

def _divisor(freq_in, freq_out, max_ppm=None):
    divisor = freq_in // freq_out
    if divisor <= 0:
        raise ArgumentError("output frequency is too high")

    ppm = 1000000 * ((freq_in / divisor) - freq_out) / freq_out
    if max_ppm is not None and ppm > max_ppm:
        raise ArgumentError("output frequency deviation is too high")

    return divisor


class UART(Module):
    def __init__(self, tx, clk_freq, baud_rate):
        self.tx_data = Signal(8)
        self.tx_ready = Signal()
        self.tx_ack = Signal()

        divisor = _divisor(freq_in=clk_freq, freq_out=baud_rate, max_ppm=50000)

        tx_counter = Signal(max=divisor)
        self.tx_strobe = tx_strobe = Signal()
        self.comb += tx_strobe.eq(tx_counter == 0)
        self.sync += \
            If(tx_counter == 0,
                tx_counter.eq(divisor - 1)
            ).Else(
                tx_counter.eq(tx_counter - 1)
            )

        self.tx_bitno = tx_bitno = Signal(3)
        self.tx_latch = tx_latch = Signal(8)
        self.submodules.tx_fsm = FSM(reset_state="IDLE")
        self.tx_fsm.act("IDLE",
            self.tx_ack.eq(1),
            If(self.tx_ready,
                NextValue(tx_counter, divisor - 1),
                NextValue(tx_latch, self.tx_data),
                NextState("START")
            ).Else(
                NextValue(tx, 1)
            )
        )
        self.tx_fsm.act("START",
            If(self.tx_strobe,
                NextValue(tx, 0),
                NextState("DATA")
            )
        )
        self.tx_fsm.act("DATA",
            If(self.tx_strobe,
                NextValue(tx, tx_latch[0]),
                NextValue(tx_latch, Cat(tx_latch[1:8], 0)),
                NextValue(tx_bitno, tx_bitno + 1),
                If(self.tx_bitno == 7,
                    NextState("STOP")
                )
            )
        )
        self.tx_fsm.act("STOP",
            If(self.tx_strobe,
                NextValue(tx, 1),
                NextState("IDLE")
            )
        )

class Midiori(Module):
    def __init__(self):
        self.tx = Signal()
        self.uart = UART(self.tx, 16000000, 31250)
        self.submodules += self.uart
        self.fifo = SyncFIFO(8, 16)
        self.submodules += self.fifo
        self.tx_running = Signal()
        self.comb += self.uart.tx_ready.eq(self.fifo.readable)
        self.comb += self.fifo.re.eq(self.uart.tx_ack)
        self.comb += self.uart.tx_data.eq(self.fifo.dout)
        self.addr = Signal(23)
        self._as = Signal()
        self._lds = Signal()
        self._dtready = Signal()
        self._rw = Signal()
        self.data = TSTriple(8)
        self.group_num = Signal(4)
        self.addr_num = Signal(3)
        self.register_num = Signal(8)

        # internal read-only registers

        self.txemp = Signal()
        self.comb += self.txemp.eq(self.fifo.level == 0)
        #self.comb += self.txemp.eq(1)
        self.txrdy = Signal()
        #self.comb += self.txrdy.eq(self.fifo.writable)
        self.comb += self.txrdy.eq(1)
        self.txidl = Signal()
        self.comb += self.txidl.eq(1)
        self.txbsy = Signal()
        self.comb += self.txbsy.eq(0)
        self.tsr = Signal(8)
        self.comb += self.tsr.eq(Cat(self.txbsy,0,self.txidl,0,0,0,self.txrdy,self.txemp))

        # irq controller
        self.isr = Signal(8, reset=0x10) #rx break detected at start

        # irq sets
        self.previous_empty = Signal()
        self.sync += If((self.previous_empty == 0) & (self.txemp == 1),
                        self.isr[6].eq(1)
        )
        self.sync += self.previous_empty.eq(self.txemp)

        self.xltr_oe = Signal()
        self.comb += self.addr_num.eq(self.addr[0:3])
        self.comb += self.register_num.eq(Cat(self.addr_num, 0, self.group_num))
        fsm = FSM(reset_state="IDLE")
        self.submodules += fsm
        fsm.act("IDLE",
                self._dtready.eq(1),
                self.xltr_oe.eq(1),
                If((self._as == 0) &
                   (self.addr[3:24] == base_addr[3:24]),
                   # enable xltr early
                   self.xltr_oe.eq(0),
                   If(self._lds == 0,
                       If((self._rw == 1),
                           NextState("RDATA"),
                       ).Else(
                           NextState("WDATA"),
                       )
                   )
                )
        )
        fsm.act("RDATA",
                self._dtready.eq(0),
                If(self.addr_num == 0,
                   # irq vector register
                   self.data.o.eq(0x10)
                ).Elif(self.addr_num == 2,
                    self.data.o.eq(0x90)
                ).Else(
                    If(self.register_num == 0x34,
                       self.data.o.eq(0x04)
                    ).Elif(self.register_num == 0x36,
                           self.data.o.eq(0x00)
                    ).Elif(self.register_num == 0x54,
                           self.data.o.eq(self.tsr)
                    ).Elif(self.register_num == 0x64,
                           self.data.o.eq(0xa0)
                    ).Elif(self.register_num == 0x74,
                           self.data.o.eq(0x00)
                    ).Elif(self.register_num == 0x96,
                           self.data.o.eq(0xFF)
                    )
                ),
                If(self._as == 1,
                   NextState("IDLE")
                )
        )
        fsm.act("WDATA",
                self._dtready.eq(0),
                If(self.addr_num == 0x01,
                   NextValue(self.group_num, self.data.i[0:4])
                ).Else(
                    If(self.register_num == 0x56,
                       NextValue(self.fifo.we, 1),
                       NextValue(self.fifo.din, self.data.i),
                       # clear tx empty isr
                       NextValue(self.isr[6], 0)
                    )
                ),
                #only spend one cycle in WDATA
                #so that writes only happen once
                NextState("WWAIT")
        )
        fsm.act("WWAIT",
                NextValue(self.fifo.we, 0),
                If(self._as == 1,
                   NextState("IDLE")
                )
        )

def midi_read(m, reg):
    yield m.addr.eq(base_addr+1)
    yield m._as.eq(0)
    yield m._lds.eq(0)
    yield m._rw.eq(0)
    yield m.data.i.eq(reg >> 4)
    while (yield m._dtready == 1):
        yield
    yield m._as.eq(1)
    yield m._lds.eq(1)
    while (yield m._dtready == 0):
        yield
    yield m._rw.eq(1)
    yield m.addr.eq(base_addr+(reg&0x0F))
    yield m._as.eq(0)
    yield m._lds.eq(0)
    while (yield m._dtready == 1):
        yield
    yield m._as.eq(1)
    yield m._lds.eq(1)
    while (yield m._dtready == 0):
        yield

def midi_write(m, reg, value):
    yield m.addr.eq(base_addr+1)
    yield m._as.eq(0)
    yield m._lds.eq(0)
    yield m._rw.eq(0)
    yield m.data.i.eq(reg >> 4)
    while (yield m._dtready == 1):
        yield
    yield m._as.eq(1)
    yield m._lds.eq(1)
    while (yield m._dtready == 0):
        yield
    yield m._rw.eq(0)
    yield m.data.i.eq(value)
    yield m.addr.eq(base_addr+(reg&0x0F))
    yield m._as.eq(0)
    yield m._lds.eq(0)
    while (yield m._dtready == 1):
        yield
    yield m._as.eq(1)
    yield m._lds.eq(1)
    while (yield m._dtready == 0):
        yield

def midi_wait_empty(m):
    while (yield m.fifo.level > 0):
        yield

def test(m):
    yield m.addr.eq(0)
    yield m._as.eq(1)
    yield m._lds.eq(1)
    yield m._rw.eq(1)
    yield
    yield m.addr.eq(base_addr)
    yield
    yield m._as.eq(0)
    yield m._lds.eq(0)
    yield
    yield m._as.eq(1)
    yield m._lds.eq(1)
    yield
    yield
    yield from midi_read(m, 0x34)
    yield from midi_read(m, 0x16)
    for i in range(1,17):
        yield from midi_write(m, 0x56, i)
    yield from midi_wait_empty(m)
    for i in range(1, 10000):
        yield

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "sim":
        m = Midiori()
        run_simulation(m, test(m), vcd_name="midiori.vcd")
    else:
        plat = midiori_platform.Platform()
        m = Midiori()
        m.comb += m.addr.eq(plat.request("addr"))
        m.comb += m._as.eq(plat.request("as"))
        m.comb += m._lds.eq(plat.request("lds"))
        m.comb += m._rw.eq(plat.request("rw"))
        m.comb += plat.request("dtack").eq(m._dtready)
        m.specials += m.data.get_tristate(plat.request("data"))
        m.comb += plat.request("xltr_oe").eq(m.xltr_oe)
        m.comb += m.data.oe.eq(~plat.request("iddir"))
        m.comb += plat.request("tx").eq(m.tx)
        plat.build(m)
