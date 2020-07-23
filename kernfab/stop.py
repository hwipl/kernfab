"""
Module for stopping kernel VM(s)
"""

from kernfab import qemu


def stop() -> None:
    """
    Stop kernel VM(s)
    """

    # images = ["1", "2"]
    images = ["1"]
    for name in images:
        vm_id = f"{name}"
        qemu.stop_vm(vm_id)
