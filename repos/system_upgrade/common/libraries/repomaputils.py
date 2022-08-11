import os
import io  # Python2/Python3 compatible IO (open etc.)

from leapp.exceptions import StopActorExecutionError
from leapp.libraries.common import config
from leapp.libraries.common.fetch import read_or_fetch
from leapp.libraries.stdlib import api
from leapp.models import RepositoriesMap, RepositoryMap, VendorRepositoriesMapCollection
from leapp.models.fields import ModelViolationError

REPOMAP_FILE = "repomap.csv"
"""Path to the repository mapping file."""
BASE_REPOMAP_DIR = "/etc/leapp/files"
VENDOR_REPOMAP_DIR = "/etc/leapp/files/vendors.d"


def _raise_error(msg, details):
    raise StopActorExecutionError(
        msg,
        details={
            "details": details,
            "hint": (
                "Read documentation at the following link for more"
                " information about how to retrieve the valid file:"
                " https://access.redhat.com/articles/3664871"
            ),
        },
    )


def read_local(
    filename,
    directory=BASE_REPOMAP_DIR,
    allow_empty=False,
    encoding="utf-8",
):
    logger = api.current_logger()
    local_path = os.path.join(directory, filename)
    try:
        with io.open(local_path, encoding=encoding) as f:
            data = f.read()
            if not allow_empty and not data:
                _raise_error(
                    local_path, "File {} exists but is empty".format(local_path)
                )
            logger.warning(
                "File {lp} successfully read ({l} bytes)".format(
                    lp=local_path, l=len(data)
                )
            )
            return [line.strip() for line in data.splitlines()]
    except EnvironmentError:
        _raise_error(
            local_path, "File {} exists but couldn't be read".format(local_path)
        )
    except Exception as e:
        raise e


def read_or_fetch_repofile(repofile, directory):
    contents = read_or_fetch(repofile, directory)
    return [line.strip() for line in contents.splitlines()]


def scan_repomaps(repomap_file, repomap_dir, read_repofile_func=read_or_fetch_repofile):
    """
    Scan the repository mapping file and produce RepositoriesMap msg.

    See the description of the actor for more details.
    """
    _exp_src_prod_type = config.get_product_type("source")
    _exp_dst_prod_type = config.get_product_type("target")

    repositories = []
    line_num = 0
    for line in read_repofile_func(repomap_file, repomap_dir)[1:]:
        line_num += 1

        api.current_logger().debug("Grabbing line {} of file {}: \"{}\"".format(line_num, repomap_file, line))

        # skip empty lines and comments
        if not line or line.startswith("#"):
            api.current_logger().debug("Line skipped")
            continue

        try:
            (
                from_repoid,
                to_repoid,
                to_pes_repo,
                from_minor_version,
                to_minor_version,
                arch,
                repo_type,
                src_prod_type,
                dst_prod_type,
            ) = line.split(",")

            # filter out records irrelevant for this run
            if (
                arch != api.current_actor().configuration.architecture
                or _exp_src_prod_type != src_prod_type
                or _exp_dst_prod_type != dst_prod_type
            ):
                api.current_logger().debug("Line filtered out")
                continue

            new_repo_map = RepositoryMap(
                    from_repoid=from_repoid,
                    to_repoid=to_repoid,
                    to_pes_repo=to_pes_repo,
                    from_minor_version=from_minor_version,
                    to_minor_version=to_minor_version,
                    arch=arch,
                    repo_type=repo_type,
                )

            api.current_logger().debug("Map added: {}".format(new_repo_map.dump()))
            repositories.append(new_repo_map)

        except (ModelViolationError, ValueError) as err:
            _raise_error(
                "The repository mapping file is invalid. It is possible the file is out of date.",
                "Offending line number: {} ({}).".format(line_num, err),
            )

    if not repositories:
        _raise_error(
            "The repository mapping file is invalid. Could not find any repository mapping record.",
            "",
        )

    return RepositoriesMap(file=repomap_file, repositories=repositories)


def scan_vendor_repomaps(repomap_dir):
    if not os.path.isdir(repomap_dir):
        api.current_logger().debug(
            "The {} directory doesn't exist. Nothing to do.".format(repomap_dir)
        )
        return None

    vendor_maps = []

    for repomap_name in os.listdir(repomap_dir):
        # Only scan the .csv files, those are the maps.
        if not repomap_name.endswith(".csv"):
            continue
        scanned_map = scan_repomaps(
            repomap_name, repomap_dir, read_repofile_func=read_local
        )
        vendor_maps.append(scanned_map)

    return VendorRepositoriesMapCollection(maps=vendor_maps)
