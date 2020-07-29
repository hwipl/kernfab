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
    bridge_name = "kernfabbr0"
    bridge_ip = "172.23.32.1/24"

    # add bridge device
    add_cmd = f"{ip_tool} link add name {bridge_name} type bridge"
    run.run_cmd(host, add_cmd)

    # make sure bridge device is up
    up_cmd = f"{ip_tool} link set {bridge_name} up"
    run.run_cmd(host, up_cmd)

    # set promiscuous mode on bridge device
    promisc_cmd = f"{ip_tool} link set {bridge_name} promisc on"
    run.run_cmd(host, promisc_cmd)

    # set ip address on bridge device
    ip_cmd = f"{ip_tool} address add {bridge_ip} dev {bridge_name}"
    run.run_cmd(host, ip_cmd)


def _stop_bridge() -> None:
    """
    Stop vm network bridge
    """

    host = ""
    ip_tool = "/usr/bin/ip"
    bridge_name = "kernfabbr0"
    bridge_ip = "172.23.32.1/24"

    # remove ip from bridge device
    ip_cmd = f"{ip_tool} address del {bridge_ip} dev {bridge_name}"
    run.run_cmd(host, ip_cmd)

    # turn promiscuous mode of on bridge device
    promisc_cmd = f"{ip_tool} link set {bridge_name} promisc off"
    run.run_cmd(host, promisc_cmd)

    # set bridge down
    down_cmd = f"{ip_tool} link set {bridge_name} down"
    run.run_cmd(host, down_cmd)

    # remove bridge device
    del_cmd = f"{ip_tool} link del name {bridge_name} type bridge"
    run.run_cmd(host, del_cmd)


def _start_dnsmasq() -> None:
    """
    Start dhcp and dns server for vms
    """

    host = ""
    dnsmasq_tool = "/usr/bin/dnsmasq"
    bridge_name = "kernfabbr0"
    pid_file = "/tmp/kernfab_vm_bridge_dnsmasq.pid"
    bridge_ip_range = "172.23.32.10,172.23.32.254"
    bridge_routes = "0.0.0.0/0,172.23.32.1"
    cmd = f"{dnsmasq_tool} " \
        f"--interface={bridge_name} " \
        "--bind-interfaces " \
        "--except-interface=lo " \
        f"--pid-file={pid_file} " \
        f"--dhcp-range={bridge_ip_range} " \
        f"--dhcp-option=option:classless-static-route,{bridge_routes}"

    if config.NUM_VMS > 8:
        print("too many VMs")
        return

    for i in range(config.NUM_VMS):
        mac_to_ip = f"52:54:00:00:00:0{i + 1},172.23.32.1{i + 1}"
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
    bridge_name = "kernfabbr0"

    # enable ip forwarding
    sysctl_tool = "/usr/bin/sysctl"
    fwd_cmd = f"{sysctl_tool} net.ipv4.conf.{bridge_name}.forwarding=1"
    run.run_cmd(host, fwd_cmd)

    # enable nat
    iptables_tool = "/usr/bin/iptables"
    prefix = "172.23.32.0/24"
    masq_cmd = f"{iptables_tool} -t nat -A POSTROUTING -s {prefix} " \
        "-j MASQUERADE"
    run.run_cmd(host, masq_cmd)

    out_cmd = f"{iptables_tool} -A FORWARD -m conntrack " \
        f"--ctstate RELATED,ESTABLISHED -o {bridge_name} -d {prefix} -j ACCEPT"
    run.run_cmd(host, out_cmd)

    in_cmd = f"{iptables_tool} -A FORWARD -i {bridge_name} -s {prefix} " \
        "-j ACCEPT"
    run.run_cmd(host, in_cmd)


def _stop_nat() -> None:
    """
    Stop nat for vms
    """

    host = ""
    bridge_name = "kernfabbr0"

    # disable ip forwarding
    sysctl_tool = "/usr/bin/sysctl"
    fwd_cmd = f"{sysctl_tool} net.ipv4.conf.{bridge_name}.forwarding=0"
    run.run_cmd(host, fwd_cmd)

    # disable nat
    iptables_tool = "/usr/bin/iptables"
    prefix = "172.23.32.0/24"
    masq_cmd = f"{iptables_tool} -t nat -D POSTROUTING -s {prefix} " \
        "-j MASQUERADE"
    run.run_cmd(host, masq_cmd)

    out_cmd = f"{iptables_tool} -D FORWARD -m conntrack " \
        f"--ctstate RELATED,ESTABLISHED -o {bridge_name} -d {prefix} -j ACCEPT"
    run.run_cmd(host, out_cmd)

    in_cmd = f"{iptables_tool} -D FORWARD -i {bridge_name} -s {prefix} " \
        "-j ACCEPT"
    run.run_cmd(host, in_cmd)


def _create_if_up_script() -> None:
    """
    Create if up script for vm
    """

    host = ""

    # create script
    ip_tool = "/usr/bin/ip"
    bridge_name = "kernfabbr0"
    script = f"""#!/bin/bash

IP={ip_tool}
BRIDGE={bridge_name}
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
