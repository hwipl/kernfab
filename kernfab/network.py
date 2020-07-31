"""
Module for vm networking
"""

from kernfab import config, run


def _start_bridge() -> None:
    """
    Start vm network bridge
    """

    host = ""

    # add bridge device
    add_cmd = f"{config.IP_TOOL} link add name {config.BRIDGE_NAME} " \
        "type bridge"
    run.run_cmd(host, add_cmd)

    # make sure bridge device is up
    up_cmd = f"{config.IP_TOOL} link set {config.BRIDGE_NAME} up"
    run.run_cmd(host, up_cmd)

    # set promiscuous mode on bridge device
    promisc_cmd = f"{config.IP_TOOL} link set {config.BRIDGE_NAME} promisc on"
    run.run_cmd(host, promisc_cmd)

    # set ip address on bridge device
    ip_cmd = f"{config.IP_TOOL} address add {config.BRIDGE_IP}/" \
        f"{config.BRIDGE_IP_PREFIX_LEN} dev {config.BRIDGE_NAME}"
    run.run_cmd(host, ip_cmd)


def _stop_bridge() -> None:
    """
    Stop vm network bridge
    """

    host = ""

    # remove ip from bridge device
    ip_cmd = f"{config.IP_TOOL} address del {config.BRIDGE_IP}/" \
        f"{config.BRIDGE_IP_PREFIX_LEN} dev {config.BRIDGE_NAME}"
    run.run_cmd(host, ip_cmd)

    # turn promiscuous mode of on bridge device
    promisc_cmd = f"{config.IP_TOOL} link set {config.BRIDGE_NAME} promisc off"
    run.run_cmd(host, promisc_cmd)

    # set bridge down
    down_cmd = f"{config.IP_TOOL} link set {config.BRIDGE_NAME} down"
    run.run_cmd(host, down_cmd)

    # remove bridge device
    del_cmd = f"{config.IP_TOOL} link del name {config.BRIDGE_NAME} " \
        "type bridge"
    run.run_cmd(host, del_cmd)


def _start_dnsmasq() -> None:
    """
    Start dhcp and dns server for vms
    """

    host = ""
    bridge_routes = f"0.0.0.0/0,{config.BRIDGE_IP}"
    cmd = f"{config.DNSMASQ_TOOL} " \
        f"--interface={config.BRIDGE_NAME} " \
        "--bind-interfaces " \
        "--except-interface=lo " \
        f"--pid-file={config.DNSMASQ_PID_FILE} " \
        f"--dhcp-range={config.DNSMASQ_DHCP_IP_RANGE} " \
        f"--dhcp-option=option:classless-static-route,{bridge_routes}"

    if config.NUM_VMS > 8:
        print("too many VMs")
        return

    for i in range(config.NUM_VMS):
        mac_to_ip = f"{config.vm_get_mac(i)},{config.vm_get_ip(i)}"
        cmd += f" --dhcp-host={mac_to_ip}"

    print(cmd)
    run.run_cmd(host, cmd)


def _stop_dnsmasq() -> None:
    """
    Stop dhcp and dns server for vms
    """

    host = ""
    cmd = f"{config.KILL_TOOL} $({config.CAT_TOOL} {config.DNSMASQ_PID_FILE})"
    run.run_cmd(host, cmd)


def _start_nat() -> None:
    """
    Start nat for vms
    """

    host = ""

    # enable ip forwarding
    fwd_cmd = f"{config.SYSCTL_TOOL} " \
        f"net.ipv4.conf.{config.BRIDGE_NAME}.forwarding=1"
    run.run_cmd(host, fwd_cmd)

    # enable nat
    prefix = f"{config.BRIDGE_IP_NET}/{config.BRIDGE_IP_PREFIX_LEN}"
    masq_cmd = f"{config.IPTABLES_TOOL} -t nat -A POSTROUTING -s {prefix} " \
        "-j MASQUERADE"
    run.run_cmd(host, masq_cmd)

    out_cmd = f"{config.IPTABLES_TOOL} -A FORWARD -m conntrack " \
        f"--ctstate RELATED,ESTABLISHED -o {config.BRIDGE_NAME} -d {prefix} " \
        "-j ACCEPT"
    run.run_cmd(host, out_cmd)

    in_cmd = f"{config.IPTABLES_TOOL} -A FORWARD -i {config.BRIDGE_NAME} " \
        f"-s {prefix} -j ACCEPT"
    run.run_cmd(host, in_cmd)


def _stop_nat() -> None:
    """
    Stop nat for vms
    """

    host = ""

    # disable ip forwarding
    fwd_cmd = f"{config.SYSCTL_TOOL} " \
        f"net.ipv4.conf.{config.BRIDGE_NAME}.forwarding=0"
    run.run_cmd(host, fwd_cmd)

    # disable nat
    prefix = f"{config.BRIDGE_IP_NET}/{config.BRIDGE_IP_PREFIX_LEN}"
    masq_cmd = f"{config.IPTABLES_TOOL} -t nat -D POSTROUTING -s {prefix} " \
        "-j MASQUERADE"
    run.run_cmd(host, masq_cmd)

    out_cmd = f"{config.IPTABLES_TOOL} -D FORWARD -m conntrack " \
        f"--ctstate RELATED,ESTABLISHED -o {config.BRIDGE_NAME} -d {prefix} " \
        "-j ACCEPT"
    run.run_cmd(host, out_cmd)

    in_cmd = f"{config.IPTABLES_TOOL} -D FORWARD -i {config.BRIDGE_NAME} " \
        f"-s {prefix} -j ACCEPT"
    run.run_cmd(host, in_cmd)


def _create_if_up_script() -> None:
    """
    Create if up script for vm
    """

    host = ""

    # create script
    script = f"""#!/bin/bash

IP={config.IP_TOOL}
BRIDGE={config.BRIDGE_NAME}
TAP=\\$1

# add tap interface to bridge
\\$IP link set \\"\\$TAP\\" up
\\$IP link set \\"\\$TAP\\" promisc on
\\$IP link set \\"\\$TAP\\" master \\$BRIDGE
"""
    cat_cmd = f"{config.CAT_TOOL} <<-\\\"EOF\\\" > " \
        f"{config.VM_IF_UP_SCRIPT}\n{script}EOF"
    run.run_cmd(host, cat_cmd)

    # make script executable
    chmod_cmd = f"{config.CHMOD_TOOL} +x {config.VM_IF_UP_SCRIPT}"
    run.run_cmd(host, chmod_cmd)


def _create_if_down_script() -> None:
    """
    Create if down script for vm
    """

    host = ""

    # create script
    script = f"""#!/bin/bash

IP={config.IP_TOOL}
TAP=\\$1

# remove tap interface from bridge
\\$IP link set \\"\\$TAP\\" nomaster
\\$IP link set \\"\\$TAP\\" promisc off
\\$IP link set \\"\\$TAP\\" down
"""
    cat_cmd = f"{config.CAT_TOOL} <<-\\\"EOF\\\" > " \
        f"{config.VM_IF_DOWN_SCRIPT}\n{script}EOF"
    run.run_cmd(host, cat_cmd)

    # make script executable
    chmod_cmd = f"config.CHMOD_TOOL +x {config.VM_IF_DOWN_SCRIPT}"
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
