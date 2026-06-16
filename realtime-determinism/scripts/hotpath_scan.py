"""Heuristic hot-path hazard scanner: flags real-time-unsafe operations inside a control-loop
function — I/O (print/open/input/socket), blocking (sleep), logging, lock acquisition, and
allocation (comprehensions, list/dict/set/bytearray). Python AST; stdlib only.

Heuristic, not a proof: a clean scan is NECESSARY, not SUFFICIENT, for RT-safety (it can't see
into called functions, C extensions, or implicit allocations). Use it to catch the obvious.
"""
from __future__ import annotations
import ast
import sys
from dataclasses import dataclass

ERROR, WARN = "error", "warn"
_LOG = {"info", "debug", "warning", "warn", "error", "critical", "exception", "log"}
_SOCK = {"recv", "send", "sendall", "connect", "recvfrom"}
_ALLOC_CALLS = {"list", "dict", "set", "bytearray", "bytes"}
_IO_NAMES = {"print", "input", "open"}


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    line: int


def scan_source(src: str, func=None) -> list:
    tree = ast.parse(src)
    targets = [n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and (func is None or n.name == func)]
    out = []
    seen = set()

    def add(sev, code, msg, line):
        key = (code, line)
        if key not in seen:
            seen.add(key)
            out.append(Finding(sev, code, msg, line))

    for fn in targets:
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Name):
                    if f.id in _IO_NAMES:
                        add(ERROR, "io_call", f"'{f.id}()' is blocking I/O in the hot path", node.lineno)
                    elif f.id in _ALLOC_CALLS:
                        add(WARN, "alloc", f"'{f.id}()' allocates in the hot path", node.lineno)
                elif isinstance(f, ast.Attribute):
                    a = f.attr
                    if a == "sleep":
                        add(ERROR, "blocking_call", "'sleep' blocks the hot path", node.lineno)
                    elif a in _LOG:
                        add(ERROR, "logging_call",
                            f"logging ('{a}') in the hot path is non-deterministic I/O", node.lineno)
                    elif a == "acquire":
                        add(ERROR, "lock_acquire",
                            "lock acquire in the hot path can block unboundedly (needs priority inheritance)", node.lineno)
                    elif a in _SOCK:
                        add(ERROR, "io_call", f"socket '{a}' is blocking I/O in the hot path", node.lineno)
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                add(WARN, "alloc", "comprehension allocates in the hot path", node.lineno)
            elif isinstance(node, ast.With):
                for item in node.items:
                    ctx = item.context_expr
                    name = None
                    if isinstance(ctx, ast.Name):
                        name = ctx.id
                    elif isinstance(ctx, ast.Attribute):
                        name = ctx.attr
                    elif isinstance(ctx, ast.Call):
                        cf = ctx.func
                        name = cf.id if isinstance(cf, ast.Name) else (cf.attr if isinstance(cf, ast.Attribute) else None)
                    if name and "lock" in name.lower():
                        add(ERROR, "lock_with", "with-block acquires a lock in the hot path", node.lineno)
    return out


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: hotpath_scan.py <file.py> [function_name]", file=sys.stderr)
        return 2
    with open(argv[1]) as fh:
        src = fh.read()
    func = argv[2] if len(argv) == 3 else None
    findings = scan_source(src, func)
    for x in findings:
        print(f"[{x.severity.upper()}] {x.code} (line {x.line}): {x.message}")
    return 1 if any(x.severity == ERROR for x in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
