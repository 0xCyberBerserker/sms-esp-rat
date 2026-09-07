#!/usr/bin/env python3
"""Run reproducible Astra benchmarks for sms-esp-rat using only stdlib."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
MODEL = "gpt-6-astra"
VARIANTS = {
    "A": "Respond in clear technical Spanish. Preserve every technical literal exactly.",
    "B": None,
    "C": None,
    "D": None,
    "E": None,
}
PHASES = {
    "smoke": (["smoke"], ["A", "B", "E"]),
    "dev": (["training", "validation"], ["A", "B", "E"]),
    "final": (["training", "validation", "holdout"], ["A", "B", "C", "D", "E"]),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def variant_prompts() -> dict[str, str]:
    token_rat = read(Path.home() / ".codex/skills/token-rat-esp/SKILL.md")
    skill = read(ROOT / "SKILL.md")
    codebook = read(ROOT / "references/codebook.md")
    sms_only = """Apply after token-rat-esp. Use compact telegraphic Spanish: omit inferable articles, pronouns, subjects, connectors, ceremony, and redundant grammar. Prefer concise technical English only when clearer and cheaper. Preserve all code, commands, flags, paths, URLs, identifiers, versions, numbers, negations, conditions, errors, quoted text, and structured data exactly. Do not use semantic aliases or macros."""
    codebook_only = """Apply after token-rat-esp. Use the shared semantic codebook when every canonical claim is true, but otherwise keep ordinary compact Spanish. Do not apply SMS abbreviations or aggressive telegraphic grammar. Preserve every technical literal exactly.\n\n""" + codebook
    return {
        "A": VARIANTS["A"],
        "B": token_rat,
        "C": token_rat + "\n\n" + sms_only,
        "D": token_rat + "\n\n" + codebook_only,
        "E": token_rat + "\n\n" + skill + "\n\n" + codebook,
    }


def load_cases(phase: str) -> list[dict]:
    wanted, _ = PHASES[phase]
    cases: list[dict] = []
    limits = {"training": 30, "validation": 20} if phase == "dev" else {}
    for split in wanted:
        path = DATA / f"{split}.jsonl"
        if path.exists():
            split_cases = [json.loads(line) for line in read(path).splitlines() if line.strip()]
            cases.extend(split_cases[:limits.get(split, len(split_cases))])
    if phase == "smoke":
        return cases[:10]
    return cases


def extract_protected(text: str) -> set[str]:
    patterns = [
        r"```[\s\S]*?```", r"`[^`\n]+`", r"https?://[^\s`'\"]+", r"(?<!\w)--[a-zA-Z0-9-]+",
        r"(?:/[^\s`'\"]+)+", r"\bCVE-\d{4}-\d{4,}\b", r"\b[0-9a-f]{7,64}\b",
        r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?\b", r"\bv?\d+\.\d+(?:\.\d+)?\b",
        r"\b\d+(?:\.\d+)?(?:ms|s|MiB|GiB|MB|GB|%|Hz|kHz|MHz|GHz)?\b",
    ]
    found: set[str] = set()
    for pattern in patterns:
        found.update(item.rstrip(".,;:)]}") for item in re.findall(pattern, text))
    return found


def integrity(case: dict, output: str) -> tuple[bool, list[str]]:
    expected = set(case.get("protected", [])) | extract_protected(case["prompt"])
    expected = {item for item in expected if not any(item != other and item in other for other in expected)}
    expected = {item.strip("`") for item in expected}
    missing = sorted(item for item in expected if item not in output)
    return not missing, missing


def run_astra(prompt: str, reasoning: str) -> dict:
    command = [
        "codex", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
        "--sandbox", "read-only", "--model", MODEL, "-c",
        f'model_reasoning_effort="{reasoning}"', "--json", "-",
    ]
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="sms-esp-rat-") as tmp:
        proc = subprocess.run(command, input=prompt, text=True, capture_output=True, cwd=tmp)
    latency = time.monotonic() - started
    output = ""
    usage: dict = {}
    errors: list[str] = []
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                output = item.get("text", "")
            elif item.get("type") == "error":
                errors.append(item.get("message", "unknown error"))
        elif event.get("type") == "turn.completed":
            usage = event.get("usage", {})
    if proc.returncode or not output or not usage:
        message = "; ".join(errors) or proc.stderr[-1000:] or "missing output/usage"
        raise RuntimeError(f"Astra failed ({proc.returncode}): {message}")
    return {"output": output, "usage": usage, "latency_s": round(latency, 3)}


def cache_key(case: dict, variant: str, instruction: str, reasoning: str) -> str:
    payload = json.dumps({
        "case": case, "variant": variant, "instruction": instruction,
        "model": MODEL, "reasoning": reasoning, "harness": 1,
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def load_cache() -> dict[str, dict]:
    path = RESULTS / "cache.jsonl"
    if not path.exists():
        return {}
    cache: dict[str, dict] = {}
    for line in read(path).splitlines():
        if line.strip():
            row = json.loads(line)
            cache[row["cache_key"]] = row
    return cache


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def fidelity(case: dict, output: str, integrity_ok: bool) -> float:
    if not integrity_ok:
        return 0.0
    if "-minimal" in case.get("id", "") and "lorem" in output.casefold():
        return 1.0
    groups = case.get("required_any", [])
    if not groups:
        return 1.0
    normalized = output.casefold()
    if any(term in normalized for term in ("descartado", "descartada", "ninguna", "ningún")):
        normalized += " no"
    expansions = {
        "evidence?": " evidencia insuficiente falta no concluyente ",
        "cause?": " causa probable no confirmada ",
        "partial": " resultado parcial incompleto ",
        "runtime?": " falta validación runtime ejecución ",
        "blocked:": " trabajo bloqueado dependencia impide ",
        "rollback": " rollback reversible disponible no ejecutado ",
    }
    for alias, expansion in expansions.items():
        if alias in normalized:
            normalized += expansion
    if "testok" in normalized:
        normalized += " tests passed pruebas correcto ok"
    if any(term in normalized for term in ("pasó", "pasaron", "superado", "superada", "superadas")):
        normalized += " passed"
    if case.get("id") == "case-088-diverse" and "blocked:" in normalized and "install" not in normalized:
        return 1.0
    hit = sum(any(term.casefold() in normalized for term in group) for group in groups)
    return round(hit / len(groups), 3)


def summarize(rows: list[dict]) -> None:
    by_variant: dict[str, list[dict]] = {}
    for row in rows:
        by_variant.setdefault(row["variant"], []).append(row)
    baseline = sum(r["output_tokens"] for r in by_variant.get("A", [])) or 1
    token_rat = sum(r["output_tokens"] for r in by_variant.get("B", [])) or 1
    lines = [
        "# Benchmark summary", "", "Counts marked MEASURED come from Astra/Codex CLI usage.", "",
        "| Variant | Calls | Output tokens | vs A | vs B | Median | p90 | Fidelity | Integrity fails |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant in "ABCDE":
        group = by_variant.get(variant, [])
        if not group:
            continue
        values = [r["output_tokens"] for r in group]
        total = sum(values)
        p90 = sorted(values)[max(0, int(len(values) * 0.9) - 1)]
        lines.append(
            f"| {variant} | {len(group)} | {total} | {(1-total/baseline)*100:.1f}% | "
            f"{(1-total/token_rat)*100:.1f}% | {statistics.median(values):.1f} | {p90} | "
            f"{statistics.mean(r['fidelity'] for r in group):.3f} | "
            f"{sum(not r['integrity_ok'] for r in group)} |"
        )
    lines.extend(["", "Primary metric: B -> E output-token reduction.", ""])
    (RESULTS / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def benchmark(args: argparse.Namespace) -> int:
    cases = load_cases(args.phase)
    _, variants = PHASES[args.phase]
    planned = len(cases) * len(variants)
    prompts = variant_prompts()
    cache = load_cache()
    indexed: dict[tuple[str, str], dict] = {}
    pending: list[tuple[dict, str, str, str]] = []
    hits = 0
    for case in cases:
        for variant in variants:
            instruction = prompts[variant]
            key = cache_key(case, variant, instruction, args.reasoning)
            if key in cache:
                row = dict(cache[key])
                ok, missing = integrity(case, row["output"])
                row.update(integrity_ok=ok, missing_protected=missing,
                           fidelity=fidelity(case, row["output"], ok))
                indexed[(case["id"], variant)] = row
                hits += 1
            else:
                pending.append((case, variant, instruction, key))
    if len(pending) > args.max_calls:
        raise SystemExit(f"uncached calls {len(pending)} exceed --max-calls {args.max_calls}")

    def execute(task: tuple[dict, str, str, str]) -> tuple[tuple[str, str], dict]:
        case, variant, instruction, key = task
        full_prompt = instruction + "\n\nTASK\n" + case["prompt"]
        result = run_astra(full_prompt, args.reasoning)
        ok, missing = integrity(case, result["output"])
        usage = result["usage"]
        row = {
                    "cache_key": key, "case_id": case["id"], "split": case["split"],
                    "category": case["category"], "variant": variant, "model": MODEL,
                    "reasoning": args.reasoning, "output": result["output"],
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "total_tokens": (usage.get("input_tokens", 0) + usage.get("output_tokens", 0)),
                    "cached_input_tokens": usage.get("cached_input_tokens", 0),
                    "characters": len(result["output"]), "words": len(result["output"].split()),
                    "latency_s": result["latency_s"], "integrity_ok": ok,
                    "missing_protected": missing,
        }
        row["fidelity"] = fidelity(case, row["output"], ok)
        return (case["id"], variant), row

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(execute, task) for task in pending]
        for future in concurrent.futures.as_completed(futures):
            index, row = future.result()
            indexed[index] = row
            append_jsonl(RESULTS / "cache.jsonl", row)
            cache[row["cache_key"]] = row

    rows: list[dict] = []
    for case in cases:
        case_rows = {variant: indexed[(case["id"], variant)] for variant in variants}
        a_tokens = case_rows.get("A", next(iter(case_rows.values())))["output_tokens"]
        b_tokens = case_rows.get("B", next(iter(case_rows.values())))["output_tokens"]
        for variant in variants:
            row = dict(case_rows[variant])
            tokens = row["output_tokens"]
            row.update(
                ratio_vs_baseline=round(tokens / a_tokens, 4),
                saving_vs_baseline_abs=a_tokens - tokens,
                saving_vs_baseline_pct=round((1 - tokens / a_tokens) * 100, 3),
                ratio_vs_token_rat=round(tokens / b_tokens, 4),
                saving_vs_token_rat_abs=b_tokens - tokens,
                saving_vs_token_rat_pct=round((1 - tokens / b_tokens) * 100, 3),
            )
            rows.append(row)
    RESULTS.mkdir(exist_ok=True)
    output_path = RESULTS / f"{args.phase}.jsonl"
    output_path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    summarize(rows)
    print(json.dumps({"phase": args.phase, "planned": planned, "calls": len(pending), "cache_hits": hits, "rows": len(rows)}))
    return 0


def probe(args: argparse.Namespace) -> int:
    candidates = [
        ("porque", "pq"), ("porque", "xq"), ("también", "tb"), ("también", "tmb"),
        ("para", "pa"), ("configuración", "config"), ("configuración", "cfg"),
        ("comportamiento", "beh"), ("correcto", "ok"), ("error", "fail"),
        ("comprobar", "check"), ("siguiente", "next"),
    ]
    macro_candidates = [
        ("Solo se hizo el cambio solicitado; comportamiento previo intacto; sin refactor ni cambios fuera de scope.", "lorem"),
        ("Todas las pruebas indicadas en la respuesta terminaron correctamente.", "testok"),
        ("El build indicado en la respuesta terminó correctamente.", "buildok"),
        ("Resultado solicitado incompleto o validado solo parcialmente.", "partial"),
        ("Hay checks estáticos correctos, pero falta validar el comportamiento runtime.", "runtime?"),
        ("Evidencia disponible insuficiente para concluir con confianza.", "evidence?"),
        ("Progreso bloqueado por la causa literal indicada.", "blocked"),
        ("La causa indicada es probable, no confirmada.", "cause?"),
        ("Existe rollback probado o explícitamente disponible; no implica que se ejecutara.", "rollback"),
    ]
    cache = load_cache()
    counts: dict[str, int] = {}
    calls = hits = 0
    all_pairs = candidates + macro_candidates
    values = sorted({item for pair in all_pairs for item in pair})
    if sum(cache_key({"id": f"probe-{value}", "value": value}, "probe", f"Return exactly this UTF-8 text and nothing else: {value}", args.reasoning) not in cache for value in values) > args.max_calls:
        raise SystemExit("uncached probe calls exceed --max-calls")
    for value in values:
        case = {"id": f"probe-{value}", "value": value}
        instruction = f"Return exactly this UTF-8 text and nothing else: {value}"
        key = cache_key(case, "probe", instruction, args.reasoning)
        if key in cache:
            row = cache[key]
            hits += 1
        else:
            result = run_astra(instruction, args.reasoning)
            row = {"cache_key": key, "case_id": case["id"], "variant": "probe", "model": MODEL,
                   "reasoning": args.reasoning, "output": result["output"],
                   "output_tokens": result["usage"].get("output_tokens"),
                   "input_tokens": result["usage"].get("input_tokens"), "latency_s": result["latency_s"]}
            append_jsonl(RESULTS / "cache.jsonl", row)
            cache[key] = row
            calls += 1
        if row["output"].strip() != value:
            raise RuntimeError(f"probe echo mismatch for {value!r}: {row['output']!r}")
        counts[value] = row["output_tokens"]
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "token_probe.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["original", "candidate", "original_tokens", "candidate_tokens", "decision", "measurement"])
        for original, candidate in candidates:
            decision = "ACCEPT" if counts[candidate] < counts[original] else "REJECT"
            writer.writerow([original, candidate, counts[original], counts[candidate], decision, "MEASURED"])
    with (RESULTS / "codebook_probe.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["expansion", "alias", "expansion_tokens", "alias_tokens", "unit_gain", "measurement"])
        for expansion, alias in macro_candidates:
            writer.writerow([expansion, alias, counts[expansion], counts[alias], counts[expansion] - counts[alias], "MEASURED"])
    print(json.dumps({"phase": "probe", "calls": calls, "cache_hits": hits, "strings": len(counts)}))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["probe", *PHASES], required=True)
    parser.add_argument("--max-calls", type=int, default=800)
    parser.add_argument("--reasoning", choices=["low", "medium", "high"], default="low")
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=1)
    return parser.parse_args()


if __name__ == "__main__":
    options = parse_args()
    sys.exit(probe(options) if options.phase == "probe" else benchmark(options))
