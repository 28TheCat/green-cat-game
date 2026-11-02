# 资源压缩

游戏仍然是无需依赖和构建的静态网页。下面的工具仅在替换图片或修改文案时使用。

```powershell
python -m pip install pillow "fonttools[woff]"
python tools/optimize_assets.py
```

- 输入：`v1/assets/fruits/1.png`～`11.png` 和完整字体 `ZCOOLKuaiLe-Regular.ttf`。
- 输出：同尺寸无损 WebP、独立的 32px 标签页图标，以及 `GreenCat-UI.woff2`。
- 脚本逐张验证 RGBA 像素一致；不会修改 PNG、原始字体、OFL 授权或 `parts.js`。
- 字体保留 HTML、游戏脚本和样式中的现有字符以及 ASCII。修改文案后重新运行，新增字符才会包含在字体中。
- 浏览器默认加载 WebP 和 WOFF2；游戏图片加载失败会回退到 PNG。原始文件保留用于回退和后续重新压缩。
- 体积对照报告在 `output/playwright/asset-sizes.json`，该报告记录图片和字体体积，不代表真实网络加载耗时。
