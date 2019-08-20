from nmigen.build import *
from nmigen.vendor.lattice_ice40 import LatticeICE40Platform

__all__ = ["MidioriPlatform"]

class MidioriPlatform(LatticeICE40Platform):
    device    = "iCE40HX1K"
    package   = "vq100"
    clocks    = [
        ("sync", 16e6),
    ]
    resources = [
        Resource("sync", 0, Pins("63", dir="i")),
        Resource("rw", 0, Pins("100", dir="i")),
        Resource("exreset", 0, Pins("99", dir="i")),
        Resource("ioclk", 0, Pins("97", dir="i")),
        Resource("iddir", 0, Pins("96", dir="i")),
        Resource("iack4", 0,Pins("95", dir="i")),
        Resource("iack2", 0, Pins("94", dir="i")),
        Resource("dtack", 0, Pins("93", dir="o")),
        Resource("irq4", 0, Pins("91", dir="o")),
        Resource("irq2", 0, Pins("90", dir="o")),
        Resource("lds", 0, Pins("1", dir="i")),
        Resource("as", 0, Pins("2", dir="i")),
        Resource("a", 0, Pins("3", dir="i")),
        Resource("b", 0, Pins("4", dir="i")),
        Resource("c", 0, Pins("7", dir="i")),

        Resource("addr", 0, Pins("40 37 36 34 33 30 29 18 16 15 13 12 10 9 8 81 80 79 78 74 73 72 71", dir="i")),
        Resource("data", 0, Pins("28 27 26 25 24 21 20 19", dir="io")),

        Resource("xltr_oe", 0, Pins("51", dir="o")),
        Resource("tx", 0, Pins("66", dir="o"))

    ]
    connectors = []
