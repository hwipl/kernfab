"""
Module for vm networking
"""

from kernfab import config, run


def _start_bridge() -> None:
    """
    Start vm network bridge
    """

    host = ""
    ip_tool = "/usr/bin/ip"

    # add bridge device
    add_cmd = f"{ip_tool} link add name {config.BRIDGE_NAME} type bridge"
    run.run_cmd(host, add_cmd)

    # make sure bridge device is up
    up_cmd = f"{ip_tool} link set {config.BRIDGE_NAME} up"
    run.run_cmd(host, up_cmd)

    # set promiscuous mode on bridge device
    promisc_cmd = f"{ip_tool} link set {config.BRIDGE_NAME} promisc on"
    run.run_cmd(host, promisc_cmd)

    # set ip address on bridge device
    ip_cmd = f"{ip_tool} address add {config.BRIDGE_IP}/" \
        f"{config.BRIDGE_IP_PREFIX_LEN} dev {config.BRIDGE_NAME}"
    run.run_cmd(host, ip_cmd)


def _stop_bridge() -> None:
    """
    Stop vm network bridge
    """

    host = ""
    ip_tool = "/usr/bin/ip"

    # remove ip from bridge device
    ip_cmd = f"{ip_tool} address del {config.BRIDGE_IP}/" \
        f"{config.BRIDGE_IP_PREFIX_LEN} dev {config.BRIDGE_NAME}"
    run.run_cmd(host, ip_cmd)

    # turn promiscuous mode of on bridge device
    promisc_cmd = f"{ip_tool} link set {config.BRIDGE_NAME} promisc off"
    run.run_cmd(host, promisc_cmd)

    # set bridge down
    down_cmd = f"{ip_tool} link set {config.BRIDGE_NAME} down"
    run.run_cmd(host, down_cmd)

    # remove bridge device
    del_cmd = f"{ip_tool} link del name {config.BRIDGE_NAME} type bridge"
    run.run_cmd(host, del_cmd)


def _start_dnsmasq() -> None:
    """
    Start dhcp and dns server for vms
    """

    host = ""
    dnsmasq_tool = "/usr/bin/dnsmasq"
    pid_file = "/tmp/kernfab_vm_bridge_dnsmasq.pid"
    bridge_ip_range = "172.23.32.10,172.23.32.254"
    bridge_routes = f"0.0.0.0/0,{config.BRIDGE_IP}"
    cmd = f"{dnsmasq_tool} " \
        f"--interface={config.BRIDGE_NAME} " \
        "--bind-interfaces " \
        "--except-interface=lo " \
        f"--pid-file={pid_file} " \
        f"--dhcp-range={bridge_ip_range} " \
        f"--dhcp-option=option:classless-static-route,{bridge_routes}"

    if config.NUM_VMS > 8:
        print("too many VMs")
        return

    for i in range(config.NUM_VMS):
        mac_to_ip = f"52:54:00:00:00:1{i},172.23.32.1{i}"
        cmd += f" --dhcp-host={mac_to_ip}"

    print(cmd)
    run.run_cmd(host, cmd)


def _stop_dnsmasq() -> None:
    """
    Stop dhcp and dns server for vms
    """

    host = ""
    pid_file = "/tmp/kernfab_vm_bridge_dnsmasq.pid"
    cmd = f"kill $(cat {pid_file})"
    run.run_cmd(host, cmd)


def _start_nat() -> None:
    """
    Start nat for vms
    """

    host = ""

    # enable ip forwarding
    sysctl_tool = "/usr/bin/sysctl"
    fwd_cmd = f"{sysctl_tool} net.ipv4.conf.{config.BRIDGE_NAME}.forwarding=1"
    run.run_cmd(host, fwd_cmd)

    # enable nat
    iptables_tool = "/usr/bin/iptables"
    prefix = "172.23.32.0/24"
    masq_cmd = f"{iptables_tool} -t nat -A POSTROUTING -s {prefix} " \
        "-j MASQUERADE"
    run.run_cmd(host, masq_cmd)

    out_cmd = f"{iptables_tool} -A FORWARD -m conntrack " \
        f"--ctstate RELATED,ESTABLISHED -o {config.BRIDGE_NAME} -d {prefix} " \
        "-j ACCEPT"
    run.run_cmd(host, out_cmd)

    in_cmd = f"{iptables_tool} -A FORWARD -i {config.BRIDGE_NAME} " \
        f"-s {prefix} -j ACCEPT"
    run.run_cmd(host, in_cmd)


def _stop_nat() -> None:
    """
    Stop nat for vms
    """

    host = ""

    # disable ip forwarding
    sysctl_tool = "/usr/bin/sysctl"
    fwd_cmd = f"{sysctl_tool} net.ipv4.conf.{config.BRIDGE_NAME}.forwarding=0"
    run.run_cmd(host, fwd_cmd)

    # disable nat
    iptables_tool = "/usr/bin/iptables"
    prefix = "172.23.32.0/24"
    masq_cmd = f"{iptables_tool} -t nat -D POSTROUTING -s {prefix} " \
        "-j MASQUERADE"
    run.run_cmd(host, masq_cmd)

    out_cmd = f"{iptables_tool} -D FORWARD -m conntrack " \
        f"--ctstate RELATED,ESTABLISHED -o {config.BRIDGE_NAME} -d {prefix} " \
        "-j ACCEPT"
    run.run_cmd(host, out_cmd)

    in_cmd = f"{iptables_tool} -D FORWARD -i {config.BRIDGE_NAME} " \
        f"-s {prefix} -j ACCEPT"
    run.run_cmd(host, in_cmd)


def _create_if_up_script() -> None:
    """
    Create if up script for vm
    """

    host = ""

    # create script
    ip_tool = "/usr/bin/ip"
    script = f"""#!/bin/bash

IP={ip_tool}
BRIDGE={config.BRIDGE_NAME}
TAP=\\$1

# add tap interface to bridge
\\$IP link set \\"\\$TAP\\" up
\\$IP link set \\"\\$TAP\\" promisc on
\\$IP link set \\"\\$TAP\\" master \\$BRIDGE
"""
    cat_cmd = f"cat <<-\\\"EOF\\\" > {config.VM_IF_UP_SCRIPT}\n{script}EOF"
    run.run_cmd(host, cat_cmd)

    # make script executable
    chmod_cmd = f"chmod +x {config.VM_IF_UP_SCRIPT}"
    run.run_cmd(host, chmod_cmd)


def _create_if_down_script() -> None:
    """
    Create if down script for vm
    """

    host = ""

    # create script
    ip_tool = "/usr/bin/ip"
    script = f"""#!/bin/bash

IP={ip_tool}
TAP=\\$1

# remove tap interface from bridge
\\$IP link set \\"\\$TAP\\" nomaster
\\$IP link set \\"\\$TAP\\" promisc off
\\$IP link set \\"\\$TAP\\" down
"""
    cat_cmd = f"cat <<-\\\"EOF\\\" > {config.VM_IF_DOWN_SCRIPT}\n{script}EOF"
    run.run_cmd(host, cat_cmd)

    # make script executable
    chmod_cmd = f"chmod +x {config.VM_IF_DOWN_SCRIPT}"
    run.run_cmd(host, chmod_cmd)


def start() -> None:
    """
    Start vm network
    """

    _start_bridge()
    _start_dnsmasq()
    _start_nat()
    _create_if_up_script()
    _create_if_down_script()


def stop() -> None:
    """
    Stop vm network
    """

    _stop_nat()
    _stop_dnsmasq()
    _stop_bridge()
