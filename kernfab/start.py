"""
Module for starting kernel VM(s)
"""

from kernfab import config, qemu


def start() -> None:
    """
    Start kernel
    """

    # images = ["1", "2"]
    images = ["1"]
    for name in images:
        vm_image = f"{config.QEMU_SUBIMG_NAME}{name}"
        vm_id = f"{name}"
        qemu.run_vm(vm_image, vm_id)
