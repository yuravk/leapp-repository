import json
import os

from leapp.exceptions import StopActorExecutionError
from leapp.libraries.stdlib import api
from leapp.models import VendorSignatures


def get_distribution_data(distribution):
    distributions_path = api.get_common_folder_path('distro')

    distribution_config = os.path.join(distributions_path, distribution, 'gpg-signatures.json')
    if os.path.exists(distribution_config):
        with open(distribution_config) as distro_config_file:
            distro_config_json = json.load(distro_config_file)
    else:
        raise StopActorExecutionError(
            'Cannot find distribution signature configuration.',
            details={'Problem': 'Distribution {} was not found in {}.'.format(distribution, distributions_path)})

    # Extend with Vendors signatures
    for siglist in api.consume(VendorSignatures):          
        distro_config_json["keys"].extend(siglist.sigs)

    return distro_config_json
