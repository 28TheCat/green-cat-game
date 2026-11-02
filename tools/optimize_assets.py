"""开发时运行：python -m pip install pillow 'fonttools[woff]'，再运行此脚本。
生成无损 WebP 和游戏文字的 WOFF2 子集，保留原始 PNG、字体及授权。
图片尺寸和透明通道不变，不重新生成碰撞参数。
"""
import json
from pathlib import Path

from PIL import Image
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FRUITS = ROOT / 'v1/assets/fruits'
FONTS = ROOT / 'v1/assets/fonts'


def main():
    images = []
    for i in range(1, 12):
        source = FRUITS / f'{i}.png'
        target = source.with_suffix('.webp')
        with Image.open(source) as im:
            original = im.convert('RGBA')
            original.save(target, 'WEBP', lossless=True, exact=True, method=6)
            with Image.open(target) as encoded:
                assert original.size == encoded.size
                assert original.tobytes() == encoded.convert('RGBA').tobytes(), source
        images.append({'name': source.name, 'before': source.stat().st_size, 'after': target.stat().st_size})

    # 标签页图标单独缩小，避免浏览器为 32px 图标再次请求整张角色图。
    with Image.open(FRUITS / '1.png') as im:
        icon = im.convert('RGBA').resize((32, 32), Image.Resampling.LANCZOS)
        icon.save(ROOT / 'v1/assets/favicon.webp', 'WEBP', lossless=True, exact=True, method=6)

    # 包含 HTML、游戏文本、样式以及 ASCII；未来修改文案后重新运行即可。
    paths = ['v1/index.html', 'v1/game.js', 'v1/style.css', 'v1/garden.css']
    text = ''.join((ROOT / path).read_text(encoding='utf-8') for path in paths)
    text += ''.join(chr(i) for i in range(32, 127))
    source_font = FONTS / 'ZCOOLKuaiLe-Regular.ttf'
    target_font = FONTS / 'GreenCat-UI.woff2'
    font = TTFont(source_font, recalcTimestamp=False)
    supported = set(font.getBestCmap()) & set(map(ord, text))
    options = subset.Options()
    options.flavor = 'woff2'
    options.recalc_timestamp = False
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=supported)
    subsetter.subset(font)
    font.flavor = 'woff2'
    font.save(target_font)
    with TTFont(target_font) as result:
        assert supported <= set(result.getBestCmap()), 'Font lost required glyphs'

    report = {
        'images': images,
        'font': {'before': source_font.stat().st_size, 'after': target_font.stat().st_size, 'glyphs': len(supported)},
    }
    report['before'] = sum(i['before'] for i in images) + report['font']['before']
    report['after'] = sum(i['after'] for i in images) + report['font']['after']
    report['reduction_percent'] = round((1 - report['after'] / report['before']) * 100, 1)
    output = ROOT / 'output/playwright/asset-sizes.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
