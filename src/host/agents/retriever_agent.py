import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urldefrag

import requests
from bs4 import BeautifulSoup


CONTENT_SELECTOR = ".et_pb_module.et_pb_post_content.et_pb_post_content_0_tb_body"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape and save EU AI Act full article content.")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("/Users/sefika/projects/eu-ai-act-ontology/memory/procedural/ai_act_full_content.json"),
    )
    parser.add_argument(
        "--url", "-u",
        default="https://artificialintelligenceact.eu/ai-act-explorer/",
    )
    parser.add_argument("--timeout", "-t", type=int, default=30)
    parser.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (compatible; AIActContentRetriever/1.0)",
    )
    return parser


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_soup(url: str, headers: dict, timeout: int) -> BeautifulSoup:
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def canonical_url(base_url: str, href: str) -> str:
    absolute = urljoin(base_url, href)
    absolute, _ = urldefrag(absolute)
    return absolute


def is_chapter_heading(text: str) -> bool:
    return bool(re.match(r"^Chapter\s+[IVXLC]+\b", text, re.IGNORECASE))


def is_article_text(text: str) -> bool:
    return bool(re.match(r"^Article\s+\d+[a-zA-Z]?\b", text, re.IGNORECASE))


def is_annex_text(text: str) -> bool:
    return bool(re.match(r"^Annex\s+[IVXLC]+\b", text, re.IGNORECASE))


def extract_title_from_page(soup: BeautifulSoup, fallback: str) -> str:
    heading = soup.find(["h1", "h2", "h3"])
    if heading:
        return clean_text(heading.get_text(" ", strip=True))
    if soup.title:
        return clean_text(soup.title.get_text(" ", strip=True))
    return fallback




def extract_content_from_target_row(soup: BeautifulSoup) -> str:

    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()

    content = soup.select_one(CONTENT_SELECTOR)

    if not content:
        return ""

    for bad in content.select(
        ".et_pb_sidebar, .widget, .toc, .table-of-contents, nav, aside"
    ):
        bad.decompose()

    text = clean_text(content.get_text("\n", strip=True))

    stop_markers = [
        "\nSuitable Recitals",
        "\nCopy URL",
        "\nPrevious",
        "\nNext",
        "\n← Previous",
        "\nNext →",
    ]

    for marker in stop_markers:
        index = text.find(marker)
        if index != -1:
            text = text[:index]

    return clean_text(text)


def unique_items(items: list[dict], key: str = "url") -> list[dict]:
    seen = set()
    output = []

    for item in items:
        value = item.get(key)
        if not value or value in seen:
            continue

        seen.add(value)
        output.append(item)

    return output


def scrape_index_structure(
    base_url: str,
    headers: dict,
    timeout: int,
) -> tuple[list[dict], list[dict]]:
    soup = get_soup(base_url, headers, timeout)
    print("Scraping index structure for chapters and annexes...")
    print(f"Base URL: {base_url}")
    main = soup.select_one(
        ".et_pb_row.et_pb_row_2_tb_body.reverse-col-order.et_pb_gutters2"
    )

    if not main:
        main = soup.find("main") or soup.body or soup

    chapters: list[dict] = []
    annexes: list[dict] = []
    current_chapter: dict | None = None

    for element in main.find_all(["h1", "h2", "h3", "h4", "a"]):
        text = clean_text(element.get_text(" ", strip=True))
        if not text:
            continue

        if is_chapter_heading(text):
            current_chapter = {
                "chapter": text,
                "title": text,
                "articles": [],
            }
            chapters.append(current_chapter)
            continue

        if element.name == "a" and is_annex_text(text):
            href = element.get("href")
            if href:
                annexes.append({
                    "annex": text,
                    "title": text,
                    "url": canonical_url(base_url, href),
                })
            continue

        if current_chapter and element.name == "a" and is_article_text(text):
            href = element.get("href")
            if href:
                current_chapter["articles"].append({
                    "article": text,
                    "title": text,
                    "url": canonical_url(base_url, href),
                })

    for chapter in chapters:
        chapter["articles"] = unique_items(chapter["articles"])

    return chapters, unique_items(annexes)


def extract_content_from_target_row(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()

    content = soup.select_one(CONTENT_SELECTOR)

    if not content:
        print(f"WARNING: target div not found: {CONTENT_SELECTOR}")

        candidates = soup.select(".et_pb_row.reverse-col-order.et_pb_gutters2")
        print(f"Found fallback candidate rows: {len(candidates)}")

        content = candidates[0] if candidates else None

    if not content:
        return ""

    print("Extracting from div classes:", content.get("class"))

    for bad in content.select(
        ".et_pb_sidebar, .widget, .toc, .table-of-contents, nav, aside"
    ):
        bad.decompose()

    article_heading = None
    for heading in content.find_all(["h1", "h2", "h3"]):
        heading_text = clean_text(heading.get_text(" ", strip=True))
        if is_article_text(heading_text) or is_annex_text(heading_text):
            article_heading = heading
            break

    if article_heading:
        parts = [clean_text(article_heading.get_text(" ", strip=True))]

        for element in article_heading.find_all_next():
            if content not in element.parents:
                break

            text = clean_text(element.get_text(" ", strip=True))
            if not text:
                continue

            if text in {
                "Copy URL",
                "Suitable Recitals",
                "Previous",
                "Next",
                "← Previous",
                "Next →",
            }:
                break

            if element.find(["p", "li", "h1", "h2", "h3", "h4"]):
                continue

            if text not in parts:
                parts.append(text)

        return clean_text("\n".join(parts))

    return clean_text(content.get_text("\n", strip=True))

def enrich_articles(chapters: list[dict], headers: dict, timeout: int) -> list[dict]:
    for chapter in chapters:
        for article in chapter.get("articles", []):
            url = article.get("url")

            if not url:
                article["text"] = ""
                continue

            print(f"Scraping article: {article['title']}")
            print(f"Article URL: {url}")
            soup = get_soup(url, headers, timeout)
            article["page_title"] = extract_title_from_page(soup, article["title"])
            article["text"] = extract_content_from_target_row(soup)

    return chapters


def enrich_annexes(annexes: list[dict], headers: dict, timeout: int) -> list[dict]:
    for annex in annexes:
        url = annex.get("url")

        if not url:
            annex["text"] = ""
            continue

        print(f"Scraping annex: {annex['title']}")

        soup = get_soup(url, headers, timeout)
        annex["page_title"] = extract_title_from_page(soup, annex["title"])
        annex["text"] = extract_content_from_target_row(soup)

    return annexes


def scrape_all_ai_act_content(base_url: str, headers: dict, timeout: int) -> dict:
    print("Scraping index structure for chapters and annexes...")
    chapters, annexes = scrape_index_structure(base_url, headers, timeout)

    print(f"Found {len(chapters)} chapters and {len(annexes)} annexes.")
    print("Enriching article content...")

    chapters = enrich_articles(chapters, headers, timeout)

    print("Enriching annex content...")
    annexes = enrich_annexes(annexes, headers, timeout)

    return {
        "regulation": "EU AI Act",
        "citation": "Regulation (EU) 2024/1689",
        "source_url": base_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "chapters": chapters,
        "annexes": annexes,
    }


def save_all_content(output_file: Path, base_url: str, headers: dict, timeout: int) -> dict:
    print("Starting full content retrieval for EU AI Act...")

    data = scrape_all_ai_act_content(
        base_url=base_url,
        headers=headers,
        timeout=timeout,
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving full content to {output_file}...")

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def print_summary(data: dict, output_file: Path) -> None:
    chapters = data.get("chapters", [])
    articles_count = sum(len(ch.get("articles", [])) for ch in chapters)

    print("=== EU AI Act Full Content Summary ===")
    print(f"Regulation : {data.get('regulation')}")
    print(f"Chapters   : {len(chapters)}")
    print(f"Articles   : {articles_count}")
    print(f"Annexes    : {len(data.get('annexes', []))}")
    print(f"Output     : {output_file}")


if __name__ == "__main__":
    args = build_parser().parse_args()

    headers = {
        "User-Agent": args.user_agent,
    }

    full_content = save_all_content(
        output_file=args.output,
        base_url=args.url,
        headers=headers,
        timeout=args.timeout,
    )

    print_summary(full_content, output_file=args.output)