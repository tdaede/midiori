#!/usr/bin/env python3


from amaranth import *
from amaranth.lib import io
from amaranth.compat import Module as CompatModule
from amaranth.compat import If, TSTriple, FSM, NextState, NextValue, run_simulation
from amaranth.compat.fhdl import verilog
from amaranth.compat.genlib.fifo import *
from amaranth.compat.genlib.coding import PriorityEncoder
from midiori_platform import *
import subprocess

base_addr = Const(0xeafa00 >> 1)

describe = subprocess.check_output(["git", "describe", "--tags", "--long"]).strip().decode()
version_string = Array(("midiori "+describe+"\x00").encode('shift_jis'))

def _divisor(freq_in, freq_out, max_ppm=None):
    divisor = freq_in // freq_out
    if divisor <= 0:
        raise ArgumentError("output frequency is too high")

    ppm = 1000000 * ((freq_in / divisor) - freq_out) / freq_out
    if max_ppm is not None and ppm > max_ppm:
        raise ArgumentError("output frequency deviation is too high")

    return divisor


class UART(Elaboratable):
    def __init__(self, tx, clk_freq, baud_rate):
        self.tx_data = Signal(8)
        self.tx_ready = Signal()
        self.tx_ack = Signal()
        self.tx = tx

        self.divisor = _divisor(freq_in=clk_freq, freq_out=baud_rate, max_ppm=50000)

        self.tx_counter = Signal(range(0, self.divisor))
        self.tx_strobe = tx_strobe = Signal()

        self.tx_bitno = tx_bitno = Signal(3)
        self.tx_latch = tx_latch = Signal(8)

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.tx_strobe.eq(self.tx_counter == 0)
        with m.If(self.tx_counter == 0):
            m.d.sync += self.tx_counter.eq(self.divisor - 1)
        with m.Else():
            m.d.sync += self.tx_counter.eq(self.tx_counter - 1)

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.tx_ack.eq(1)
                with m.If(self.tx_ready):
                    m.d.sync += self.tx_counter.eq(self.divisor - 1)
                    m.d.sync += self.tx_latch.eq(self.tx_data)
                    m.next = "START"
                with m.Else():
                    m.d.sync += self.tx.eq(1)
            with m.State("START"):
                with m.If(self.tx_strobe):
                    m.d.sync += self.tx.eq(0)
                    m.next = "DATA"
            with m.State("DATA"):
                with m.If(self.tx_strobe):
                    m.d.sync += self.tx.eq(self.tx_latch[0])
                    m.d.sync += self.tx_latch.eq(Cat(self.tx_latch[1:8], 0))
                    m.d.sync += self.tx_bitno.eq(self.tx_bitno + 1)
                    with m.If(self.tx_bitno == 7):
                        m.next = "STOP"
            with m.State("STOP"):
                with m.If(self.tx_strobe):
                    m.d.sync += self.tx.eq(1)
                    m.next = "IDLE"
        return m

class Midiori(Elaboratable):
    def __init__(self):
        # tx uart registers
        self.tx = Signal()
        self.uart_tx = Signal()
        self.uart = UART(self.uart_tx, 16000000, 31250)
        self.brke = Signal()
        self.txe = Signal()
        self.fifo = SyncFIFOBuffered(8, 16)

        self.addr = Signal(23)
        self._irq = Signal(reset=1)
        self._iack = Signal()
        self._as = Signal()
        self._lds = Signal()
        self._dtready = Signal(reset=1)
        self._rw = Signal()
        self.exreset = Signal(reset=1)
        # this type is just being used for Record(i,o,oe)
        self.data = io.Pin(8, "io")
        self.addr_num = Signal(3)
        self.register_num = Signal(8)
        self.version_index = Signal(5)

        # internal read-only registers

        self.txemp = Signal()
        self.txrdy = Signal()
        self.txidl = Signal()
        self.ase = Signal()

        self.txbsy = Signal()
        self.tsr = Signal(8)

        # internal read-write registers
        self.group_num = Signal(4)
        self.ier = Signal(8)
        self.ivo = Signal(3)
        self.ic = Signal()

        # irq controller
        self.isr = Signal(8, reset=0x00)
        self.ivr = Signal(8)
        self.vec = Signal(4)
        self.isr_masked = Signal(8)

        self.previous_empty = Signal()
    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.txemp.eq(self.fifo.level == 0)
        m.d.comb += self.txrdy.eq(self.fifo.w_rdy)
        with m.If(self.brke):
            m.d.comb += self.tx.eq(0)
        with m.Else():
            m.d.comb += self.tx.eq(self.uart_tx)
        m.submodules += self.uart
        m.submodules += self.fifo
        # the itx fifo is described as a 4 deep fifo,
        # but it's really just 4 different types of
        # messages that can be sent
        itx_fifo_fe = Signal()
        itx_fifo_in_progress = Signal()
        m.d.comb += self.uart.tx_ready.eq(self.fifo.r_rdy | itx_fifo_fe)
        with m.If(itx_fifo_in_progress):
            m.d.comb += self.fifo.r_en.eq(0)
        with m.Else():
            m.d.comb += self.fifo.r_en.eq(self.uart.tx_ack)
        with m.If(itx_fifo_fe):
            m.d.comb += self.uart.tx_data.eq(0xfe)
        with m.Else():
            m.d.comb += self.uart.tx_data.eq(self.fifo.r_data)
        with m.If(self.uart.tx_ack & itx_fifo_fe & ~itx_fifo_in_progress):
            m.d.sync += itx_fifo_fe.eq(0)
            m.d.sync += itx_fifo_in_progress.eq(1)
        with m.Elif(self.uart.tx_ack & itx_fifo_in_progress):
            m.d.sync += itx_fifo_in_progress.eq(0)

        txidl_counter = Signal(21)
        with m.If(txidl_counter >= 1280000):
            m.d.sync += txidl_counter.eq(0)
            m.d.sync += self.txidl.eq(1)
            m.d.sync += itx_fifo_fe.eq(self.ase)
        with m.Elif(~self.txemp | ~self.txe):
            m.d.sync += txidl_counter.eq(0)
        with m.Else():
            m.d.sync += txidl_counter.eq(txidl_counter + 1)

        m.d.comb += self.txbsy.eq(0)
        m.d.comb += self.tsr.eq(Cat(self.txbsy,0,self.txidl,0,0,0,self.txrdy,self.txemp))

        #8us clock divider
        midi_divider = Signal(7)
        #all games should set this to 1, but
        #simulate it for completeness
        clkm = Signal()
        m.d.sync += midi_divider.eq(midi_divider-1)
        midi_clk_en = Signal()
        with m.If(clkm):
            m.d.comb += midi_clk_en.eq(midi_divider == 0)
        with m.Else():
            m.d.comb += midi_clk_en.eq(midi_divider[0:6] == 0)

        m.d.comb += self.isr_masked.eq(self.isr & self.ier)
        isr_pe = PriorityEncoder(8)
        m.submodules += isr_pe
        m.d.comb += isr_pe.i.eq(self.isr_masked)
        m.d.comb += self.vec.eq(Cat(isr_pe.o, isr_pe.n))
        m.d.comb += self.ivr.eq(Cat(0,self.vec,self.ivo))
        m.d.comb += self._irq.eq(self.isr_masked == 0)

        # irq sets
        with m.If((self.previous_empty == 0) & (self.txemp == 1)):
            m.d.sync += self.isr[6].eq(1)
        m.d.sync += self.previous_empty.eq(self.txemp)

        #general purpose timer
        gpt_low_byte_cache = Signal(8)
        gpt_reset_value = Signal(16)
        gpt_counter = Signal(14)
        with m.If(midi_clk_en):
            with m.If((gpt_counter == 0) & (gpt_reset_value > 1)):
                m.d.sync += gpt_counter.eq(gpt_reset_value)
                m.d.sync += self.isr[7].eq(1)
            with m. Else():
                m.d.sync += gpt_counter.eq(gpt_counter-1)

        #midi clock timer
        clock_low_byte_cache = Signal(8)
        clock_reset_value = Signal(16)
        clock_counter = Signal(14)
        with m.If(midi_clk_en):
            with m.If((clock_counter == 0) & (clock_reset_value > 1)):
                m.d.sync += clock_counter.eq(clock_reset_value)
                m.d.sync += self.isr[1].eq(1)
            with m.Else():
                m.d.sync += clock_counter.eq(clock_counter-1)

        #midi click counter
        # todo: clock off midi clock and implement isr mux
        click_counter = Signal(7)
        click_reset_value = Signal(7)
        with m.If(0):
            with m.If((click_counter == 0) & (click_reset_value > 0)):
                m.d.sync += click_counter.eq(click_reset_value)
                m.d.sync += self.isr[1].eq(1)
            with m.Else():
                m.d.sync += click_counter.eq(click_counter-1)

        #register io state machine
        self.xltr_oe = Signal()
        m.d.comb += self.addr_num.eq(self.addr[0:3])
        m.d.comb += self.register_num.eq(Cat(self.addr_num, 0, self.group_num))
        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self._dtready.eq(1)
                m.d.comb += self.xltr_oe.eq(1)
                with m.If((self._iack == 0) & (self._irq == 0)):
                   #enable xltr early
                   m.d.comb += self.xltr_oe.eq(0),
                   m.next = "IACK"
                with m.Elif((self._as == 0) &
                   (self.addr[3:24] == base_addr[3:24])):
                   # enable xltr early
                   m.d.comb += self.xltr_oe.eq(0)
                   with m.If(self._lds == 0):
                       with m.If((self._rw == 1)):
                           m.next = "RDATA"
                       with m.Else():
                           m.next = "WDATA"
            with m.State("IACK"):
                m.d.comb += self._dtready.eq(0),
                m.d.comb += self.data.o.eq(self.ivr),
                with m.If(self._iack == 1):
                   m.next = "IDLE"
            with m.State("RDATA"):
                m.d.comb += self._dtready.eq(0)
                with m.If(self.addr_num == 0):
                   # irq vector register
                    m.d.comb += self.data.o.eq(self.ivr)
                with m.Elif(self.addr_num == 2):
                    m.d.comb += self.data.o.eq(self.isr)
                with m.Else():
                    with m.If(self.register_num == 0x34):
                        m.d.comb += self.data.o.eq(0x04)
                    with m.Elif(self.register_num == 0x36):
                        m.d.comb += self.data.o.eq(0x00)
                    with m.Elif(self.register_num == 0x54):
                        m.d.comb += self.data.o.eq(self.tsr)
                    with m.Elif(self.register_num == 0x64):
                        m.d.comb += self.data.o.eq(0xa0)
                    with m.Elif(self.register_num == 0x74):
                        m.d.comb += self.data.o.eq(0x00)
                    with m.Elif(self.register_num == 0x96):
                        m.d.comb += self.data.o.eq(0xFF)
                    with m.Elif(self.register_num == 0xF5):
                        m.d.comb += self.data.o.eq(version_string[self.version_index])
                with m.If(self._as == 1):
                   m.next = "IDLE"
            with m.State("WDATA"):
                m.d.comb += self._dtready.eq(0)
                with m.If(self.addr_num == 0x01):
                    m.d.sync += self.group_num.eq(self.data.i[0:4])
                    m.d.sync += self.ic.eq(self.data.i[7])
                with m.Elif(self.addr_num == 0x03):
                    m.d.sync += self.isr.eq(self.isr & ~self.data.i)
                with m.Else():
                    with m.If(self.register_num == 0x04):
                        m.d.sync += self.ivo.eq(self.data.i[5:8])
                    with m.Elif(self.register_num == 0x06):
                        m.d.sync += self.ier.eq(self.data.i)
                    with m.Elif(self.register_num == 0x14):
                        m.d.sync += self.ase.eq(self.data.i[5])
                    with m.Elif(self.register_num == 0x55):
                        m.d.sync += self.txe.eq(self.data.i[0]),
                        with m.If(self.data.i[2]):
                            m.d.sync += self.txidl.eq(0)
                        m.d.sync += self.brke.eq(self.data.i[3])
                    with m.Elif(self.register_num == 0x56):
                       m.d.sync += self.fifo.w_en.eq(1)
                       m.d.sync += self.fifo.w_data.eq(self.data.i)
                       # clear tx empty isr
                       m.d.sync += self.isr[6].eq(0)
                    with m.Elif(self.register_num == 0x66):
                        m.d.sync += clkm.eq(self.data.i[1])
                    with m.Elif(self.register_num == 0x67):
                        m.d.sync += click_reset_value.eq(self.data.i[0:7])
                        with m.If(self.data.i[7]):
                            m.d.sync += click_counter.eq(self.data.i[0:7])
                    with m.Elif(self.register_num == 0x84):
                        m.d.sync += gpt_low_byte_cache.eq(self.data.i)
                    with m.Elif(self.register_num == 0x85):
                        m.d.sync += gpt_reset_value.eq(Cat(gpt_low_byte_cache, self.data.i[0:6]))
                        with m.If(self.data.i[7]):
                            m.d.sync += gpt_counter.eq(Cat(gpt_low_byte_cache, self.data.i[0:6]))
                    with m.Elif(self.register_num == 0x86):
                        m.d.sync += clock_low_byte_cache.eq(self.data.i)
                    with m.Elif(self.register_num == 0x87):
                        m.d.sync += clock_reset_value.eq(Cat(clock_low_byte_cache, self.data.i[0:6]))
                        with m.If(self.data.i[7]):
                            m.d.sync += clock_counter.eq(Cat(clock_low_byte_cache, self.data.i[0:6]))
                    with m.Elif(self.register_num == 0xF4):
                        m.d.sync += self.version_index.eq(self.data.i)
                #only spend one cycle in WDATA
                #so that writes only happen once
                m.next = "WWAIT"
            with m.State("WWAIT"):
                m.d.comb += self._dtready.eq(0)
                m.d.sync += self.fifo.w_en.eq(0)
                with m.If(self._as == 1):
                   m.next= "IDLE"

        #manual resets - the bus FSM cannot be reset during an ic
        #todo: consider using clock domain reset instead
        with m.If(self.exreset == 0 | self.ic):
            m.d.sync += self.group_num.eq(0)
            m.d.sync += clkm.eq(0)
            m.d.sync += self.ivo.eq(0)
            m.d.sync += self.ier.eq(0)
            m.d.sync += self.isr.eq(0)
            m.d.sync += self.txe.eq(0)
            m.d.sync += self.brke.eq(0)
            m.d.sync += self.ase.eq(0)
            m.d.sync += gpt_counter.eq(0)
            m.d.sync += gpt_low_byte_cache.eq(0)
            m.d.sync += gpt_reset_value.eq(0)
            m.d.sync += clock_counter.eq(0)
            m.d.sync += clock_low_byte_cache.eq(0)
            m.d.sync += clock_reset_value.eq(0)

        if platform is not None:
            m.domains.sync = ClockDomain()
            m.d.comb += ClockSignal().eq(plat.request("sync").i)
            m.d.comb += self.addr.eq(plat.request("addr").i)
            m.d.comb += self._as.eq(plat.request("as").i)
            m.d.comb += self._lds.eq(plat.request("lds").i)
            m.d.comb += self._rw.eq(plat.request("rw").i)
            m.d.comb += plat.request("dtack").o.eq(self._dtready)
            # is there a better way to "attach" this?
            data_port = plat.request("data")
            m.d.comb += self.data.i.eq(data_port.i)
            m.d.comb += data_port.o.eq(self.data.o)
            m.d.comb += data_port.oe.eq(self.data.oe)
            m.d.comb += plat.request("xltr_oe").o.eq(self.xltr_oe)
            m.d.comb += self.data.oe.eq(~plat.request("iddir").i)
            m.d.comb += plat.request("tx").o.eq(self.tx)
            m.d.comb += plat.request("irq2").o.eq(self._irq)
            m.d.comb += self._iack.eq(plat.request("iack2").i)
            m.d.comb += self.exreset.eq(plat.request("exreset").i)
        return m

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

def midi_iack(m):
    while (yield m._irq == 1):
        yield
    yield m._iack.eq(0)
    while (yield m._dtready == 1):
        yield
    yield m._iack.eq(1)
    while (yield m._dtready == 0):
        yield

def test(m):
    yield m.addr.eq(0)
    yield m._as.eq(1)
    yield m._lds.eq(1)
    yield m._rw.eq(1)
    yield m._iack.eq(1)
    yield
    assert(yield m._dtready == 1)
    yield m.addr.eq(base_addr)
    yield
    yield m._as.eq(0)
    yield m._lds.eq(0)
    yield
    yield m._as.eq(1)
    yield m._lds.eq(1)
    yield
    assert(yield m._dtready == 0)
    yield
    # test reset
    yield from midi_write(m, 0x06, 0xFF)
    yield
    yield from midi_write(m, 0x01, 0x80)
    yield
    yield from midi_write(m, 0x01, 0x00)
    yield
    assert(yield m.ier == 0x00)
    #configure
    yield from midi_read(m, 0x34)
    yield from midi_read(m, 0x16)
    yield from midi_write(m, 0x04, 0xE0)
    yield from midi_write(m, 0x06, 0x40) #tx irq only
    yield from midi_write(m, 0x55, 0x01)
    for i in range(0,2):
        yield from midi_write(m, 0x56, i)
    assert(yield m.isr == 0x00)
    assert(yield m.vec == 8)
    assert(yield m.fifo.r_data == 0x00)
    yield from midi_iack(m)
    yield from midi_wait_empty(m)
    assert(yield m.isr == 0x40)
    assert(yield m.vec == 6)
    yield from midi_write(m, 0xf4, 0x00)
    yield from midi_read(m, 0xf5)
    for i in range(1, 10000):
        yield

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "sim":
        m = Midiori()
        run_simulation(m, test(m), vcd_name="midiori.vcd")
    else:
        plat = MidioriPlatform()
        m = Midiori()
        plat.build(m)
