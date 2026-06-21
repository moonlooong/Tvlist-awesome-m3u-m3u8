#!/usr/bin/env python3
"""
Convert M3U IPTV playlist to DIYP .txt format.

DIYP format:
    分类,#genre#
    频道名,URL

M3U format:
    #EXTM3U
    #EXTINF:-1,tvg-id="..." group-title="央视",CCTV-1
    http://example.com/stream

Usage:
    python3 scripts/m3u_to_diyp.py <input.m3u> [output.txt]

If output is omitted, prints to stdout.
"""

import re
import sys
from collections import OrderedDict


def parse_m3u(filepath: str) -> OrderedDict:
    """Parse M3U file, return {category: [(name, url), ...]} in file order."""
    groups = OrderedDict()

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF:"):
            # Extract group-title
            gt_match = re.search(r'group-title="([^"]*)"', line)
            category = gt_match.group(1) if gt_match else "未分类"

            # Extract channel name: text after the last comma
            # e.g. "#EXTINF:-1,...,湖南卫视" → "湖南卫视"
            name = line.rsplit(",", 1)[-1].strip()

            # Find URL on next non-empty line
            url = ""
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith("#"):
                    url = next_line
                    i = j  # advance past URL
                    break
                j += 1

            if url and name:
                if category not in groups:
                    groups[category] = []
                groups[category].append((name, url))

        i += 1

    return groups


def to_diyp(groups: OrderedDict) -> str:
    """Convert parsed groups to DIYP .txt format."""
    lines = []
    for category, channels in groups.items():
        lines.append(f"{category},#genre#")
        for name, url in channels:
            lines.append(f"{name},{url}")
        lines.append("")  # blank line between categories
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.m3u> [output.txt]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    groups = parse_m3u(input_path)
    result = to_diyp(groups)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Converted: {input_path} → {output_path}")
        print(f"  Categories: {len(groups)}, Channels: {sum(len(v) for v in groups.values())}")
    else:
        print(result)


if __name__ == "__main__":
    main()
