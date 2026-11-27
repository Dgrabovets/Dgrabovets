"""Переводит символы шрифтов бренда в контуры и пишет profilegen/glyphs.json

Запускается вручную после смены шрифтов, нужен `fontTools`. Сборке профиля он не нужен
"""

import json
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

from profilegen import settings
from profilegen.font_enum import FontEnum
from profilegen.glyph_text import GLYPHS_PATH

# Файл шрифта и насыщенность для каждого начертания
SOURCES = {FontEnum.MONO_MEDIUM: ("JetBrainsMono[wght].ttf", 500),
           FontEnum.MONO_BOLD: ("JetBrainsMono[wght].ttf", 700),
           FontEnum.SANS_MEDIUM: ("IBMPlexSans[wdth,wght].ttf", 500)}

# Печатные ASCII и Latin-1, многоточие и типографский апостроф: этого хватает английским текстам профиля
CHARACTERS = "".join(map(chr, [*range(32, 127), *range(160, 256)])) + "…’"

# Номер записи об авторских правах в таблице имён шрифта
COPYRIGHT_NAME_ID = 0


def extract(file_name: str, weight: int) -> tuple[str, dict]:
    """Снимает контуры символов одного начертания

    Args:
        file_name: Файл вариативного шрифта в папке шрифтов
        weight: Насыщенность

    Returns:
        Строка об авторских правах и данные начертания
    """
    font = TTFont(settings.fonts_dir() / file_name)
    axes = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}
    static = instantiateVariableFont(font, axes | {"wght": weight})
    glyph_names = static.getBestCmap()
    glyphs = static.getGlyphSet()
    table = {}

    for symbol in CHARACTERS:
        if ord(symbol) not in glyph_names:
            continue

        glyph = glyphs[glyph_names[ord(symbol)]]
        pen = SVGPathPen(glyphs, ntos=lambda value: str(round(value)))
        # У шрифта ось Y смотрит вверх, у SVG вниз
        glyph.draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
        table[symbol] = [round(glyph.width), pen.getCommands()]

    return (static["name"].getDebugName(COPYRIGHT_NAME_ID),
            {"unitsPerEm": static["head"].unitsPerEm, "glyphs": table})


def main() -> None:
    """Пишет таблицу контуров всех начертаний"""
    extracted = {font: extract(*source) for font, source in SOURCES.items()}
    result = {"license": "SIL Open Font License 1.1, https://openfontlicense.org",
              "copyright": sorted({notice for notice, _ in extracted.values()}),
              "fonts": {font.value: data for font, (_, data) in extracted.items()}}

    GLYPHS_PATH.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
