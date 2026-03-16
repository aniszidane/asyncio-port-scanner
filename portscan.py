#!/usr/bin/env python3
"""Asyncio Port Scanner

- Reads targets (IP or domain) from a text file
- Scans a list of TCP ports concurrently using asyncio
- Writes results to JSON and CSV

Safety:
  Only scan systems you own or have explicit permission to test.
"""

import argparse
import asyncio
import csv
import json
import socket
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 465, 587,
    631, 993, 995, 1433, 1521, 2049, 2375, 2376, 3306, 3389, 5432, 5900,
    6379, 8080, 8443, 9200, 27017,
]


async def resolve_host(host: str) -> Optional[str]:
    """Resolve a domain to an IP.

    If `host` is already an IP, return it as-is.
    Returns None if resolution fails.
    """
    try:
        socket.inet_aton(host)
        return host
    except OSError:
        pass

    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        return infos[0][4][0]  # first resolved IP
    except Exception:
        return None


async def check_port(ip: str, port: int, timeout: float, sem: asyncio.Semaphore) -> bool:
    """Attempt to open a TCP connection to (ip, port)."""
    async with sem:
        try:
            conn = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)
            # We only care if connect succeeded.
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return True
        except Exception:
            return False


async def scan_target(
    target: str,
    ports: List[int],
    timeout: float,
    sem: asyncio.Semaphore,
) -> Dict[str, Any]:
    ip = await resolve_host(target)
    result: Dict[str, Any] = {
        "target": target,
        "ip": ip,
        "open_ports": [],
        "error": None,
    }

    if not ip:
        result["error"] = "dns_resolution_failed"
        return result

    tasks = [check_port(ip, p, timeout, sem) for p in ports]
    statuses = await asyncio.gather(*tasks)
    result["open_ports"] = [p for p, ok in zip(ports, statuses) if ok]
    return result


def read_targets(path: str) -> List[str]:
    targets: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            targets.append(line)
    return targets


def write_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_csv(path: str, results: List[Dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target", "ip", "open_ports", "error"])
        for r in results:
            w.writerow(
                [
                    r.get("target"),
                    r.get("ip") or "",
                    ";".join(map(str, r.get("open_ports", []))),
                    r.get("error") or "",
                ]
            )


async def main() -> None:
    ap = argparse.ArgumentParser(description="Async port scanner (CSV/JSON report)")
    ap.add_argument("-i", "--input", required=True, help="File with targets (one per line)")
    ap.add_argument("-o", "--out", default="report", help="Output prefix (default: report)")
    ap.add_argument(
        "--ports",
        default=",".join(map(str, COMMON_PORTS)),
        help="Comma-separated ports (default: common ports)",
    )
    ap.add_argument("--timeout", type=float, default=0.8, help="Timeout per port (seconds)")
    ap.add_argument("--concurrency", type=int, default=400, help="Max simultaneous connections")

    args = ap.parse_args()

    targets = read_targets(args.input)
    ports = sorted({int(p.strip()) for p in args.ports.split(",") if p.strip()})

    sem = asyncio.Semaphore(args.concurrency)

    started_at = datetime.now(timezone.utc).isoformat()
    scan_tasks = [scan_target(t, ports, args.timeout, sem) for t in targets]
    results = await asyncio.gather(*scan_tasks)
    finished_at = datetime.now(timezone.utc).isoformat()

    payload: Dict[str, Any] = {
        "meta": {
            "started_at": started_at,
            "finished_at": finished_at,
            "targets": len(targets),
            "ports": ports,
            "timeout": args.timeout,
            "concurrency": args.concurrency,
        },
        "results": results,
    }

    json_path = f"{args.out}.json"
    csv_path = f"{args.out}.csv"
    write_json(json_path, payload)
    write_csv(csv_path, results)

    # quick summary
    total_open = sum(len(r.get("open_ports", [])) for r in results)
    print(f"Done. Targets={len(targets)} OpenPortsFound={total_open}")
    print(f"JSON: {json_path}")
    print(f"CSV : {csv_path}")


if __name__ == "__main__":
    asyncio.run(main())
