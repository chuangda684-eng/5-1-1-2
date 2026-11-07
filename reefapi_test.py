"""ReefAPIでAmazon.co.jpの商品を1件取得するテスト。

スプレッドシートへは書き込まない。APIキーは表示しない。
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ENDPOINT = "https://api.reefapi.com/amazon/v1/product/detail"
MARKETPLACE = "co.jp"
TEST_ASIN = "B0BX2RKS3G"
TIMEOUT_SECONDS = 90


def load_api_key():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        print(".env が見つかりません。課題フォルダに .env を置いてください。")
        sys.exit(1)

    load_dotenv(env_path)
    api_key = os.getenv("REEFAPI_API_KEY", "").strip()
    if not api_key:
        print("REEFAPI_API_KEY が .env に設定されていません。")
        sys.exit(1)
    return api_key


def redact(text, api_key):
    if text is None:
        return ""
    hidden = str(text).replace(api_key, "[REDACTED]")
    return hidden[:500]


def error_message(payload):
    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        parts = [
            str(error.get(key))
            for key in ("code", "type", "message", "details")
            if error.get(key)
        ]
        return " ".join(parts)
    if error:
        return str(error)
    return ""


def product_from(payload):
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return {}
    product = data.get("product")
    if isinstance(product, dict):
        return product
    if data.get("asin") or data.get("title"):
        return data
    return {}


def stock_label(product):
    in_stock = product.get("in_stock")
    if in_stock is True:
        return "在庫あり"
    if in_stock is False:
        return "在庫なし"
    availability = product.get("availability")
    if isinstance(availability, str) and availability.strip():
        return availability.strip()
    return "在庫表示なし"


def price_label(product):
    if product.get("price_str"):
        return str(product["price_str"])
    if product.get("price") is None:
        return ""
    currency = product.get("currency_code") or ""
    if currency == "JPY":
        return f"{product['price']}円"
    return str(product["price"])


def fetch_product(api_key, asin):
    """商品を1件取得する。失敗してもプログラムは終了しない。"""
    try:
        response = requests.post(
            ENDPOINT,
            headers={
                "x-api-key": api_key,
                "content-type": "application/json",
            },
            json={"asin": asin, "marketplace": MARKETPLACE},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.Timeout:
        return {
            "ok": False,
            "status_code": None,
            "error": "ReefAPIが時間内に応答しませんでした。",
        }
    except requests.RequestException as error:
        return {
            "ok": False,
            "status_code": None,
            "error": redact(error, api_key),
        }

    try:
        payload = response.json()
    except ValueError:
        return {
            "ok": False,
            "status_code": response.status_code,
            "error": redact(response.text, api_key),
        }

    if response.status_code >= 400 or not payload.get("ok"):
        message = error_message(payload) or redact(response.text, api_key)
        return {
            "ok": False,
            "status_code": response.status_code,
            "error": redact(message, api_key),
        }

    product = product_from(payload)
    return {
        "ok": True,
        "status_code": response.status_code,
        "asin": product.get("asin") or asin,
        "title": product.get("title") or "",
        "price": price_label(product),
        "stock": stock_label(product),
        "error": "",
    }


def main():
    api_key = load_api_key()
    result = fetch_product(api_key, TEST_ASIN)
    if not result["ok"]:
        print("ReefAPIの呼び出しに失敗しました。")
        if result["status_code"] is not None:
            print(f"HTTPステータス: {result['status_code']}")
        if result["error"]:
            print(result["error"])
        sys.exit(1)

    print("ReefAPIの取得に成功しました")
    print(f"ASIN: {result['asin']}")
    print(f"商品名: {result['title'] or '取得できませんでした'}")
    print(f"価格: {result['price'] or '取得できませんでした'}")
    print(f"在庫状況: {result['stock']}")


if __name__ == "__main__":
    main()
