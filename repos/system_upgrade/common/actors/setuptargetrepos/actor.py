from leapp.actors import Actor
from leapp.libraries.actor import setuptargetrepos
from leapp.models import (
    CustomTargetRepository,
    InstalledRPM,
    RepositoriesBlacklisted,
    RepositoriesFacts,
    RepositoriesMapping,
    RepositoriesSetupTasks,
    RHUIInfo,
    SkippedRepositories,
    TargetRepositories,
    UsedRepositories,
    VendorCustomTargetRepositoryList
)
from leapp.tags import FactsPhaseTag, IPUWorkflowTag


class SetupTargetRepos(Actor):
    """
    Produces list of repositories that should be available to be used by Upgrade process.

    Based on current set of Red Hat Enterprise Linux repositories, produces the list of target
    repositories. Additionally process request to use custom repositories during the upgrade
    transaction.
    """

    name = 'setuptargetrepos'
    consumes = (CustomTargetRepository,
                InstalledRPM,
                RepositoriesSetupTasks,
                RepositoriesMapping,
                RepositoriesFacts,
                RepositoriesBlacklisted,
                RHUIInfo,
                UsedRepositories,
                VendorCustomTargetRepositoryList)
    produces = (TargetRepositories, SkippedRepositories)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):
        setuptargetrepos.process()
