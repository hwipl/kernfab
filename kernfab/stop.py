"""
Module for stopping kernel VM(s)
"""

from kernfab import config, qemu


def stop(is_quit: bool) -> None:
    """
    Stop kernel VM(s)
    """

    for name in range(config.NUM_VMS):
        vm_id = f"{name}"
        if is_quit:
            qemu.quit_vm(vm_id)
        else:
            qemu.stop_vm(vm_id)
