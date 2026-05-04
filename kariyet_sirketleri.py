#!/usr/bin/env python3
"""
Kariyer.net üzerinde "Elektrik Elektronik Mühendisi" geçen iş ilanlarını bulur
ve yalnızca şirket adlarını listeler.

Kullanım:
  python kariyet_sirketleri.py
  python kariyet_sirketleri.py --query "Elektrik Elektronik Mühendisi"
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Set

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.kariyer.net/is-ilanlari"
DEFAULT_QUERY = "Elektrik Elektronik Mühendisi"


def fetch_company_names(query: str, max_pages: int = 3, timeout: int = 20) -> List[str]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
    )

    companies: Set[str] = set()

    for page in range(1, max_pages + 1):
        params = {"k": query, "p": page}
        response = session.get(BASE_URL, params=params, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Kariyer.net kart yapısında şirket adı için yaygın seçiciler
        selectors = [
            '[data-test="company-name"]',
            ".company-name",
            "a[href*='/firma-profil/']",
            "span[class*='company']",
        ]

        before = len(companies)
        for selector in selectors:
            for node in soup.select(selector):
                name = node.get_text(strip=True)
                if name:
                    companies.add(name)

        # Yeni şirket bulunmadıysa daha fazla sayfaya gitmeye gerek kalmayabilir
        if len(companies) == before and page > 1:
            break

    return sorted(companies)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kariyer.net ilanlarından şirket isimlerini çeker"
    )
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Arama kelimesi")
    parser.add_argument(
        "--max-pages", type=int, default=3, help="Taranacak maksimum sayfa sayısı"
    )
    args = parser.parse_args()

    try:
        companies = fetch_company_names(args.query, max_pages=args.max_pages)
    except requests.RequestException as exc:
        print(f"İstek hatası: {exc}", file=sys.stderr)
        return 1

    if not companies:
        print("Şirket bulunamadı. HTML yapısı değişmiş olabilir; seçicileri güncelleyin.")
        return 2

    for company in companies:
        print(company)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
