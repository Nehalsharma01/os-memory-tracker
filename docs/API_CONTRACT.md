# OS Memory Tracker — API Contract

Version: 1.0 (initial proposal)

Base URL:
http://127.0.0.1:5000

All endpoints return JSON.

## 1. Health Check

GET /api/health

Response:
{
  "status": "ok",
  "service": "os-memory-tracker"
}

## 2. System Memory

GET /api/system/memory

Response:
{
  "timestamp": "ISO-8601 timestamp",
  "source": "linux-proc",
  "memory": {
    "total_kb": 0,
    "available_kb": 0,
    "used_kb": 0,
    "swap_total_kb": 0,
    "swap_free_kb": 0,
    "swap_used_kb": 0
  }
}

All numeric values are examples/placeholders in this document.
The implementation must return actual measurements.

## 3. System-Wide Page Faults

GET /api/system/page-faults

Response:
{
  "timestamp": "ISO-8601 timestamp",
  "source": "linux-proc",
  "minor_faults_total": 0,
  "major_faults_total": 0,
  "minor_faults_per_second": 0.0,
  "major_faults_per_second": 0.0
}

Cumulative counters and rates are different measurements.
Rates must be calculated from counter differences over elapsed time.
Do not invent rates before a valid sampling interval exists.

## 4. Process List

GET /api/processes

Response:
{
  "timestamp": "ISO-8601 timestamp",
  "processes": [
    {
      "pid": 1234,
      "name": "example",
      "minor_faults": 0,
      "major_faults": 0
    }
  ]
}

The example process is illustrative only.

## 5. Process Details

GET /api/processes/{pid}

Response:
{
  "timestamp": "ISO-8601 timestamp",
  "pid": 1234,
  "name": "example",
  "minor_faults": 0,
  "major_faults": 0
}

If the process does not exist or access is denied, return an
appropriate HTTP error with a JSON error message.

## General Rules

- Timestamps must be ISO-8601 formatted.
- Memory values are reported in KiB (1024 bytes).
- Page-fault counters are cumulative since process/system startup
  where the Linux interface provides cumulative counters.
- Rates are measured as counter changes divided by elapsed time.
- Process information may change between requests.
- Processes can exit during sampling; handle this safely.
- Monitoring is limited to information visible inside the Linux
  environment. WSL statistics are not automatically equivalent
  to unrestricted Windows-wide process statistics.
- Do not expose secrets or unnecessary personal information.

## Fragmentation Simulator

The fragmentation simulator is an independently testable module
owned by Person 2. Its algorithm interface and result format must
be documented by Person 2 before dashboard integration.

External fragmentation:
(1 - largest_free_block / total_free_memory) * 100

If total_free_memory is zero, report 0% by documented convention.
## Process Monitoring

### GET /api/processes

Returns accessible Linux processes, sorted by resident memory
in descending order.

Each process contains:
- `pid`: Process ID
- `name`: Process name
- `memory_rss_kb`: Resident memory in KiB
- `memory_virtual_kb`: Virtual memory in KiB
- `minor_faults_total`: Cumulative minor page faults
- `major_faults_total`: Cumulative major page faults

Response also includes `timestamp`, `source`, and `count`.

### GET /api/processes/{pid}

Returns monitoring statistics for one process.

Returns HTTP 404 if the process cannot be found or accessed.

## Per-Process Page-Fault Rates

The `GET /api/processes` endpoint returns these cumulative counters and rate fields for each process:

- `minor_faults_total`: Cumulative minor page faults.
- `major_faults_total`: Cumulative major page faults.
- `minor_faults_per_second`: Minor page-fault rate per second.
- `major_faults_per_second`: Major page-fault rate per second.
- `memory_rss_kb`: Resident memory in KiB.
- `memory_virtual_kb`: Virtual memory in KiB.

Rates are calculated from counter differences divided by elapsed time. Rates are `null` on the first sample and when a valid rate cannot be calculated, such as when counters decrease.

The `GET /api/processes/{pid}` endpoint currently returns cumulative counters and memory statistics, but not rate fields.

These measurements describe the Linux environment visible to the application. In WSL, they do not automatically represent all Windows processes or host memory.
