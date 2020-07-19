"""
Module for installing the kernel
"""

from kernfab import config, qemu, run


def _install_sub_image_kernel() -> None:
    """
    Install kernel in sub image
    """

    mount_dir = "vm-mount"
    install_host = ""
    kernel_version = "5.8.0-rc4+"

    # extract kernel archive to mounted vm image
    kernel_archive = f"linux-{kernel_version}-x86.tar.xz"
    cmd = f"tar xvfJ {kernel_archive} -C {mount_dir}"
    run.run_cmd(install_host, cmd)

    # rename/copy installed kernel
    cmd = f"cp {mount_dir}/boot/vmlinuz-{kernel_version} " \
        f"{mount_dir}/boot/vmlinuz-linux"
    run.run_cmd(install_host, cmd)

    # create initramfs for kernel
    cmd = f"mkinitcpio -g {mount_dir}/boot/initramfs-linux.img " \
        f"-k {kernel_version} -r {mount_dir}"
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
        _install_sub_image_kernel()
        qemu.umount_image()


def install() -> None:
    """
    Install kernel
    """

    _install_sub_images()
