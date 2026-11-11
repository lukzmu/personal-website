import hashlib
from urllib.parse import quote

GRID = 5
CELL = 10
BACKGROUND = "#e5e5e5"


def identicon_data_uri(seed: str) -> str:
    """Deterministic, mirrored 5x5 avatar: the same seed always yields the same picture."""
    digest = hashlib.sha256(seed.encode()).digest()
    hue = digest[0] * 360 // 256
    colour = f"hsl({hue} 55% 45%)"

    half = (GRID + 1) // 2
    rects = []
    for row in range(GRID):
        for column in range(half):
            if digest[1 + row * half + column] % 2:
                continue
            for x in {column, GRID - 1 - column}:
                rects.append(f'<rect x="{x * CELL}" y="{row * CELL}" width="{CELL}" height="{CELL}"/>')

    size = GRID * CELL
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges">'
        f'<rect width="{size}" height="{size}" fill="{BACKGROUND}"/>'
        f'<g fill="{colour}">{"".join(rects)}</g></svg>'
    )
    return f"data:image/svg+xml,{quote(svg)}"
