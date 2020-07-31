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
