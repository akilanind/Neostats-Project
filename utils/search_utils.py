def perform_web_search(query: str) -> str:
    try:
        from duckduckgo_search import DDGS

        enriched_query = f"{query} India government scheme 2024"

        results_text: list[str] = []

        with DDGS() as ddgs:
            raw_results = list(ddgs.text(enriched_query, max_results=3))

        if not raw_results:
            return "No web search results found for this query."

        for i, result in enumerate(raw_results, start=1):
            title = result.get("title", "No title")
            snippet = result.get("body", "No description available.")
            url = result.get("href", "URL not available")

            results_text.append(
                f"[Web Result {i}]\n"
                f"Title  : {title}\n"
                f"Snippet: {snippet}\n"
                f"URL    : {url}"
            )

        separator = "\n" + "─" * 60 + "\n"
        return separator.join(results_text)

    except ImportError:
        error_msg = (
            "duckduckgo-search is not installed. Run: pip install duckduckgo-search"
        )
        print(f"[search_utils.py] {error_msg}")
        return "Web search unavailable."

    except Exception as e:
        print(f"[search_utils.py] perform_web_search failed: {e}")
        return "Web search unavailable."
