"""
Module for stopping kernel VM(s)
"""

from kernfab import config, network, qemu


def stop(is_quit: bool) -> None:
    """
    Stop kernel VM(s)
    """

    for vm_id in range(config.NUM_VMS):
        if is_quit:
            qemu.quit_vm(vm_id)
        else:
            qemu.stop_vm(vm_id)
    network.stop()
