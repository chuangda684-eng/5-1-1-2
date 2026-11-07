"""products.txt のASINを読み込み、形式だけを確認する。

Keepaへの通信と、スプレッドシートへの書き込みは行わない。
"""

import re
import sys
from pathlib import Path

MAX_ASINS = 5
ASIN_PATTERN = re.compile(r"^[A-Za-z0-9]{10}$")
PRODUCTS_PATH = Path(__file__).resolve().parent / "products.txt"


def load_asins(path=PRODUCTS_PATH):
    if not path.is_file():
        print("products.txt が見つかりません。課題フォルダに作成してください。")
        sys.exit(1)

    asins = []
    seen = set()
    text = path.read_text(encoding="utf-8-sig")

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ASIN_PATTERN.fullmatch(line) is None:
            print(f"ASINの形式が正しくありません（{line_number}行目）。")
            print("10文字の英数字で入力してください。")
            sys.exit(1)

        asin = line.upper()
        if asin in seen:
            print(f"警告: 重複したASINを除外しました（{line_number}行目）: {asin}")
            continue
        seen.add(asin)
        asins.append(asin)

    if not asins:
        print("ASINが1件もありません。products.txt に1件以上書いてください。")
        sys.exit(1)
    if len(asins) > MAX_ASINS:
        print(f"ASINは最大{MAX_ASINS}件です。現在{len(asins)}件あるため処理を中止しました。")
        sys.exit(1)
    return asins


def main():
    asins = load_asins()
    print(f"ASINを読み込みました: {len(asins)}件")
    for index, asin in enumerate(asins, start=1):
        print(f"{index}. {asin}")


if __name__ == "__main__":
    main()
