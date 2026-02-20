**Before doing anything, please read the [leapp-repository documentation](https://leapp-repository.readthedocs.io/) and [ELevate wiki](https://wiki.almalinux.org/elevate/)**

Also, you could find the [Leapp framework documentation](https://leapp.readthedocs.io/) useful to read.

---

## Supported Distributions

This fork extends leapp in-place upgrade support beyond RHEL to the following distributions:

- **AlmaLinux** (8 → 9, 9 → 10)
- **AlmaLinux Kitten** (as a CentOS Stream equivalent)
- **CentOS Stream** (8 → 9, 9 → 10)

Cross-distribution upgrades (e.g. CentOS 7 → AlmaLinux 8) are also supported through the [ELevate](https://almalinux.org/elevate/) project.

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
  - If you want, you can optionally send anything else would you like to provide (e.g. storage info)

**For your convenience you can pack all logs with this command:**

`# tar -czf leapp-logs.tgz /var/log/leapp /var/lib/leapp/leapp.db`

Then you may attach only the `leapp-logs.tgz` file.
