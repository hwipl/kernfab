"""
Module for vm networking
"""

from kernfab import run


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


def start() -> None:
    """
    Start vm network
    """

    _start_bridge()


def stop() -> None:
    """
    Stop vm network
    """

    _stop_bridge()
