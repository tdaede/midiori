from migen.build.generic_platform import *
from migen.build.lattice import LatticePlatform


__all__ = ['Platform']


_io = [
    ("sclk", 0, Pins("63"), IOStandard("LVCMOS33")),
    ("rw", 0, Pins("100"), IOStandard("LVCMOS33")),
    ("exreset", 0, Pins("99"), IOStandard("LVCMOS33")),
    ("ioclk", 0, Pins("97"), IOStandard("LVCMOS33")),
    ("iddir", 0, Pins("96"), IOStandard("LVCMOS33")),
    ("iack4", 0, Pins("95"), IOStandard("LVCMOS33")),
    ("iack2", 0, Pins("94"), IOStandard("LVCMOS33")),
    ("dtack", 0, Pins("93"), IOStandard("LVCMOS33")),
    ("irq4", 0, Pins("91"), IOStandard("LVCMOS33")),
    ("irq2", 0, Pins("90"), IOStandard("LVCMOS33")),
    ("lds", 0, Pins("1"), IOStandard("LVCMOS33")),
    ("as", 0, Pins("2"), IOStandard("LVCMOS33")),
    ("a", 0, Pins("3"), IOStandard("LVCMOS33")),
    ("b", 0, Pins("4"), IOStandard("LVCMOS33")),
    ("c", 0, Pins("7"), IOStandard("LVCMOS33")),

    ("addr", 0, Pins("40 37 36 34 33 30 29 18 16 15 13 12 10 9 8 81 80 79 78 74 73 72 71"), IOStandard("LVCMOS33")),
    ("data", 0, Pins("28 27 26 25 24 21 20 19"), IOStandard("LVCMOS33")),

    ("xltr_oe", 0, Pins("51"), IOStandard("LVCMOS33")),
]

_connectors = [
]


class Platform(LatticePlatform):
    default_clk_name = "sclk"
    default_clk_period = 1e9 / 16e6

    def __init__(self):
        LatticePlatform.__init__(self, "ice40-hx1k-vq100", _io, _connectors,
                                 toolchain="icestorm")

