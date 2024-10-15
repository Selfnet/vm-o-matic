fstab = """
UUID=${root_uuid} / ext4 defaults 0 1
UUID=${swap_uuid} none swap sw 0 0
"""

bgpnet = """
source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto ${iface}
iface ${iface} inet static
	address ${ip4}/32
	post-up ip route add 141.70.124.10 dev ${iface}
	post-up ip route add default via 141.70.124.10

iface ${iface} inet6 static
	address ${ip6}/128
	post-up ip route add 2001:7c7:2100::1 dev ${iface}
	post-up ip route add default via 2001:7c7:2100::1
"""

bridgenet = """
source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto ${iface}
iface ${iface} inet static
	address ${ip4}/27
	gateway 141.70.127.129

iface ${iface} inet6 static
	address ${ip6}/64
	gateway 2001:7c7:2100:104::1
"""

setup = """
#!/bin/bash
set -e
locale-gen
update-locale LANG=en_US.UTF-8
grub-install ${dev} --modules="biosdisk part_msdos"
update-grub
sed -i 's:${part_root}:/dev/vda2:g' /boot/grub/grub.cfg
systemctl enable nftables
ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
passwd
"""

partitions = """
label: dos
unit: sectors

size=${swap_size}, type=82
type=83, bootable
"""

firewall = """
#!/usr/sbin/nft -f

flush ruleset

table inet firewall {
        chain input {
                type filter hook input priority 0; policy drop;
                ct state established,related accept
                ct state invalid drop
                iif "lo" accept
                ip6 nexthdr ipv6-icmp accept
                ip protocol icmp accept
                tcp dport ssh jump ssh
                reject
        }

        chain forward {
                type filter hook forward priority 0; policy drop;
        }

        chain output {
                type filter hook output priority 0; policy accept;
        }

        chain ssh {
                ip saddr { 141.70.126.251, 141.70.127.251, 141.70.127.59} accept #login-{1,2,3}
                ip6 saddr { 2001:7c7:2100:700::1, 2001:7c7:2100:701::1, 2001:7c7:2100:401::35 } accept #login-{1,2,3}
        }
}
"""

libvirt_definition = """
<domain type='kvm'>
  <name>${hostname}</name>
  <memory unit='KiB'>${memory}</memory>
  <currentMemory unit='KiB'>${memory}</currentMemory>
  <vcpu placement='static'>${cpu}</vcpu>
  <resource>
    <partition>/machine</partition>
  </resource>
  <os>
    <type arch='x86_64' machine='pc-1.1'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <cpu mode="host-model" check="none"/>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/bin/kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='${vm_disk}.qcow2'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <interface type='bridge'>
      <source bridge='${bridge}'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <video>
      <model type='cirrus' vram='9216' heads='1'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </memballoon>
    <rng model="virtio">
      <backend model="random">/dev/urandom</backend>
    </rng>
  </devices>
</domain>
"""

sudo_ldap = """
add cn=${hostname},ou=sudoers,dc=selfnet,dc=de
objectClass: top
objectClass: sudoRole
sudoCommand: ALL
sudoRunAs: ALL
cn: ${hostname}
description: sudo auf ${hostname}
sudoHost: ${ip4}
sudoHost: ${ip6}
sudoHost: ${hostname}.server.selfnet.de
"""
