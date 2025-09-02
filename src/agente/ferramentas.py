from __future__ import annotations

from typing import List, Dict

import urllib.parse
import feedparser

from datetime import datetime, timedelta

from src.configuracao import NEWS_QUERY


def news_search(max_results: int = 8, days_back: int = 14) -> List[Dict[str, str]]:
    """Busca manchetes no Google News RSS e retorna uma lista de dicionários.

    Este código é defensivo: retorna strings vazias quando campos não existem
    e filtra por data usando `published_parsed` quando presente.
    """

    query_terms = NEWS_QUERY
    q = urllib.parse.quote(query_terms)
    url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    feed = feedparser.parse(url)
    cutoff = datetime.utcnow() - timedelta(days=days_back)

    results: List[Dict[str, str]] = []
    for entry in feed.entries[: max_results * 2]:
        link = entry.get("link", "")
        title = entry.get("title", "")
        published = entry.get("published_parsed")

        if published is not None:
            published_dt = datetime(*published[:6])
            if published_dt < cutoff:
                continue

        results.append({"title": title, "url": link})
        if len(results) >= max_results:
            break

    return results
