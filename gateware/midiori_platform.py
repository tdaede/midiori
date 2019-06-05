from nmigen.build import *
from nmigen.vendor.lattice_ice40 import LatticeICE40Platform

__all__ = ["MidioriPlatform"]

class MidioriPlatform(LatticeICE40Platform):
    device    = "hx1k"
    package   = "vq100"
    clocks    = [
        ("sync", 16e6),
    ]
    resources = [
        Resource("sync", 0, Pins("63", dir="i"),
                 extras={"GLOBAL": "1", "IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("rw", 0, Pins("100", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("exreset", 0, Pins("99", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("ioclk", 0, Pins("97", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("iddir", 0, Pins("96", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("iack4", 0,Pins("95", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("iack2", 0, Pins("94", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("dtack", 0, Pins("93", dir="o"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("irq4", 0, Pins("91", dir="o"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("irq2", 0, Pins("90", dir="o"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("lds", 0, Pins("1", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("as", 0, Pins("2", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("a", 0, Pins("3", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("b", 0, Pins("4", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("c", 0, Pins("7", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),

                 Resource("addr", 0, Pins("40 37 36 34 33 30 29 18 16 15 13 12 10 9 8 81 80 79 78 74 73 72 71", dir="i"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("data", 0, Pins("28 27 26 25 24 21 20 19", dir="io"), extras={"IO_STANDARD": "SB_LVCMOS33"}),

                 Resource("xltr_oe", 0, Pins("51", dir="o"), extras={"IO_STANDARD": "SB_LVCMOS33"}),
                 Resource("tx", 0, Pins("66", dir="o"), extras={"IO_STANDARD": "SB_LVCMOS33"})

    ]
    connectors = []
