"""
Module for starting kernel VM(s)
"""

from kernfab import config, qemu


def start(base_image: bool = False) -> None:
    """
    Start kernel
    """

    if base_image:
        vm_image = config.QEMU_BASEIMG_NAME
        vm_id = "0"
        qemu.run_vm(vm_image, vm_id)
    else:
        for name in range(config.NUM_VMS):
            vm_image = f"{config.QEMU_SUBIMG_NAME}{name}"
            vm_id = f"{name}"
            qemu.run_vm(vm_image, vm_id)
