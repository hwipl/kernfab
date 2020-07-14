"""
Module for creating virtual machine images and
running virtual machines with qemu
"""

from kernfab import config, run


def create_base_image() -> None:
    """
    Create a base vm image
    """

    image_host = ""
    file_format = "qcow2"
    file_name = config.QEMU_BASEIMG_NAME
    file_size = config.QEMU_BASEIMG_SIZE
    image_cmd = f"qemu-img create -f {file_format} {file_name} {file_size}"
    run.run_cmd(image_host, image_cmd)


def create_sub_image() -> None:
    """
    Create a sub vm image that is based on a base image
    """

    image_host = ""
    base_image = config.QEMU_BASEIMG_NAME
    file_name = config.QEMU_SUBIMG_NAME
    image_cmd = f"qemu-img create -b {base_image} {file_name}"
    run.run_cmd(image_host, image_cmd)


def mount_image() -> None:
    """
    Mount a vm image
    """

    mnt_host = ""

    # setup network block device
    nbd_dev = "/dev/nbd0"
    file_name = config.QEMU_SUBIMG_NAME
    nbd_cmd = f"qemu-nbd --connect={nbd_dev} {file_name}"
    run.run_cmd(mnt_host, nbd_cmd)

    # mount nbd partition
    nbd_part = "/dev/nbd0p1"
    mnt_dir = "vm-mount"
    mnt_cmd = f"mount {nbd_part} {mnt_dir}"
    run.run_cmd(mnt_host, mnt_cmd)


def umount_image() -> None:
    """
    Unmount a vm image
    """

    mnt_host = ""

    # umount nbd partition
    mnt_dir = "vm-mount"
    mnt_cmd = f"umount {mnt_dir}"
    run.run_cmd(mnt_host, mnt_cmd)

    # close network block device
    nbd_dev = "/dev/nbd0"
    nbd_cmd = f"qemu-nbd --disconnect {nbd_dev}"
    run.run_cmd(mnt_host, nbd_cmd)


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
    vm_cmd = f"{config.QEMU} {options}"
    run.run_cmd(host, vm_cmd)
