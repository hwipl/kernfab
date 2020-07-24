"""
Module for configuration/settings
"""

# number of simultaneous build jobs to run
BUILDJOBS = 32

# name of qemu executable
QEMU = "qemu-system-x86_64"

# qemu image settings
QEMU_BASEIMG_NAME = "qemu-base.img"
QEMU_BASEIMG_SIZE = "20G"
QEMU_SUBIMG_NAME = "qemu-sub.img"

# vm settings
NUM_VMS = 2
