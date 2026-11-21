"""
Stage 1 batch run: ask ChatGPT, Claude and/or Gemini (through their APIs) to write tests
for every function in stage1/dataset.json, save them, and run them with pytest.

Safe to stop (Ctrl+C) and start again: functions that already have tests for a
tool are skipped, so it continues where it left off.

Usage (from the backend folder, with your keys in backend/.env):

    python3 stage1_generate_all.py --tool claude
    python3 stage1_generate_all.py --tool chatgpt
    python3 stage1_generate_all.py --tool gemini
    python3 stage1_generate_all.py --tool all --workers 4
    python3 stage1_generate_all.py --tool claude --limit 5        # try 5 first
    python3 stage1_generate_all.py --tool claude --redo-broken    # retry files that could not run
"""

import argparse
import concurrent.futures
import json
import sys
import threading
import time
import traceback

import main  # noqa: F401  (loads the backend first; stage1 builds on it)
import stage1

LOG_FILE = stage1.STAGE1_DIR / "generation_log.jsonl"
_lock = threading.Lock()


def log(entry):
    with _lock:
        with LOG_FILE.open("a") as f:
            f.write(json.dumps(entry) + "\n")


def needs_work(tool, item, redo_broken):
    saved = stage1.read_saved(tool, item)
    if saved is None:
        return True
    if redo_broken and not (saved.get("run") or {}).get("could_run"):
        return True
    return False


def process(tool, item):
    start = time.time()
    try:
        answer, model, usage = stage1.generate_with_api(tool, stage1.build_prompt(item))
        stage1.save_test(tool, item, answer, source="api", model=model, usage=usage)
        run = stage1.run_tests(tool, item)
        entry = {"tool": tool, "id": item["id"], "ok": True, "model": model, "usage": usage,
                 "tests": run["total"], "passed": run["passed"], "could_run": run["could_run"],
                 "seconds": round(time.time() - start, 1), "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:  # keep going with the other functions
        detail = getattr(e, "detail", None) or f"{type(e).__name__}: {e}"
        entry = {"tool": tool, "id": item["id"], "ok": False, "error": str(detail)[:500],
                 "seconds": round(time.time() - start, 1), "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        if not getattr(e, "detail", None):
            entry["trace"] = traceback.format_exc()[-1500:]
    log(entry)
    return entry


def main_cli():
    ap = argparse.ArgumentParser(description="Generate Stage 1 tests through the AI APIs")
    ap.add_argument("--tool", choices=["chatgpt", "claude", "gemini", "all"], required=True,
                    help="one tool, or 'all' for every tool that has an API key")
    ap.add_argument("--workers", type=int, default=3, help="requests at the same time (default 3)")
    ap.add_argument("--limit", type=int, default=None, help="only do this many functions (to try it out)")
    ap.add_argument("--redo-broken", action="store_true", help="redo tests that could not run")
    args = ap.parse_args()

    info = stage1.tools_info()
    if args.tool == "all":
        tools = [t for t in stage1.TOOLS if info[t]["auto"]]
        missing = [info[t]["name"] for t in stage1.TOOLS if not info[t]["auto"]]
        if missing:
            print("Skipping (no API key in backend/.env): " + ", ".join(missing))
        if not tools:
            sys.exit("No API keys found. Add them to backend/.env (see backend/.env.example).")
    else:
        tools = [args.tool]
    for t in tools:
        if not info[t]["auto"]:
            sys.exit(f"{info[t]['name']}: no API key. Add {info[t]['key_env']}=... to backend/.env")

    items = stage1.load_dataset()["functions"]
    jobs = [(t, it) for it in items for t in tools if needs_work(t, it, args.redo_broken)]
    if args.limit:
        jobs = jobs[:args.limit]
    done_before = {t: sum(1 for it in items if stage1.read_saved(t, it)) for t in tools}
    print(f"Dataset: {len(items)} functions. Already done: "
          + ", ".join(f"{info[t]['name']} {done_before[t]}" for t in tools))
    print(f"To do now: {len(jobs)}  (models: " + ", ".join(f"{info[t]['name']}={info[t]['model']}" for t in tools)
          + f")  workers={args.workers}\nLog: {LOG_FILE}\n")
    if not jobs:
        print("Nothing to do — everything is already generated.")
        return

    ok = fail = 0
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(args.workers) as ex:
        futures = {ex.submit(process, t, it): (t, it) for t, it in jobs}
        for n, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            e = fut.result()
            if e["ok"]:
                ok += 1
                status = (f"{e['tests']} tests, {e['passed']} passed" if e["could_run"]
                          else "saved, but the test file could not run")
            else:
                fail += 1
                status = "ERROR: " + e["error"][:120]
            elapsed = time.time() - start
            eta = elapsed / n * (len(jobs) - n)
            print(f"[{n}/{len(jobs)}] {info[e['tool']]['name']:8} {e['id'][:70]:70} {status}"
                  f"   (~{eta / 60:.0f} min left)", flush=True)

    print(f"\nFinished: {ok} generated, {fail} failed, in {(time.time() - start) / 60:.1f} min.")
    if fail:
        print("Run the same command again to retry the failed ones.")


if __name__ == "__main__":
    main_cli()
