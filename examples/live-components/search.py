"""
Live search with debouncing

Shows:
- Debounced events
- Async handlers
- Loading states
- Empty states
"""

from hyper import live
import asyncio

@live
async def search():
    query = ""
    results = []
    loading = False

    async def search_items(q: str):
        nonlocal query, results, loading

        query = q
        if not q:
            results = []
            return

        loading = True
        # Force a render to show loading state
        await render()

        # Simulate API call
        await asyncio.sleep(0.3)

        # Mock search results
        all_items = [
            "Apple", "Apricot", "Banana", "Blueberry",
            "Cherry", "Cranberry", "Date", "Dragonfruit",
            "Elderberry", "Fig", "Grape", "Guava"
        ]

        results = [
            item for item in all_items
            if q.lower() in item.lower()
        ]
        loading = False

    t"""
    <div class="search-box">
        <input
            type="search"
            placeholder="Search fruits..."
            value="{query}"
            @input.debounce.300="search_items(value)"
        />

        {% if loading %}
        <div class="loading">Searching...</div>
        {% elif query and not results %}
        <div class="empty">No results for "{query}"</div>
        {% elif results %}
        <ul class="results">
            {% for item in results %}
            <li>{item}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    """
