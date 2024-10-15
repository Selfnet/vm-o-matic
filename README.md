# vm-o-matic

vm-o-matic is how we create VMs running in libvirtd at Selfnet. Its 
current incarnation is based on cloud-init after previous attempts 
using deboostrap turned out to be too slow.

It automates everything from creating the disk image in ceph, creating 
the ISO image with the information for cloud-init to generating the 
vm definition and LDAP snippet.

Since it's purpose built for our particular environment and 
requirements at Selfnet, don't expect that you can use this out of the 
box.
