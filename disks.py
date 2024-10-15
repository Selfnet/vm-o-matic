from util import log, subprocess, contextmanager


class Ceph_Disk(object):
    """Provide interfaces to create and map ceph disks"""

    def __init__(self, rbd_opts, pool=None):
        self.rbd_opts = rbd_opts
        self.pool = pool or "vms"

    def get_name(self, name):
        return f"{self.pool}/{name}"

    def create(self, name, size_gb):
        name = self.get_name(name)
        log("creating disk", name)
        r = subprocess.run(
            ["rbd"]
            + self.rbd_opts
            + ["-s", f"{size_gb:.0f}G", "--image-feature=layering", "create", name],
            check=True,
        )
        return r.returncode == 0

    @contextmanager
    def map(self, name):
        dev = (
            subprocess.check_output(
                ["rbd"] + self.rbd_opts + ["map", self.get_name(name)]
            )
            .decode()
            .strip()
        )
        try:
            yield dev
        finally:
            subprocess.run(["rbd", "unmap", dev], check=True)


class QEMU_Disk(object):
    """Provide functions to create and map qcow2 images"""

    def __init__(self, path):
        self.path = path

        # Check whether nbd is correctly loaded
        try:
            log("checking nbd module for maxmimum number of partitions")
            with open("/sys/module/nbd/parameters/max_part", "r") as param:
                max_part = param.read()
                if int(max_part) < 3:
                    log("Insufficient number of allowed nbd partitions.")
                    exit("Try 'rmmod nbd && modprobe nbd max_part=16'")
                else:
                    log(f"You are good to go with {max_part} maximum partitions")
        except:
            exit("Is nbd loaded? Try 'modprobe nbd max_part=16'")

    def get_path(self, name):
        return f"{self.path}{name}.qcow2"

    def create(self, name, size_gb):
        path = self.get_path(name)
        log(f"creating qcow2 image {name} in {path}")
        r = subprocess.run(
            [
                "qemu-img",
                "create",
                "-f",
                "qcow2",
                path,
                f"{size_gb:.0f}G",
            ],
            check=True,
        )
        return r.returncode == 0

    @contextmanager
    def map(self, name):
        # Maybe build checks here for multiple concurrent deployments
        dev = "/dev/nbd0"
        subprocess.run(["qemu-nbd", "-c", dev, self.get_path(name)])
        try:
            yield dev
        finally:
            subprocess.run(["qemu-nbd", "-d", dev], check=True)
