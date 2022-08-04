from leapp.libraries.common.repomaputils import (
    scan_repomaps,
    read_or_fetch_repofile,
    BASE_REPOMAP_DIR,
    REPOMAP_FILE,
)
from leapp.libraries.stdlib import api


def scan_repositories(read_repofile_func=read_or_fetch_repofile):
    """
    Scan the repository mapping file and produce RepositoriesMap msg.

    See the description of the actor for more details.
    """
    reposmap = scan_repomaps(REPOMAP_FILE, BASE_REPOMAP_DIR, read_repofile_func)

    api.produce(reposmap)
