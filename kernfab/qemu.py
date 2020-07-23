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

    # make sure mount directory exists
    mnt_dir = "vm-mount"
    mkdir_cmd = f"mkdir {mnt_dir}"
    run.run_ok(mnt_host, mkdir_cmd)

    # mount nbd partition
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


def run_vm(vm_image: str, vm_id: str) -> None:
    """
    Run a VM
    """

    host = ""
    options = "-enable-kvm " \
        "-m 512 " \
        "-daemonize " \
        f"-vnc 127.0.0.1:{vm_id} " \
        f"-drive discard=unmap,cache=none,file={vm_image},if=virtio " \
        f"-netdev tap,id=net0,ifname=vmtap{vm_id},script=no,downscript=no " \
        "-device virtio-net-pci,netdev=net0 " \
        "-object rng-random,filename=/dev/urandom,id=rng0 " \
        "-device virtio-rng-pci,rng=rng0 " \
        f"-monitor unix:vm{vm_id}.sock,server,nowait"
    vm_cmd = f"{config.QEMU} {options}"
    print(vm_cmd)
    run.run_background(host, vm_cmd)


def stop_vm(vm_id: str) -> None:
    """
    Stop a VM
    """

    host = ""
    cmd = f"echo \"system_powerdown\" | nc -U \"vm{vm_id}.sock\""
    run.run_cmd(host, cmd)


def quit_vm(vm_id: str) -> None:
    """
    Quit a VM (force stop)
    """

    host = ""
    cmd = f"echo \"quit\" | nc -U \"vm{vm_id}.sock\""
    run.run_cmd(host, cmd)


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
