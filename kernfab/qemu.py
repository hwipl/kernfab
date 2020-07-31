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
    file_name = config.qemu_get_base_image()

    # stop if file already exists
    if run.run_ok(image_host, f"{config.LS_TOOL} {file_name}"):
        print("File already exists")
        return

    file_format = "qcow2"
    file_size = config.QEMU_IMG_SIZE
    image_cmd = f"{config.QEMU_IMG_TOOL} create -f {file_format} " \
        f"{file_name} {file_size}"
    run.run_cmd(image_host, image_cmd)


def create_vm_image(vm_id: int) -> None:
    """
    Create a vm image that is based on a base image
    """

    image_host = ""
    file_format = "qcow2"
    base_image = config.qemu_get_base_image()
    file_name = config.qemu_get_vm_image(vm_id)
    image_cmd = f"{config.QEMU_IMG_TOOL} create -f {file_format} " \
        f"-b {base_image} {file_name}"
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
    run.run_try(mnt_host, f"{config.LS_TOOL} {nbd_part}", 10)

    # make sure mount directory exists
    mnt_dir = config.QEMU_IMG_MOUNT_DIR
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
    mnt_dir = config.QEMU_IMG_MOUNT_DIR
    mnt_cmd = f"umount {mnt_dir}"
    print(f"Umounting dir {mnt_dir}")
    run.run_cmd(mnt_host, mnt_cmd)

    # close network block device
    nbd_dev = "/dev/nbd0"
    nbd_cmd = f"qemu-nbd --disconnect {nbd_dev}"
    print(f"Disconnecting nbd {nbd_dev}")
    run.run_cmd(mnt_host, nbd_cmd)


def run_vm(vm_image: str, vm_id: int) -> None:
    """
    Run a VM
    """

    host = ""

    # check if vm is already running
    vm_sock = config.vm_get_sockfile(vm_id)
    if run.run_ok(host, f"{config.LS_TOOL} {vm_sock}"):
        print("VM seems to be running already")
        return

    if vm_id > 8:
        print("invalid VM ID")
        return

    vm_tap = config.vm_get_tap(vm_id)
    options = "-enable-kvm " \
        f"-m {config.VM_MEM_SIZE} " \
        "-daemonize " \
        f"-vnc 127.0.0.1:{vm_id} " \
        f"-drive discard=unmap,cache=none,file={vm_image},if=virtio " \
        f"-netdev tap,id=net0,ifname={vm_tap}," \
        f"script={config.VM_IF_UP_SCRIPT}," \
        f"downscript={config.VM_IF_DOWN_SCRIPT} " \
        f"-device virtio-net-pci,netdev=net0," \
        f"mac={config.vm_get_mac(int(vm_id))} " \
        "-object rng-random,filename=/dev/urandom,id=rng0 " \
        "-device virtio-rng-pci,rng=rng0 " \
        f"-monitor unix:{vm_sock},server,nowait"
    vm_cmd = f"{config.QEMU} {options}"
    print(vm_cmd)
    run.run_background(host, vm_cmd)


def _remove_vm_sockfile(vm_id: int) -> None:
    """
    Delete sockfile of vm
    """

    host = ""
    vm_sock = config.vm_get_sockfile(vm_id)
    cmd = f"rm {vm_sock}"
    run.run_cmd(host, cmd)


def stop_vm(vm_id: int) -> None:
    """
    Stop a VM
    """

    host = ""
    vm_sock = config.vm_get_sockfile(vm_id)
    if run.run_ok(host, f"{config.LS_TOOL} {vm_sock}"):
        cmd = f"{config.ECHO_TOOL} \"system_powerdown\" | nc -U \"{vm_sock}\""
        run.run_cmd(host, cmd)
        _remove_vm_sockfile(vm_id)


def quit_vm(vm_id: int) -> None:
    """
    Quit a VM (force stop)
    """

    host = ""
    vm_sock = config.vm_get_sockfile(vm_id)
    if run.run_ok(host, f"{config.LS_TOOL} {vm_sock}"):
        cmd = f"{config.ECHO_TOOL} \"quit\" | nc -U \"{vm_sock}\""
        run.run_cmd(host, cmd)
        _remove_vm_sockfile(vm_id)


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
    file_name = config.qemu_get_base_image()
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
