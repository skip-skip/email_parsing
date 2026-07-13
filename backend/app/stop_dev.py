"""Stop all dev servers (backend on port 8000, frontend on port 5173).

Kills processes listening on the target ports AND orphaned uvicorn
multiprocessing children (spawn_main) that survive parent termination.

Usage:
    python -m backend.app.stop_dev
"""
from __future__ import annotations

import subprocess


def _pids_on_ports(*ports: int) -> set[str]:
    out = subprocess.check_output(["netstat", "-ano"], text=True)
    pids: set[str] = set()
    for line in out.splitlines():
        if "LISTENING" not in line:
            continue
        for port in ports:
            if f":{port}" in line:
                pids.add(line.split()[-1])
    return pids


def _pids_by_command(*patterns: str) -> set[str]:
    ps_filter = " -or ".join(
        f"($_.CommandLine -like '*{p}*')" for p in patterns
    )
    ps_cmd = (
        "Get-CimInstance Win32_Process "
        f"| Where-Object {{{ps_filter}}} "
        "| Select-Object -ExpandProperty ProcessId"
    )
    try:
        out = subprocess.check_output(
            ["pwsh", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    return {line.strip() for line in out.splitlines() if line.strip().isdigit()}


def _kill_pids(pids: set[str]) -> int:
    killed = 0
    for pid in pids:
        r = subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        if r.returncode == 0:
            killed += 1
    return killed


def main() -> None:
    pids = _pids_on_ports(8000, 5173)
    pids |= _pids_by_command("uvicorn", "spawn_main", "npm run dev")
    killed = _kill_pids(pids)
    print(f"Stopped {killed} process(es)." if pids else "No dev servers running.")


if __name__ == "__main__":
    main()
