import pytest

from leapp import reporting
from leapp.libraries.actor import checkmicroarchitecture
from leapp.libraries.common.config.architecture import ARCH_SUPPORTED, ARCH_X86_64
from leapp.libraries.common.testutils import create_report_mocked, CurrentActorMocked, logger_mocked
from leapp.libraries.stdlib import api
from leapp.models import CPUInfo
from leapp.utils.report import is_inhibitor


@pytest.mark.parametrize("arch", [arch for arch in ARCH_SUPPORTED if not arch == ARCH_X86_64])
def test_not_x86_64_passes(monkeypatch, arch):
    """
    Test no report is generated on an architecture different from x86-64
    """

    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(api, 'current_logger', logger_mocked())
    monkeypatch.setattr(api, 'current_actor', CurrentActorMocked(arch=arch))

    checkmicroarchitecture.process()

    assert 'Architecture not x86-64. Skipping microarchitecture test.' in api.current_logger.infomsg
    assert not reporting.create_report.called


ENTIRE_V2_FLAG_SET = checkmicroarchitecture.X86_64_BASELINE_FLAGS + checkmicroarchitecture.X86_64_V2_FLAGS
ENTIRE_V3_FLAG_SET = ENTIRE_V2_FLAG_SET + checkmicroarchitecture.X86_64_V3_FLAGS


@pytest.mark.parametrize(
    ('target_ver', 'cpu_flags', 'dst_distro'),
    [
        ('9.0', ENTIRE_V2_FLAG_SET, 'rhel'),
        ('10.0', ENTIRE_V3_FLAG_SET, 'rhel'),
        ('9.0', ENTIRE_V2_FLAG_SET, 'almalinux'),
        # AlmaLinux 10 is built for x86-64-v2 as well, so v2 flags are enough
        ('10.0', ENTIRE_V2_FLAG_SET, 'almalinux'),
        ('10.0', ENTIRE_V3_FLAG_SET, 'almalinux'),
    ]
)
def test_valid_microarchitecture(monkeypatch, target_ver, cpu_flags, dst_distro):
    """
    Test no report is generated on a valid microarchitecture
    """

    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(api, 'current_logger', logger_mocked())

    monkeypatch.setattr(api, 'current_actor', CurrentActorMocked(arch=ARCH_X86_64, dst_ver=target_ver,
                                                                 dst_distro=dst_distro,
                                                                 msgs=[CPUInfo(flags=cpu_flags)]))

    checkmicroarchitecture.process()

    assert 'Architecture not x86-64. Skipping microarchitecture test.' not in api.current_logger.infomsg
    assert not reporting.create_report.called


@pytest.mark.parametrize(
    ('target_ver', 'cpu_flags', 'dst_distro'),
    (
        ('9.0', checkmicroarchitecture.X86_64_BASELINE_FLAGS, 'rhel'),
        ('10.0', ENTIRE_V2_FLAG_SET, 'rhel'),
        ('9.0', checkmicroarchitecture.X86_64_BASELINE_FLAGS, 'almalinux'),
        # AlmaLinux 10 still requires v2 as the baseline
        ('10.0', checkmicroarchitecture.X86_64_BASELINE_FLAGS, 'almalinux'),
    )
)
def test_invalid_microarchitecture(monkeypatch, target_ver, cpu_flags, dst_distro):
    """
    Test report is generated on x86-64 architecture with invalid microarchitecture and the upgrade is inhibited
    """
    cpu_info = CPUInfo(flags=cpu_flags)
    monkeypatch.setattr(reporting, "create_report", create_report_mocked())
    monkeypatch.setattr(api, 'current_logger', logger_mocked())
    monkeypatch.setattr(api, 'current_actor',
                        CurrentActorMocked(arch=ARCH_X86_64, msgs=[cpu_info], dst_ver=target_ver,
                                           dst_distro=dst_distro))

    checkmicroarchitecture.process()

    produced_title = reporting.create_report.report_fields.get('title')
    produced_summary = reporting.create_report.report_fields.get('summary')

    assert 'Architecture not x86-64. Skipping microarchitecture test.' not in api.current_logger().infomsg
    assert reporting.create_report.called == 1
    assert 'microarchitecture is unsupported' in produced_title
    assert 'has a higher CPU requirement' in produced_summary
    assert reporting.create_report.report_fields['severity'] == reporting.Severity.HIGH
    assert is_inhibitor(reporting.create_report.report_fields)
