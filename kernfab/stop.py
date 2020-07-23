"""
Module for stopping kernel VM(s)
"""

from kernfab import qemu


def stop(is_quit: bool) -> None:
    """
    Stop kernel VM(s)
    """

    # images = ["1", "2"]
    images = ["1"]
    for name in images:
        vm_id = f"{name}"
        if is_quit:
            qemu.quit_vm(vm_id)
        else:
            qemu.stop_vm(vm_id)
