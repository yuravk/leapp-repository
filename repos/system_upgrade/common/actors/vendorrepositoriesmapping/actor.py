from leapp.actors import Actor
from leapp.libraries.common.repomaputils import scan_vendor_repomaps, VENDOR_REPOMAP_DIR
from leapp.models import VendorRepositoriesMapCollection, RepositoriesMap
from leapp.tags import FactsPhaseTag, IPUWorkflowTag


class VendorRepositoriesMapping(Actor):
    """
    Scan the vendor repository mapping files and provide the data to other actors.
    """

    name = "vendor_repositories_mapping"
    consumes = ()
    produces = (RepositoriesMap, VendorRepositoriesMapCollection,)
    tags = (IPUWorkflowTag, FactsPhaseTag.Before)

    def process(self):
        vendor_repomap_collection = scan_vendor_repomaps(VENDOR_REPOMAP_DIR)
        self.produce(vendor_repomap_collection)
        for repomap in vendor_repomap_collection.maps:
            self.produce(repomap)
