"""Day 5: bounded parallel execution of independent harness jobs.

Concept: deterministic orchestration belongs outside model judgment.
Design rules: isolate each job by work directory, capture failures as results,
and return results in the caller's input order.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed


def run_fleet(jobs: list[dict], make_harness, max_workers: int = 4) -> list[dict]:
    """Run independent jobs concurrently and return ordered success reports."""
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_run_one, job, make_harness): job for job in jobs}
        results = [future.result() for future in as_completed(futures)]
    order = {job["name"]: index for index, job in enumerate(jobs)}
    return sorted(results, key=lambda result: order[result["name"]])


def _run_one(job: dict, make_harness) -> dict:
    """Run one job while converting unexpected failures to a result record."""
    try:
        return {"name": job["name"], "ok": True,
                "report": make_harness(job["workdir"]).run(job["task"])}
    except Exception as error:
        return {"name": job["name"], "ok": False,
                "report": f"{type(error).__name__}: {error}"}
