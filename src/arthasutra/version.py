__all__ = ["__version__", "bump_version"]

# Semantic-ish 4-part version: aa.bb.cc.dd
# We keep pyproject.toml in sync manually when bumping.
__version__ = "0.1.0.2"


def bump_version(ver: str) -> str:
    parts = ver.split(".")
    parts = [int(p) for p in parts] + [0] * (4 - len(parts))
    a, b, c, d = parts[:4]
    d += 1
    if d > 99:
        d = 0
        c += 1
        if c > 99:
            c = 0
            b += 1
            if b > 99:
                b = 0
                a += 1
    return f"{a}.{b}.{c}.{d}"
