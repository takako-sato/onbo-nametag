#!/usr/bin/env python3
"""
複数画像の中央下に「施策名 名前」を一括で入れるスクリプト。
・フォルダを渡すと配下の全階層（フォルダ＞フォルダ＞画像 など）を再帰的に走査し、
  見つかった画像をその場で上書き（ファイル名は変更しない）。
・施策名は引数で指定、名前は --name で指定（省略時は「研修 二郎」）。
・フォントサイズは画像サイズ（短辺）に比例して自動調整。
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow が必要です: pip install Pillow")
    sys.exit(1)

# デフォルトの名前
AUTHOR_NAME = "研修 二郎"

# 日本語フォントの候補（太字優先 → 通常）
FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    os.path.expanduser("~/Library/Fonts/NotoSansCJK-Bold.ttc"),
    os.path.expanduser("~/Library/Fonts/NotoSansCJK-Regular.ttc"),
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/meiryob.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]

# テキスト色（#565CAA）、背景は白
TEXT_COLOR = "#565CAA"
BG_COLOR = "#ffffff"


def get_japanese_font(size: int):
    """利用可能な日本語フォントを返す（太字を優先）"""
    for path in FONT_CANDIDATES:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def add_caption(
    image_path: str,
    output_path: str,
    campaign_name: str,
    author: str = AUTHOR_NAME,
    margin_ratio: float = 0.04,
    text_ratio: float = 0.045,
    padding_ratio: float = 0.015,
    color: str = TEXT_COLOR,
    bg_color: str = BG_COLOR,
) -> None:
    """
    画像の中央下に「施策名 名前」を描画して保存する。
    テキストは太字・#565CAA、白背景＋余白付き。
    """
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    short = min(w, h)

    font_size = max(12, int(short * text_ratio))
    font = get_japanese_font(font_size)

    text = f"{campaign_name} {author}"

    try:
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        tw, th = font.getsize(text)

    padding = max(4, int(short * padding_ratio))
    margin = int(short * margin_ratio)

    x = (w - tw) // 2
    y = h - th - margin - padding

    x1 = x - padding
    y1 = y - padding
    x2 = x + tw + padding
    y2 = y + th + padding

    draw = ImageDraw.Draw(img)
    radius = max(2, padding // 2)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg_color, outline=None)
    draw.text((x, y), text, font=font, fill=color)

    out_path_lower = output_path.lower()
    if out_path_lower.endswith((".jpg", ".jpeg")):
        img = img.convert("RGB")
    img.save(output_path, quality=95)
    print(f"保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="複数画像の中央下に「施策名 名前」を一括で入れる"
    )
    parser.add_argument(
        "campaign_name",
        type=str,
        help="施策名（日付など。例: 20260217配信)",
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="+",
        help="フォルダ（複数可）。配下の全階層の画像を対象にする。ファイルを直接指定しても可",
    )
    parser.add_argument(
        "-n", "--name",
        type=str,
        default=AUTHOR_NAME,
        help="名前（デフォルト: 研修 二郎）",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="指定時のみ別フォルダへ出力（指定しない場合は元画像を上書き）",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="-o 使用時のみ。出力ファイル名の接尾辞（デフォルト: なし）",
    )
    parser.add_argument(
        "--text-size",
        type=float,
        default=0.045,
        help="文字サイズの比率（画像短辺に対する割合。デフォルト: 0.045）",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.04,
        help="下余白の比率（画像短辺に対する割合。デフォルト: 0.04）",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=0.015,
        help="テキスト周りの白背景の余白の比率（デフォルト: 0.015）",
    )
    args = parser.parse_args()

    allowed = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
    paths = []
    for p in args.input:
        path = Path(p).resolve()
        if path.is_dir():
            paths.extend([
                f for f in path.rglob("*")
                if f.is_file() and f.suffix.lower() in allowed
            ])
        elif path.is_file() and path.suffix.lower() in allowed:
            paths.append(path)
        else:
            print(f"スキップ（ファイル/フォルダなし）: {p}")

    paths = list(dict.fromkeys(paths))

    if not paths:
        print("対象画像がありません。")
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    for inp in paths:
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            # 出力ファイル名は入力の「ファイル名だけ」から作る（パス traversal 防止）
            base = inp.name
            safe_stem = Path(base).stem
            safe_suffix = Path(base).suffix
            out_path = output_dir / f"{safe_stem}{args.suffix}{safe_suffix}"
        else:
            out_path = inp

        add_caption(
            str(inp),
            str(out_path),
            args.campaign_name,
            author=args.name,
            margin_ratio=args.margin,
            text_ratio=args.text_size,
            padding_ratio=args.padding,
        )


if __name__ == "__main__":
    main()
