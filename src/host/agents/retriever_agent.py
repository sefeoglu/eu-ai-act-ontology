import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urldefrag
import argparse
import requests
from bs4 import BeautifulSoup



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


def extract_main_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return clean_text(main.get_text("\n", strip=True))


def extract_title_from_page(soup: BeautifulSoup, fallback: str) -> str:
    heading = soup.find(["h1", "h2", "h3"])
    if heading:
        return clean_text(heading.get_text(" ", strip=True))
    if soup.title:
        return clean_text(soup.title.get_text(" ", strip=True))
    return fallback


def is_chapter_heading(text: str) -> bool:
    return bool(re.match(r"^Chapter\s+[IVXLC]+\b", text, re.IGNORECASE))


def is_article_text(text: str) -> bool:
    return bool(re.match(r"^Article\s+\d+[a-zA-Z]?\b", text, re.IGNORECASE))


def is_annex_text(text: str) -> bool:
    return bool(re.match(r"^Annex\s+[IVXLC]+\b", text, re.IGNORECASE))


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
    main = soup.find("main") or soup.body or soup

    chapters: list[dict] = []
    annexes: list[dict] = []
    current_chapter: dict | None = None

    for element in main.find_all(["h1", "h2", "h3", "h4", "a"]):
        text = clean_text(element.get_text(" ", strip=True))
        if not text:
            continue

        if is_chapter_heading(text):
            current_chapter = {"chapter": text, "title": text, "articles": []}
            chapters.append(current_chapter)
            continue

        if is_annex_text(text):
            href = element.get("href") if element.name == "a" else None
            annexes.append({
                "annex": text,
                "title": text,
                "url": canonical_url(base_url, href) if href else "",
            })
            continue

        if current_chapter and element.name == "a" and is_article_text(text):
            href = element.get("href")
            if not href:
                continue
            current_chapter["articles"].append({
                "article": text,
                "title": text,
                "url": canonical_url(base_url, href),
            })

    for chapter in chapters:
        chapter["articles"] = unique_items(chapter["articles"])

    return chapters, unique_items(annexes)


def enrich_articles(chapters: list[dict], headers: dict, timeout: int) -> list[dict]:
    for chapter in chapters:
        for article in chapter.get("articles", []):
            url = article.get("url")
            if not url:
                article["text"] = ""
                continue
            soup = get_soup(url, headers, timeout)
            article["page_title"] = extract_title_from_page(soup, article["title"])
            article["text"] = extract_main_text(soup)
    return chapters


def enrich_annexes(annexes, headers, timeout) -> list[dict]:
    for annex in annexes:
        url = annex.get("url")
        if not url:
            annex["text"] = ""
            continue
        soup = get_soup(url, headers, timeout)
        annex["page_title"] = extract_title_from_page(soup, annex["title"])
        annex["text"] = extract_main_text(soup)
    return annexes


def scrape_all_ai_act_content(
    base_url,
    headers,
    timeout,
) -> dict:
    print("Scraping index structure for chapters and annexes...")
    chapters, annexes = scrape_index_structure(base_url, headers, timeout)
    print(f"Found {len(chapters)} chapters and {len(annexes)} annexes. Enriching content...")
    chapters = enrich_articles(chapters, headers, timeout)
    print("Enriched all articles. Now enriching annexes...")
    annexes = enrich_annexes(annexes, headers, timeout)

    return {
        "regulation": "EU AI Act",
        "citation": "Regulation (EU) 2024/1689",
        "source_url": base_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "chapters": chapters,
        "annexes": annexes,
    }


def save_all_content(
    output_file,
    base_url,
    headers,
    timeout,
) -> dict:
    headers = headers or default_headers
    print("Starting full content retrieval for EU AI Act...")
    data = scrape_all_ai_act_content(base_url=base_url, headers=headers, timeout=timeout)
    print("Full content retrieval completed.")
    output_file = Path(output_file)
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

    config_path = open("/Users/sefika/projects/eu-ai-act-ontology/config/api_configs.json", "r").read()
    config = json.loads(config_path)
    parser = argparse.ArgumentParser(description="Scrape and save EU AI Act full content.")
    default_base_url = config["crawler"]["base_url"]
    default_output_file = config["crawler"]["output_file"]
    default_request_timeout = config["crawler"]["request_timeout"]
    default_headers = config["crawler"]["headers"]
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=default_output_file,
        help=f"Output JSON file path (default: {default_output_file})",
    )
    parser.add_argument(
        "--url", "-u",
        default=default_base_url,
        help=f"Base URL to scrape (default: {default_base_url})",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=default_request_timeout,
        help=f"HTTP request timeout in seconds (default: {default_request_timeout})",
    )
    parser.add_argument(
        "--user-agent",
        default=default_headers["User-Agent"],
        help="User-Agent header string",
    )
    args = parser.parse_args()

    custom_headers = {**default_headers, "User-Agent": args.user_agent}

    full_content = save_all_content(
        output_file=args.output,
        base_url=args.url,
        headers=custom_headers,
        timeout=args.timeout,
    )
    print_summary(full_content, output_file=args.output)