"""
Module for configuration/settings
"""

import ipaddress


# number of simultaneous build jobs to run
BUILDJOBS = 32

# name of qemu executable
QEMU = "qemu-system-x86_64"

# qemu image settings
QEMU_IMG_PREFIX = "kernfab-qemu-img"
QEMU_IMG_SUFFIX = ".qcow2"
QEMU_IMG_SIZE = "20G"
QEMU_IMG_MOUNT_DIR = "kernfab-qemu-img-mount"

# install settings
TAR_TOOL = "/usr/bin/tar"
CP_TOOL = "/usr/bin/cp"
MKINITCPIO_TOOL = "/usr/bin/mkinitcpio"
INSTALL_DEST_KERNEL = "/boot/vmlinuz-linux"
INSTALL_DEST_INITRD = "/boot/initramfs-linux.img"

# vm settings
NUM_VMS = 2
VM_MEM_SIZE = "512"
VM_TAP_NAME = "kernfabvm"
VM_IF_UP_SCRIPT = "kernfab-vm-if-up-script.sh"
VM_IF_DOWN_SCRIPT = "kernfab-vm-if-down-script.sh"
VM_SOCK_FILE_PREFIX = "kernfab-sockfile-vm"
VM_MAC_START = "52:54:00:00:00:10"
VM_IP_START = "172.23.32.10"

# network settings
IP_TOOL = "/usr/bin/ip"
DNSMASQ_TOOL = "/usr/bin/dnsmasq"
SYSCTL_TOOL = "/usr/bin/sysctl"
IPTABLES_TOOL = "/usr/bin/iptables"
CAT_TOOL = "/usr/bin/cat"
DNSMASQ_PID_FILE = "/tmp/kernfab-vm-bridge-dnsmasq.pid"
DNSMASQ_DHCP_IP_RANGE = "172.23.32.20,172.23.32.254"
BRIDGE_NAME = "kernfabbr0"
BRIDGE_IP = "172.23.32.1"
BRIDGE_IP_NET = "172.23.32.0"
BRIDGE_IP_PREFIX_LEN = "24"


def qemu_get_base_image() -> str:
    """
    Get the name of the qemu base image
    """

    return QEMU_IMG_PREFIX + "-base" + QEMU_IMG_SUFFIX


def qemu_get_vm_image(vm_id: int) -> str:
    """
    Get the name of the qemu image identified by vm_id
    """

    return QEMU_IMG_PREFIX + "-vm" + str(vm_id) + QEMU_IMG_SUFFIX


def vm_get_sockfile(vm_id: int) -> str:
    """
    Get the sockfile for vm with id vm_id
    """

    return VM_SOCK_FILE_PREFIX + str(vm_id) + ".sock"


def vm_get_tap(vm_id: int) -> str:
    """
    Get the name of the tap device of vm with id vm_id
    """

    return VM_TAP_NAME + str(vm_id)


def vm_get_mac(vm_id: int) -> str:
    """
    Create a new mac address for vm with id vm_id
    """

    # remove ":" characters from start mac address, treat it as an int and add
    # vm_id to it, convert it back to a hex string, remove leading "0x", and,
    # finally, insert ":" characters again
    base_mac = "".join(VM_MAC_START.split(":"))
    new_mac = hex(int(base_mac, 16) + vm_id)[2:]
    mac = ":".join(new_mac[i:i+2] for i in range(0, len(new_mac), 2))
    return mac


def vm_get_ip(vm_id: int) -> str:
    """
    Create a new ip address for vm with id vm_id
    """

    # use ipaddress module to convert vm ip start address to an ip address, add
    # vm_id to it, and return it as string
    start_ip = ipaddress.ip_address(VM_IP_START)
    new_ip = str(start_ip + vm_id)
    return new_ip
