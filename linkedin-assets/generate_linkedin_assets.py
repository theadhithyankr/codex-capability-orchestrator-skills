from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
W, H = 1600, 900


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def mono(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/courbd.ttf" if bold else "C:/Windows/Fonts/cour.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


F = {
    "hero": font(62, True),
    "title": font(46, True),
    "h2": font(32, True),
    "body": font(27),
    "small": font(21),
    "tiny": font(18),
    "mono": mono(23),
    "mono_small": mono(19),
    "mono_bold": mono(23, True),
}


COLORS = {
    "bg": "#f6f3ee",
    "ink": "#171717",
    "muted": "#5d6066",
    "card": "#fffdf8",
    "line": "#d8d0c4",
    "blue": "#2563eb",
    "green": "#0f766e",
    "red": "#b91c1c",
    "yellow": "#eab308",
    "terminal": "#101418",
    "terminal2": "#151b21",
    "white": "#ffffff",
}


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 18), fill=COLORS["ink"])
    draw.rectangle((0, H - 18, W, H), fill=COLORS["ink"])
    return img, draw


def rounded(draw: ImageDraw.ImageDraw, box, radius=22, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw: ImageDraw.ImageDraw, xy, value, fnt, fill=COLORS["ink"], max_width=None, line_gap=8):
    x, y = xy
    if not max_width:
        draw.text((x, y), value, font=fnt, fill=fill)
        return y + draw.textbbox((x, y), value, font=fnt)[3] - y
    avg = max(8, int(fnt.size * 0.52))
    chars = max(16, max_width // avg)
    for line in wrap(value, width=chars):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y


def pill(draw, x, y, label, fill, outline=None, fg=COLORS["white"]):
    pad_x, pad_y = 18, 10
    box = draw.textbbox((0, 0), label, font=F["small"])
    width = box[2] - box[0] + pad_x * 2
    height = box[3] - box[1] + pad_y * 2
    rounded(draw, (x, y, x + width, y + height), radius=18, fill=fill, outline=outline or fill)
    draw.text((x + pad_x, y + pad_y - 2), label, font=F["small"], fill=fg)
    return x + width + 12


def header(draw, eyebrow, title, subtitle=None):
    draw.text((80, 58), eyebrow.upper(), font=F["small"], fill=COLORS["blue"])
    draw.text((80, 92), title, font=F["hero"], fill=COLORS["ink"])
    if subtitle:
        text(draw, (84, 170), subtitle, F["body"], fill=COLORS["muted"], max_width=980)


def footer(draw):
    draw.text((80, 842), "Codex Capability Orchestrator Skills v0.2.0", font=F["small"], fill=COLORS["muted"])
    draw.text((1160, 842), "github.com/theadhithyankr", font=F["small"], fill=COLORS["muted"])


def image_1():
    img, draw = canvas()
    header(
        draw,
        "problem",
        "Codex can code. I wanted it to prepare.",
        "A plain English build request should become source-backed project context before files are touched.",
    )

    rounded(draw, (90, 285, 710, 650), fill=COLORS["card"], outline=COLORS["line"], width=2)
    draw.text((130, 325), "User prompt", font=F["h2"], fill=COLORS["ink"])
    prompt = "create a website using Shopify Liquid theme"
    rounded(draw, (130, 390, 670, 485), radius=16, fill="#eef6ff", outline="#bfd7ff", width=2)
    text(draw, (158, 416), prompt, F["body"], fill=COLORS["ink"], max_width=470)
    draw.text((130, 545), "No CLI ritual. No manual docs hunt.", font=F["body"], fill=COLORS["muted"])

    draw.line((760, 462, 840, 462), fill=COLORS["ink"], width=5)
    draw.polygon([(840, 462), (815, 445), (815, 479)], fill=COLORS["ink"])

    rounded(draw, (890, 260, 1510, 710), fill=COLORS["terminal"], outline="#2f3740", width=2)
    draw.text((930, 300), ".codex/context/", font=F["mono_bold"], fill="#d7e1ea")
    files = [
        "manifest.json",
        "docs/shopify.json",
        "docs/liquid.json",
        "detected: shopify, liquid",
        "warnings: []",
    ]
    y = 360
    for index, line in enumerate(files):
        color = "#b9f6ca" if index >= 3 else "#dbeafe"
        draw.text((950, y), line, font=F["mono"], fill=color)
        y += 58

    x = 930
    for label, color in [("prompt mined", COLORS["blue"]), ("docs provenance", COLORS["green"]), ("local manifest", COLORS["ink"])]:
        x = pill(draw, x, 645, label, color)
    footer(draw)
    img.save(OUT / "01_plain_prompt_to_context.png", quality=95)


def image_2():
    img, draw = canvas()
    header(
        draw,
        "workflow",
        "What the prep step records",
        "The output is boring on purpose: capabilities, docs sources, skill matches, and warnings.",
    )
    rounded(draw, (100, 255, 1500, 795), fill=COLORS["terminal"], outline="#2f3740", width=2)
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        draw.ellipse((132 + i * 34, 285, 152 + i * 34, 305), fill=c)
    lines = [
        "Request: create a website using Shopify Liquid theme",
        "",
        "Capabilities",
        "  - shopify   confidence=0.95   source=request",
        "  - liquid    confidence=0.95   source=request",
        "",
        "Docs",
        "  - shopify -> shopify.dev/docs/storefronts/themes",
        "  - liquid  -> shopify.dev/docs/api/liquid",
        "",
        "Manifest",
        "  - .codex/context/manifest.json",
        "  - warnings: []",
    ]
    y = 335
    for line in lines:
        if line in {"Capabilities", "Docs", "Manifest"}:
            draw.text((140, y), line, font=F["mono_bold"], fill="#ffffff")
        elif "warnings: []" in line:
            draw.text((140, y), line, font=F["mono"], fill="#b9f6ca")
        elif "->" in line:
            draw.text((140, y), line, font=F["mono"], fill="#bfdbfe")
        else:
            draw.text((140, y), line, font=F["mono"], fill="#d7e1ea")
        y += 32
    footer(draw)
    img.save(OUT / "02_internal_prep_output.png", quality=95)


def image_3():
    img, draw = canvas()
    header(
        draw,
        "architecture",
        "Source-backed context, not agent vibes",
        "The manifest is local, inspectable, repeatable, and honest about missing evidence.",
    )
    rounded(draw, (90, 245, 1510, 775), fill=COLORS["card"], outline=COLORS["line"], width=2)
    code = [
        "{",
        '  "request": "create a website using Shopify Liquid theme",',
        '  "detected_capabilities": [',
        '    {"id": "shopify", "sources": ["request"]},',
        '    {"id": "liquid", "sources": ["request"]}',
        "  ],",
        '  "docs": {',
        '    "written": [',
        '      "docs/shopify.json",',
        '      "docs/liquid.json"',
        "    ]",
        "  },",
        '  "warnings": []',
        "}",
    ]
    y = 285
    for line in code:
        color = COLORS["ink"]
        if "shopify" in line or "liquid" in line:
            color = COLORS["green"]
        if "warnings" in line:
            color = COLORS["blue"]
        draw.text((135, y), line, font=F["mono"], fill=color)
        y += 32

    rounded(draw, (980, 320, 1445, 650), radius=18, fill="#f1f5f9", outline="#d6dee8", width=2)
    draw.text((1025, 360), "Design principle", font=F["h2"], fill=COLORS["ink"])
    bullets = [
        "Know what was detected",
        "Know where docs came from",
        "Warn when context is missing",
        "Install nothing without consent",
    ]
    y = 425
    for bullet in bullets:
        draw.ellipse((1030, y + 8, 1044, y + 22), fill=COLORS["blue"])
        draw.text((1062, y), bullet, font=F["body"], fill=COLORS["ink"])
        y += 48
    footer(draw)
    img.save(OUT / "03_manifest_provenance.png", quality=95)


def image_4():
    img, draw = canvas()
    header(
        draw,
        "release",
        "v0.2.0: Prompt-driven project prep",
        "Built for the moment before implementation: load the right stack context first.",
    )
    cards = [
        ("Natural prompts", "Use normal English. Codex turns it into project context."),
        ("Tech registry", "Known stacks get trusted docs provenance immediately."),
        ("Unknown stacks", "Optional web discovery records reachable docs candidates."),
        ("Safe installs", "GitHub search and skill installs stay explicit."),
    ]
    positions = [(100, 300), (830, 300), (100, 555), (830, 555)]
    for (title, body), (x, y) in zip(cards, positions):
        rounded(draw, (x, y, x + 635, y + 185), fill=COLORS["card"], outline=COLORS["line"], width=2)
        draw.text((x + 38, y + 35), title, font=F["h2"], fill=COLORS["ink"])
        text(draw, (x + 40, y + 88), body, F["body"], fill=COLORS["muted"], max_width=530)
    rounded(draw, (1180, 92, 1485, 155), radius=22, fill=COLORS["ink"])
    draw.text((1230, 107), "released", font=F["body"], fill=COLORS["white"])
    footer(draw)
    img.save(OUT / "04_release_highlights.png", quality=95)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    image_1()
    image_2()
    image_3()
    image_4()


if __name__ == "__main__":
    main()
