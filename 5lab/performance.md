# Performance test

|                 |               |            |
|-----------------|---------------|------------|
| Metric          | Without Redis | With Redis |
| Duration        | 30s           | 30s        |
| Threads         | 4             | 4          |
| Connections     | 100           | 100        |
| Avg Latency     | 56.67ms       | 13.43ms    |
| Latency Stdev   | 24.48ms       | 6.64ms     |
| Max Latency     | 1.08s         | 340.25ms   |
| Latency Stdev   | 93.38%        | 96.07%     |
| Avg Req/Sec     | 254.98        | 890        |
| Req/Sec Stdev   | 84.30         | 72.77      |
| Max Req/Sec     | 478           | 932k       |
| Req/Sec Stdev   | 65.46%        | 70.48%     |
| Total Requests  | 26,456        | 99,148     |
| Total Data Read | 3.35MB        | 21.22MB    |
| Requests/sec    | 340.34        | 934.87     |
| Transfer/sec    | 235.62KB      | 936KB      | 