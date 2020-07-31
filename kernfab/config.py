"""
Module for configuration/settings
"""

# number of simultaneous build jobs to run
BUILDJOBS = 32

# name of qemu executable
QEMU = "qemu-system-x86_64"

# qemu image settings
QEMU_BASEIMG_NAME = "qemu-base.img"
QEMU_BASEIMG_SIZE = "20G"
QEMU_SUBIMG_NAME = "qemu-sub.img"

# vm settings
NUM_VMS = 2
VM_TAP_NAME = "kernfabvm"
VM_IF_UP_SCRIPT = "vm_if_up_script.sh"
VM_IF_DOWN_SCRIPT = "vm_if_down_script.sh"
VM_MAC_START = "52:54:00:00:00:10"

# network settings
IP_TOOL = "/usr/bin/ip"
DNSMASQ_TOOL = "/usr/bin/dnsmasq"
SYSCTL_TOOL = "/usr/bin/sysctl"
IPTABLES_TOOL = "/usr/bin/iptables"
DNSMASQ_PID_FILE = "/tmp/kernfab_vm_bridge_dnsmasq.pid"
DNSMASQ_DHCP_IP_RANGE = "172.23.32.20,172.23.32.254"
BRIDGE_NAME = "kernfabbr0"
BRIDGE_IP = "172.23.32.1"
BRIDGE_IP_NET = "172.23.32.0"
BRIDGE_IP_PREFIX_LEN = "24"


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
