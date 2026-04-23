**Before doing anything, please read the [leapp-repository documentation](https://leapp-repository.readthedocs.io/) and [ELevate wiki](https://wiki.almalinux.org/elevate/)**

Also, you could find the [Leapp framework documentation](https://leapp.readthedocs.io/) useful to read.

---

## Supported Distributions

This fork extends leapp in-place upgrade support beyond RHEL to the following distributions:

- **AlmaLinux** (8 → 9, 9 → 10)
- **AlmaLinux Kitten** (as a CentOS Stream equivalent)
- **CentOS Stream** (8 → 9, 9 → 10)

Cross-distribution upgrades (e.g. CentOS 7 → AlmaLinux 8) are also supported through the [ELevate](https://almalinux.org/elevate/) project.

## AlmaLinux-specific Enhancements

This fork adds a few capabilities on top of upstream `leapp-repository` that are specific to AlmaLinux targets.

### Upgrades to AlmaLinux 10 on `x86-64-v2` hardware

RHEL 10 dropped support for the `x86-64-v2` microarchitecture level and requires `x86-64-v3`. AlmaLinux 10 is additionally built for `x86-64-v2`, so this fork relaxes the microarchitecture inhibitor when the upgrade target distro is AlmaLinux:

- Target distro `almalinux`, major version `10` → requires `x86-64-v2` (baseline + v2 flags).
- Target distro `rhel` / `centos`, major version `10` → requires `x86-64-v3` as upstream.
- Target major version `9` → requires `x86-64-v2` for all distros.

This enables in-place upgrades to AlmaLinux 10 on CPUs that only support `x86-64-v2` when paired with the matching v2 target userspace (see below).

### Custom rootfs for target userspace bootstrap

The `targetuserspacecreator` actor can use a pre-built rootfs instead of bootstrapping the target userspace container via `dnf install --installroot`. Two methods are supported, checked in order of priority:

1. **Local tarball** — place a `.tar`, `.tar.xz`, `.tar.gz`, or `.tar.bz2` archive in `/etc/leapp/files/rootfs/`. The first archive found (sorted by name) is extracted directly into the target userspace directory.
2. **Container image** — set the environment variable `LEAPP_DEVEL_ROOTFS_CONTAINER_IMAGE` to a container image reference (e.g. `quay.io/almalinuxorg/almalinux:10`). The image is pulled via `podman`, exported as a flat filesystem, and extracted into the userspace directory. The platform can be selected with `LEAPP_DEVEL_ROOTFS_CONTAINER_PLATFORM` (e.g. `linux/amd64/v2`).

If neither is configured, the original DNF-based bootstrap is used.

Combined with the `x86-64-v2` microarchitecture relaxation above, this makes it possible to upgrade an AlmaLinux 9 system running on a v2-only CPU to AlmaLinux 10 by pointing leapp at a `linux/amd64/v2` AlmaLinux 10 container image or rootfs tarball.

## 3rd Party Repository Support (ELevate Vendors)

In addition to the base distribution repositories, this fork includes vendor integration for popular 3rd party repositories. Vendor data files are stored under `/etc/leapp/files/vendors.d/` and can provide:

- **Repository mappings** (`<vendor>_map.json`) — maps source repositories to their target equivalents
- **PES event files** (`<vendor>_pes.json`) — package migration events (install, remove, replace, reinstall) for vendor packages
- **GPG signatures** (`<vendor>.sigs`) — GPG key fingerprints for vendor-signed packages
- **GPG public keys** (`rpm-gpg/`) — trusted GPG keys imported during the upgrade

### Supported 3rd Party Repositories

The following vendors are supported via [ELevate](https://almalinux.org/elevate/):

- EPEL
- Docker CE
- MariaDB
- Nginx
- PostgreSQL
- Imunify
- KernelCare
- TuxCare
- ELevate

---

## Troubleshooting

### Where can I report an issue or RFE related to the framework or other actors?

- GitHub issues are preferred:
  - Leapp framework: [https://github.com/oamg/leapp/issues/new/choose](https://github.com/oamg/leapp/issues/new/choose)
  - Leapp actors: [https://github.com/almalinux/leapp-repository/issues/new/choose](https://github.com/almalinux/leapp-repository/issues/new/choose)
  - Leapp data: [https://github.com/almalinux/leapp-data/issues/new/choose](https://github.com/almalinux/leapp-data/issues/new/choose)

- When filing an issue, include:
  - Steps to reproduce the issue
  - *All files in /var/log/leapp*
  - */var/lib/leapp/leapp.db*
  - *journalctl*
  - If you want, you can optionally send any other relevant information (e.g. storage, network)

**For your convenience you can pack all logs with this command:**

`# tar -czf leapp-logs.tgz /var/log/leapp /var/lib/leapp/leapp.db`

Then you may attach only the `leapp-logs.tgz` file.
