"""
Module for creating virtual machine images and
running virtual machines with qemu
"""

import invoke                   # type: ignore
from fabric import Connection   # type: ignore

# name of qemu executable
QEMU = "qemu-system-x86_64"


def _run_cmd(host: str, cmd: str) -> None:
    """
    Run a command
    """

    cmd = f"bash -l -c \"{cmd}\""
    if host == "":
        invoke.run(cmd, warn=True)
    else:
        conn = Connection(host)
        conn.run(cmd, warn=True)


def create_base_image() -> None:
    """
    Create a base vm image
    """

    image_host = ""
    file_format = "qcow2"
    file_name = "qemu-base.img"
    file_size = "20G"
    image_cmd = f"qemu-img create -f {file_format} {file_name} {file_size}"
    _run_cmd(image_host, image_cmd)


def create_sub_image() -> None:
    """
    Create a sub vm image that is based on a base image
    """

    image_host = ""
    base_image = "qemu-base.img"
    file_name = "qemu-sub.img"
    image_cmd = f"qemu-img create -b {base_image} {file_name}"
    _run_cmd(image_host, image_cmd)


def run_vm():
    """
    Run a VM
    """

    host = ""
    options = "-enable-kvm " \
        "-m 512 " \
        "-daemonize " \
        "-vnc 127.0.0.1:0 " \
        "-drive discard=unmap,cache=none,file=qemu.img,if=virtio " \
        "-netdev tap=id=net0,ifname=vmtap0 " \
        "-device virtio-net-pci,netdev=net0 " \
        "-object rng-random,filename=/dev/urandom,id=rng0 " \
        "-device virtio-rng-pci, rng=rng0 " \
        "-monitor unix:vm0.sock,server,nowait"
    vm_cmd = f"{QEMU} {options}"
    _run_cmd(host, vm_cmd)
