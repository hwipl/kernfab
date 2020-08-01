# kernfab

Kernfab is a Linux kernel development tool based on fabric (and invoke). In a
kernel source code directory, you can use it to build a kernel, install it to
virtual machine (VM) images and start the VMs. Kernfab uses KVM and the qemu
tools for the VMs. A bridge interconnects the VMs, dnsmasq provides the VMs
with DHCP and DNS, and NAT enables the VMs to communicate with peers outside
the bridge.

Note: Currently, most configuration is hard-coded in config.py. Also, it was
developed with and for Arch Linux and might not even work with other
distributions.

## Usage

You can run `kernfab` with the following command line arguments:

```
usage: kernfab [-h] [--version] {build,install,start,stop,qemu} ...

Run the kernfab linux kernel development tool.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

subcommands:
  valid subcommands

  {build,install,start,stop,qemu}
                        list of subcommands
    build               build kernel
    install             install kernel
    start               start vm(s) with kernel
    stop                stop vm(s) with kernel
    qemu                qemu commands
```

You can run the subcommands with `-h` or `--help` to get additional info.

### Examples

Building a kernel:

```console
$ kernfab build
```

Installing a kernel identified by its version (here `5.8.0-rc4+`) to VM images:

```console
$ sudo kernfab install 5.8.0-rc4+
```

Running the VMs with with kernel

```console
$ sudo kernfab start
```

Stopping the kernfab VMs:

```console
$ sudo kernfab stop
```
