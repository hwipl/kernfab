"""
Module for installing the kernel
"""

from kernfab import config, qemu, run


def _chroot_sub_image_install() -> None:
    """
    Chroot into sub image directory and install
    """

    mount_dir = "vm-mount"
    install_host = ""

    # mount proc, sys and dev into chroot dir
    cmd = f"mount -t proc /proc {mount_dir}/proc/"
    run.run_cmd(install_host, cmd)
    cmd = f"mount --rbind /sys {mount_dir}/sys/"
    run.run_cmd(install_host, cmd)
    cmd = f"mount --make-rslave {mount_dir}/sys"
    run.run_cmd(install_host, cmd)
    cmd = f"mount --rbind /dev {mount_dir}/dev/"
    run.run_cmd(install_host, cmd)
    cmd = f"mount --make-rslave {mount_dir}/dev"
    run.run_cmd(install_host, cmd)

    # chroot and run install command
    # add \"su - -c <cmd>\"" to install_cmd?
    install_cmd = "pwd"     # for testing
    cmd = f"chroot {mount_dir} /bin/bash -c \"{install_cmd}\""
    run.run_cmd(install_host, cmd)

    # umount everything in chroot dir
    cmd = f"umount {mount_dir}/proc"
    run.run_cmd(install_host, cmd)
    cmd = f"umount {mount_dir}/sys"
    run.run_cmd(install_host, cmd)
    cmd = f"umount {mount_dir}/dev"
    run.run_cmd(install_host, cmd)


def _install_sub_images() -> None:
    """
    Create sub images and install in them
    """

    # images = ["1", "2"]
    images = ["1"]
    for name in images:
        qemu.create_sub_image(name)
        file_name = f"{config.QEMU_SUBIMG_NAME}{name}"
        qemu.mount_image(file_name)
        _chroot_sub_image_install()
        # qemu.umount_image()


def install() -> None:
    """
    Install kernel
    """

    _install_sub_images()
