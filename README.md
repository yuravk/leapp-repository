**Before doing anything, please read
[Leapp framework documentation](https://leapp.readthedocs.io/).**

---

## Troubleshooting

### Where can I report an issue or RFE related to the framework or other actors?

- GitHub issues are preferred:
  - Leapp framework: [https://github.com/oamg/leapp/issues/new/choose](https://github.com/oamg/leapp/issues/new/choose)
  - Leapp actors: [https://github.com/oamg/leapp-repository/issues/new/choose](https://github.com/oamg/leapp-repository/issues/new/choose)

- When filing an issue, include:
  - Steps to reproduce the issue
  - *All files in /var/log/leapp*
  - */var/lib/leapp/leapp.db*
  - *journalctl*
  - If you want, you can optionally send anything else would you like to provide (e.g. storage info)

**For your convenience you can pack all logs with this command:**

`# tar -czf leapp-logs.tgz /var/log/leapp /var/lib/leapp/leapp.db`

Then you may attach only the `leapp-logs.tgz` file.

### Where can I seek help?
We’ll gladly answer your questions and lead you to through any troubles with the
actor development.

You can reach us at IRC: `#leapp` on freenode.


## Third-party integration

If you would like to add your **signed** 3rd party packages into the upgrade process, you can use the third-party integration mechanism.

There are four components for adding your information to the elevation process:
- <vendor_name>.csv: repository mapping file
- <vendor_name>.repo: package repository information
- <vendor_name>.sigs: list of package signatures of vendor repositories
- <vendor_name>.json: package migration event list

All these files **must** have the same <vendor_name> part.

### Repository mapping file

This CSV file provides information on mappings between source system repositories (repositories present on the system being upgraded) and target system repositories (package repositories to be used during the upgrade).

The first line of the file, per CSV format, should contain the headers. Standard headers for vendor.csv files look like this:

```CSV
Source system repoid,Target system repoid in custom repo file,Target system repo name in PES,Source system minor versions,Target system minor versions,architecture,type (rpm/srpm/debuginfo),source product type (ga/beta,htb),target product type (ga/beta/htb)
```

Following lines should contain the repository map entries. As an example:

```CSV
Source system repoid,Target system repoid in custom repo file,Target system repo name in PES,Source system minor versions,Target system minor versions,architecture,type (rpm/srpm/debuginfo),source product type (ga/beta,htb),target product type (ga/beta/htb)

source-repoid,target-custom-repoid,target-pes-repoid,all,all,x86_64,rpm,ga,ga
```

**Source system repoid** is the ID of a repository that is expected to be present on the system before the upgrade.

**Target system repoid in custom repo file** is the ID of a repository listed in the associated package repository information (<vendor_name>.repo) file. It is supposed to be used during the upgrade process.

**Target system repo name in PES** is the ID which is used to refer to the target system repository in the package migration event list (<vendor_name>.json).

**Repository types**:
- rpm: normal RPM packages
- srpm: source packages
- debuginfo: packages with debug information

**Product types**:
- GA: general availability repositories
- Beta: beta-testing repositories
- HTB: High Touch Beta repositories

The repository mapping file also defines whether a vendor's packages will be included into the upgrade process at all. If at least one source repository listed in the file is present on the system, the vendor is considered active, and package repositories/PES events are enabled - otherwise, they will not affect the upgrade process.

In the above example, vendor's data (including the .repo and .json files) will affect the upgrade process only if a repository with `source-repoid` ID is present on the system.


### Package repository information

This file defines the vendor's package repositories to be used during the upgrade.

The file has the same format normal YUM/DNF package repository files do.

> NOTE: The repositories listed in this file are only used *during* the upgrade. Package repositories on the post-upgrade system should be provided through updated packages or custom repository deployment.

### Package signature list

This file should contain the list of public signature headers that the packages are signed with, one entry per line.

You can find signature headers for your packages by running the following command:

`rpm -qa --queryformat "%{NAME} || %|DSAHEADER?{%{DSAHEADER:pgpsig}}:{%|RSAHEADER?{%{RSAHEADER:pgpsig}}:{(none)}|}|\n" <PACKAGE_NAME>`

rpm will return an entry like the following:
`package-name || DSA/SHA1, Mon Aug 23 08:17:13 2021, Key ID 8c55a6628608cb71`

The value after "Key ID", in this case, `8c55a6628608cb71`, is what you should put into the signature list file.

### Package migration event list

The Leapp upgrade process uses information from the AlmaLinux PES (Package Evolution System) to keep track of how packages change between the OS versions. This data is located in `leapp-data/files/<target_system>/vendors.d/<vendor_name>.json` in the GitHub repository and in `/etc/leapp/files/vendors.d/<vendor_name>.json` on a system being upgraded.

To add new rules to the list, add a new entry to the `packageinfo` array.
**Important**: actions from PES json files will be in effect only for those packages that are signed **and** have their signatures in one of the active <vendor_name>.sigs files. Unsigned packages will be updated only if some signed package requires a new version, otherwise they will by left as they are.

Required fields:

- action: what action to perform on the listed package
  - 0 - present
  - 1 - removed
  - 2 - deprecated
  - 3 - replaced
  - 4 - split
  - 5 - merged
  - 6 - moved to new repository
  - 7 - renamed
- arches: what system architectures the listed entry relates to
- id: entry ID, must be unique
- in_packageset: set of packages on the old system
- out_packageset: set of packages to switch to, empty if removed or deprecated
- initial_release: source OS release
- release: target OS release

`in_packageset` and `out_packageset` have the following format:

```json
      "in_packageset": {
        "package": [
          {
            "module_stream": null,
            "name": "PackageKit",
            "repository": "base"
          },
          {
            "module_stream": null,
            "name": "PackageKit-yum",
            "repository": "base"
          }
        ],
        "set_id": 1592
      },
```

For `in_packageset`, `repository` field defines the package repository the package was installed from on the source system.
For `out_packageset`, `repository` field for packages should be the same as the "Target system repo name in PES" field in the associated vendor repository mapping file.
Warning: leapp doesn't force packages from out_packageset to be installed from the specific repository; instead, it enables repo from out_packageset and then dnf installs the latest package version from all enabled repos.

To take the above repository map example:

```CSV
Source system repoid,Target system repoid in custom repo file,Target system repo name in PES,Source system minor versions,Target system minor versions,architecture,type (rpm/srpm/debuginfo),source product type (ga/beta,htb),target product type (ga/beta/htb)

source-repoid,target-custom-repoid,target-pes-repoid,all,all,x86_64,rpm,ga,ga
```

For this configuration, `in_packageset` entries would have `source-repoid` as the `repository` field, and `out_packageset` would have `target-pes-repoid` in theirs.

Please refer to [PES contribution guide](https://wiki.almalinux.org/elevate/Contribution-guide.html) for additional information on entry fields.

### Providing the data

Once you've prepared the vendor data for migration, you can make a pull request to https://github.com/AlmaLinux/leapp-data/ to make it available publicly.
Files should be placed in `files/<target-system>/vendors.d/`.

Alternatively, you can deploy the vendor files on a system prior to starting the upgrade. In this case, place the files into the folder `/etc/leapp/files/vendors.d/`.
