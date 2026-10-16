from backend.monitoring.page_faults import PageFaultMonitor


def write_vmstat(path, minor, major):
    path.write_text(
        f"pgfault {minor}\npgmajfault {major}\n",
        encoding="utf-8",
    )


def test_first_sample_has_no_rates(tmp_path):
    vmstat = tmp_path / "vmstat"
    write_vmstat(vmstat, 100, 10)

    monitor = PageFaultMonitor(str(vmstat), clock=lambda: 1.0)
    result = monitor.sample()

    assert result["minor_faults_total"] == 100
    assert result["major_faults_total"] == 10
    assert result["minor_faults_per_second"] is None
    assert result["major_faults_per_second"] is None


def test_fault_rates_are_calculated(tmp_path):
    vmstat = tmp_path / "vmstat"
    write_vmstat(vmstat, 100, 10)

    times = iter([1.0, 3.0])
    monitor = PageFaultMonitor(str(vmstat), clock=lambda: next(times))

    monitor.sample()
    write_vmstat(vmstat, 120, 14)
    result = monitor.sample()

    assert result["minor_faults_per_second"] == 10.0
    assert result["major_faults_per_second"] == 2.0


def test_counter_reset_does_not_create_negative_rates(tmp_path):
    vmstat = tmp_path / "vmstat"
    write_vmstat(vmstat, 100, 10)

    times = iter([1.0, 2.0, 3.0])
    monitor = PageFaultMonitor(str(vmstat), clock=lambda: next(times))

    monitor.sample()
    write_vmstat(vmstat, 5, 1)
    reset_result = monitor.sample()

    assert reset_result["minor_faults_per_second"] is None
    assert reset_result["major_faults_per_second"] is None

    write_vmstat(vmstat, 15, 3)
    next_result = monitor.sample()

    assert next_result["minor_faults_per_second"] == 10.0
    assert next_result["major_faults_per_second"] == 2.0
