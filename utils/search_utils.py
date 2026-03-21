def perform_web_search(query: str) -> str:
    """
    Performs a web search using DuckDuckGo to get the latest government scheme info.
    """
    try:
        from duckduckgo_search import DDGS

        # Add context to focus on Indian government schemes
        enriched_query = f"{query} India government scheme 2024 2025"

        results_text: list[str] = []

        with DDGS() as ddgs:
            # text() returns an iterator of results. Limit to top 3 for speed/token economy.
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
            "The 'duckduckgo-search' package is missing. "
            "Please run: pip install duckduckgo-search"
        )
        print(f"[search_utils.py] {error_msg}")
        return "Web search is currently unavailable (missing dependency)."

    except Exception as e:
        print(f"[search_utils.py] perform_web_search failed: {e}")
        return "Web search is currently unavailable due to an unexpected error."
