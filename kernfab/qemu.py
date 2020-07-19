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
    file_name = config.QEMU_BASEIMG_NAME

    # stop if file already exists
    if run.run_ok(image_host, f"ls {file_name}"):
        print("File already exists")
        return

    file_format = "qcow2"
    file_size = config.QEMU_BASEIMG_SIZE
    image_cmd = f"qemu-img create -f {file_format} {file_name} {file_size}"
    run.run_cmd(image_host, image_cmd)


def create_sub_image(name: str) -> None:
    """
    Create a sub vm image that is based on a base image
    """

    image_host = ""
    file_format = "qcow2"
    base_image = config.QEMU_BASEIMG_NAME
    file_name = config.QEMU_SUBIMG_NAME
    image_cmd = \
        f"qemu-img create -f {file_format} -b {base_image} {file_name}{name}"
    run.run_cmd(image_host, image_cmd)


def mount_image(file_name: str) -> None:
    """
    Mount a vm image
    """

    mnt_host = ""

    # make sure nbd module is loaded
    mod_cmd = "modprobe nbd"
    run.run_ok(mnt_host, mod_cmd)

    # setup network block device
    nbd_dev = "/dev/nbd0"
    nbd_cmd = f"qemu-nbd --connect={nbd_dev} {file_name}"
    print(f"Creating nbd {nbd_dev}")
    run.run_background(mnt_host, nbd_cmd)

    # make sure nbd partition is ready
    nbd_part = "/dev/nbd0p1"
    run.run_try(mnt_host, f"ls {nbd_part}", 10)

    # mount nbd partition
    mnt_dir = "vm-mount"
    mnt_cmd = f"mount {nbd_part} {mnt_dir}"
    print(f"Mounting partition {nbd_part}")
    run.run_cmd(mnt_host, mnt_cmd)


def umount_image() -> None:
    """
    Unmount a vm image
    """

    mnt_host = ""

    # umount nbd partition
    mnt_dir = "vm-mount"
    mnt_cmd = f"umount {mnt_dir}"
    print(f"Umounting dir {mnt_dir}")
    run.run_cmd(mnt_host, mnt_cmd)

    # close network block device
    nbd_dev = "/dev/nbd0"
    nbd_cmd = f"qemu-nbd --disconnect {nbd_dev}"
    print(f"Disconnecting nbd {nbd_dev}")
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


def _qemu_base_image_create() -> None:
    """
    create base image
    """

    print("Create base image")
    create_base_image()


def _qemu_base_image_mount() -> None:
    """
    mount base image
    """

    print("Mount base image")
    file_name = config.QEMU_BASEIMG_NAME
    mount_image(file_name)


def _qemu_base_image_umount() -> None:
    """
    umount base image
    """

    print("Umount base image")
    umount_image()


def qemu(command: str) -> None:
    """
    qemu specific command handling
    """

    cmd_map = {
        "base-image-create": _qemu_base_image_create,
        "base-image-mount": _qemu_base_image_mount,
        "base-image-umount": _qemu_base_image_umount,
    }
    cmd_map[command]()
