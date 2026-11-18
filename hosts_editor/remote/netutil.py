"""Pure helpers (no Windows imports) used by the Internet block and the remote agent."""

import ipaddress


def _parse_part(part: str):
    part = part.strip()
    if not part:
        return None
    if "/" in part:
        net = ipaddress.ip_network(part, strict=False)
        return net.version, int(net.network_address), int(net.broadcast_address)
    if "-" in part:
        lo, hi = part.split("-", 1)
        a, b = ipaddress.ip_address(lo.strip()), ipaddress.ip_address(hi.strip())
        if a.version != b.version:
            raise ValueError(f"mixed IP versions in range {part!r}")
        return a.version, int(a), int(b)
    a = ipaddress.ip_address(part)
    return a.version, int(a), int(a)


def _fmt(version: int, lo: int, hi: int) -> str:
    cls = ipaddress.IPv4Address if version == 4 else ipaddress.IPv6Address
    return str(cls(lo)) if lo == hi else f"{cls(lo)}-{cls(hi)}"


def carve_ranges(spec: str, exclude) -> str:
    """Return ``spec`` (comma-separated ranges/CIDRs, netsh remoteip syntax) minus the given IPs.

    Used so that blocking the Internet never cuts the remote agent off from its server.
    Invalid exclusions are ignored; the output keeps netsh's comma-separated range format.
    """
    excl = {}
    for raw in exclude or ():
        try:
            ip = ipaddress.ip_address(str(raw).strip())
        except ValueError:
            continue
        excl.setdefault(ip.version, set()).add(int(ip))
    if not excl:
        return spec

    out = []
    for part in spec.split(","):
        parsed = _parse_part(part)
        if parsed is None:
            continue
        version, lo, hi = parsed
        cuts = sorted(x for x in excl.get(version, ()) if lo <= x <= hi)
        start = lo
        for x in cuts:
            if x > start:
                out.append(_fmt(version, start, x - 1))
            start = x + 1
        if start <= hi:
            out.append(_fmt(version, start, hi))
    return ",".join(out)
