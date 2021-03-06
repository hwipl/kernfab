"""
Module for starting kernel VM(s)
"""

from kernfab import config, network, qemu


def start(base_image: bool = False) -> None:
    """
    Start kernel
    """

    network.start()
    if base_image:
        vm_image = config.qemu_get_base_image()
        vm_id = 0
        qemu.run_vm(vm_image, vm_id)
    else:
        for vm_id in range(config.NUM_VMS):
            vm_image = config.qemu_get_vm_image(vm_id)
            qemu.run_vm(vm_image, vm_id)
