from backend.monitoring.process_fault_rates import ProcessFaultRateMonitor


def test_first_sample_has_no_rates():
    times = iter([1.0])
    monitor = ProcessFaultRateMonitor(clock=lambda: next(times))

    processes = [{
        "pid": 10,
        "minor_faults_total": 100,
        "major_faults_total": 5,
    }]

    result = monitor.sample(processes)

    assert result[0]["minor_faults_per_second"] is None
    assert result[0]["major_faults_per_second"] is None


def test_fault_rates_are_calculated():
    times = iter([1.0, 3.0])
    monitor = ProcessFaultRateMonitor(clock=lambda: next(times))

    first = [{
        "pid": 10,
        "minor_faults_total": 100,
        "major_faults_total": 5,
    }]

    second = [{
        "pid": 10,
        "minor_faults_total": 160,
        "major_faults_total": 9,
    }]

    monitor.sample(first)
    result = monitor.sample(second)

    assert result[0]["minor_faults_per_second"] == 30
    assert result[0]["major_faults_per_second"] == 2


def test_counter_reset_does_not_create_negative_rates():
    times = iter([1.0, 2.0])
    monitor = ProcessFaultRateMonitor(clock=lambda: next(times))

    first = [{
        "pid": 10,
        "minor_faults_total": 100,
        "major_faults_total": 5,
    }]

    second = [{
        "pid": 10,
        "minor_faults_total": 10,
        "major_faults_total": 1,
    }]

    monitor.sample(first)
    result = monitor.sample(second)

    assert result[0]["minor_faults_per_second"] is None
    assert result[0]["major_faults_per_second"] is None
