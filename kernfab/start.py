"""
Module for starting kernel VM(s)
"""

from kernfab import config, qemu


def start() -> None:
    """
    Start kernel
    """

    for name in range(config.NUM_VMS):
        vm_image = f"{config.QEMU_SUBIMG_NAME}{name}"
        vm_id = f"{name}"
        qemu.run_vm(vm_image, vm_id)
