# Hyper Live API Reference

Complete API reference for the proposed live state binding system.

---

## Core Decorator

### `@live`

Marks a component as stateful with WebSocket-based reactivity.

```python
from hyper import live

@live
def component():
    # Component body
    pass
```

**Parameters:** None

**Returns:** Wrapped component function

**Behavior:**
- Establishes WebSocket connection on mount
- Tracks module-level variables as state
- Binds functions as event handlers
- Auto-re-renders on state changes

**Example:**

```python
@live
def counter():
    count = 0

    def increment():
        nonlocal count
        count += 1

    t"""<button @click="increment">{count}</button>"""
```

---

## State Management

### Per-Connection State (Default)

```python
@live
def component():
    # Each connection has its own value
    count = 0
```

**Scope:** Unique per WebSocket connection
**Storage:** In-memory (process-local)
**Lifetime:** Connection duration
**Use Cases:** Forms, user-specific UI, games

---

### `shared(initial_value)`

Creates shared state across all connections.

```python
from hyper import shared

messages = shared([])

@live
def chat():
    def send(text: str):
        messages.append(text)
        broadcast()  # Updates all clients
```

**Parameters:**
- `initial_value`: Initial state value (any JSON-serializable type)

**Returns:** Reactive proxy to shared state

**Behavior:**
- Changes propagate to all connected clients
- Thread-safe (uses locks internally)
- Triggers `broadcast()` automatically if set

**Example:**

```python
# Shared counter across all users
visits = shared(0)

@live
def visitor_count():
    def increment():
        visits.value += 1
        # All connected clients see update

    t"""<p>Total visits: {visits.value}</p>"""
```

---

### `persistent(model, **filters)`

Binds to a database-backed model.

```python
from hyper import persistent
from app.models import User

@live
def profile():
    user = persistent(User, id=current_user.id)

    def update_name(name: str):
        user.name = name
        user.save()  # Persists to DB

    t"""<input value="{user.name}" @input="update_name(value)" />"""
```

**Parameters:**
- `model`: Database model class
- `**filters`: Query filters to load instance

**Returns:** Reactive model instance

**Behavior:**
- Loads from DB on component mount
- Auto-saves on state changes (configurable)
- Validates using model constraints

---

## Event Binding

### Syntax: `@event="handler"`

Binds DOM events to Python handlers.

```python
<button @click="increment">+</button>
<form @submit="save">...</form>
<input @input="search" />
<select @change="filter" />
```

**Supported Events:**
- `@click` - Mouse clicks
- `@submit` - Form submission
- `@input` - Input value changes
- `@change` - Select/checkbox changes
- `@focus` / `@blur` - Focus events
- `@keydown` / `@keyup` - Keyboard events
- Any standard DOM event (use lowercase)

---

### Event Modifiers

Chain modifiers with dots: `@event.modifier="handler"`

#### `.prevent`

Prevents default browser behavior (e.g., form submission).

```python
<form @submit.prevent="save">
    # Won't reload page
</form>
```

#### `.stop`

Stops event propagation (like `event.stopPropagation()`).

```python
<div @click="outer">
    <button @click.stop="inner">
        # Doesn't trigger outer click
    </button>
</div>
```

#### `.debounce` or `.debounce.{ms}`

Debounces the event (waits for typing to stop).

```python
# Default: 300ms
<input @input.debounce="search" />

# Custom delay
<input @input.debounce.500="search" />
```

#### `.throttle.{ms}`

Throttles the event (rate limits).

```python
# Max once per 100ms
<button @click.throttle.100="save">
    Save (rate limited)
</button>
```

#### Combining Modifiers

```python
<form @submit.prevent.stop="save">
    # Both prevent and stop
</form>

<input @input.debounce.500.stop="search">
    # Debounced by 500ms + stops propagation
</input>
```

---

### Event Parameters

Pass arguments to handlers using function call syntax.

#### From Form Inputs

```python
<form @submit="save(name, email)">
    <input name="name" />
    <input name="email" />
</form>

def save(name: str, email: str):
    # name and email auto-extracted from form
    pass
```

#### From Element Value

```python
<input @input="search(value)" />

def search(value: str):
    # 'value' is special keyword for input value
    pass
```

#### Literal Values

```python
<button @click="delete(123)">Delete</button>
<button @click="setColor('red')">Red</button>

def delete(id: int):
    pass

def setColor(color: str):
    pass
```

#### Mixed Parameters

```python
<input name="query" @input="search(value, 'products', 10)" />

def search(query: str, category: str, limit: int):
    # query from input, category and limit are literals
    pass
```

---

## Lifecycle Hooks

### `on_mount()`

Called when client connects (WebSocket opened).

```python
@live
def component():
    def on_mount():
        print("User connected!")
        # Initialize state, subscribe to events, etc.
```

**Use Cases:**
- Initialize timers
- Subscribe to external events
- Log analytics
- Load initial data

---

### `on_unmount()`

Called when client disconnects (WebSocket closed).

```python
@live
def component():
    def on_unmount():
        print("User disconnected!")
        # Cleanup, unsubscribe, save state, etc.
```

**Use Cases:**
- Cancel timers
- Unsubscribe from events
- Save state to DB
- Log session duration

---

### `on_error(error: Exception)`

Called when an error occurs during event handling.

```python
@live
def component():
    def on_error(error: Exception):
        print(f"Error: {error}")
        # Show error message to user, log to Sentry, etc.
```

---

## Broadcasting

### `broadcast()`

Sends updates to all connected clients (for shared state).

```python
from hyper import shared, broadcast

messages = shared([])

@live
def chat():
    def send(text: str):
        messages.append(text)
        broadcast()  # Notify all clients
```

**Parameters:** None

**Behavior:**
- Re-renders component for all connections
- Sends diff to each connected WebSocket
- Only affects components using shared state

**Auto-broadcast:** Set `auto_broadcast=True` on `shared()` to broadcast automatically:

```python
messages = shared([], auto_broadcast=True)

@live
def chat():
    def send(text: str):
        messages.append(text)
        # No need to call broadcast() - automatic!
```

---

### `broadcast_to(connection_ids: list[str])`

Broadcasts to specific connections.

```python
@live
def admin_panel():
    def notify_admins(message: str):
        admin_connections = get_admin_connections()
        broadcast_to(admin_connections, {
            "type": "notification",
            "message": message
        })
```

---

## Async Support

All handlers can be `async` functions.

```python
@live
async def search():
    query = ""
    results = []

    async def search_items(q: str):
        nonlocal query, results
        query = q

        # Async API call
        results = await api.search(q)

    t"""
    <input @input.debounce="search_items(value)" />
    <ul>
        {% for item in results %}
        <li>{item}</li>
        {% endfor %}
    </ul>
    """
```

**Behavior:**
- Framework awaits async handlers
- Component doesn't re-render until handler completes
- Use `await render()` to force intermediate renders

**Example: Loading States**

```python
@live
async def data():
    loading = False
    items = []

    async def load():
        nonlocal loading, items

        loading = True
        await render()  # Show loading spinner

        items = await fetch_items()
        loading = False
        await render()  # Show items
```

---

## Manual Rendering

### `await render()`

Forces an immediate re-render and update to client.

```python
@live
async def progress():
    percent = 0

    async def process():
        for i in range(100):
            percent = i
            await render()  # Update UI for each step
            await asyncio.sleep(0.1)
```

**Use Cases:**
- Show progress during long operations
- Display loading states
- Animate state transitions

---

## Configuration

### Component-Level Options

Pass options to `@live`:

```python
@live(
    debounce=300,           # Default debounce for all events
    transport="websocket",  # or "sse", "polling"
    fallback="htmx",        # Fallback for no-JS
    reconnect=True,         # Auto-reconnect on disconnect
    max_reconnects=5        # Max reconnection attempts
)
def component():
    pass
```

---

### Global Configuration

```python
# config.py
LIVE_CONFIG = {
    "transport": "websocket",
    "reconnect_attempts": 5,
    "reconnect_backoff": [1, 2, 5, 10, 30],  # seconds
    "heartbeat_interval": 30,  # seconds
    "max_message_size": 1024 * 1024,  # 1MB
    "compression": True,
    "state_backend": "memory",  # or "redis"
}
```

---

## Type Safety

All handlers are type-checked at runtime.

```python
@live
def form():
    def save(name: str, age: int, admin: bool):
        # Type validation happens automatically
        # Client sends: {"name": "Alice", "age": "30", "admin": "true"}
        # Server receives: name="Alice" (str), age=30 (int), admin=True (bool)
        pass
```

**Supported Types:**
- `str`, `int`, `float`, `bool`
- `list[T]`, `dict[K, V]`
- `Optional[T]`
- `Literal["a", "b", "c"]`
- Pydantic models
- Dataclasses

**Validation Errors:**

```python
def save(age: int):
    # If client sends non-integer, validation fails
    # Error sent back to client:
    # {"error": "Invalid parameter 'age': expected int, got str"}
    pass
```

---

## Error Handling

### Client-Side Errors

Validation errors return JSON error response:

```json
{
  "type": "error",
  "field": "age",
  "message": "Must be a valid integer"
}
```

Handle in component:

```python
@live
def form():
    error = None

    def on_error(e: Exception):
        nonlocal error
        error = str(e)

    t"""
    {% if error %}
    <div class="error">{error}</div>
    {% endif %}
    """
```

### Server-Side Errors

Unhandled exceptions:
1. Logged to console/Sentry
2. Don't crash the server
3. Return generic error to client
4. Call `on_error()` hook if defined

```python
@live
def component():
    def risky_operation():
        if random.random() < 0.1:
            raise ValueError("Random failure!")
        # ...

    def on_error(error: Exception):
        # Log to Sentry, show toast, etc.
        log_error(error)
```

---

## Testing

### Unit Tests

Test handlers like normal Python functions:

```python
def test_counter():
    from app.live.counter import increment

    # Setup state
    count = 0

    # Test handler
    increment()

    assert count == 1
```

### Integration Tests

Use test client:

```python
from hyper.testing import LiveClient

def test_counter_component():
    client = LiveClient()

    # Connect to component
    component = client.connect("/live/counter")

    # Trigger event
    component.trigger("increment")

    # Assert state
    assert component.state["count"] == 1

    # Assert HTML
    assert "Count: 1" in component.html
```

### E2E Tests

Use Playwright/Selenium:

```python
def test_counter_e2e(page):
    page.goto("/counter")

    # Wait for WebSocket connection
    page.wait_for_function("window.hyperLive?.ws?.readyState === 1")

    # Click button
    page.click("button:text('+')")

    # Assert update
    assert page.text_content("p") == "Count: 1"
```

---

## Progressive Enhancement

### Fallback to HTMX

```python
@live(fallback="htmx")
def counter():
    count = session.get("count", 0)

    def increment():
        nonlocal count
        count += 1
        session["count"] = count

    t"""
    <div>
        <p>Count: {count}</p>
        <!-- With JS: @click uses WebSocket -->
        <!-- No JS: form POSTs to server -->
        <form method="POST" action="?increment" @submit="increment">
            <button>+</button>
        </form>
    </div>
    """
```

**Behavior:**
- JavaScript enabled: WebSocket + live updates
- JavaScript disabled: Form POST + page refresh
- Same component code works both ways!

---

## Performance Tips

### 1. Debounce Input Events

```python
# Bad: Sends event on every keystroke
<input @input="search" />

# Good: Waits for typing to stop
<input @input.debounce="search" />
```

### 2. Use `@change` Instead of `@input`

```python
# For selects, checkboxes - use @change
<select @change="filter">...</select>
```

### 3. Limit Re-renders

```python
@live
def expensive():
    def handler():
        # Do work
        complex_computation()

        # Only re-render if state changed
        if state_changed:
            await render()
```

### 4. Batch Updates

```python
def update_many():
    # Bad: 100 re-renders
    for i in range(100):
        items.append(i)
        await render()

    # Good: 1 re-render
    items.extend(range(100))
    await render()
```

---

## Security

### CSRF Protection

Enabled by default for all live components:

```python
# Token auto-included in WebSocket handshake
# Validated on connection establishment
```

### Rate Limiting

```python
@live(rate_limit="10/minute")
def search():
    # Max 10 events per minute from this client
    pass
```

### Input Validation

Always validate user input:

```python
def save(name: str, age: int):
    # Type validation happens automatically
    # But also add business logic validation
    if age < 0 or age > 150:
        raise ValueError("Invalid age")

    if len(name) > 100:
        raise ValueError("Name too long")
```

### XSS Protection

All values are HTML-escaped by default:

```python
user_input = "<script>alert('xss')</script>"

t"""<p>{user_input}</p>"""
# Renders: <p>&lt;script&gt;alert('xss')&lt;/script&gt;</p>
```

To render raw HTML (dangerous!):

```python
t"""<p>{user_input|safe}</p>"""
# Only use for trusted content!
```

---

## Migration from HTMX

Step-by-step migration path:

### Before (HTMX)

```python
# app/routes.py
@app.get("/counter")
def counter():
    count = session.get("count", 0)
    return t"""
    <div id="counter">
        <p>Count: {count}</p>
        <button hx-post="/counter/increment" hx-target="#counter">+</button>
    </div>
    """

@app.post("/counter/increment")
def increment():
    count = session.get("count", 0) + 1
    session["count"] = count
    return t"""
    <div id="counter">
        <p>Count: {count}</p>
        <button hx-post="/counter/increment" hx-target="#counter">+</button>
    </div>
    """
```

### After (Live)

```python
# app/live/counter.py
from hyper import live

@live
def counter():
    count = 0

    def increment():
        nonlocal count
        count += 1

    t"""
    <div>
        <p>Count: {count}</p>
        <button @click="increment">+</button>
    </div>
    """
```

**Benefits:**
- ✅ 50% less code
- ✅ No template duplication
- ✅ No session management
- ✅ Real-time updates
- ✅ Type-safe

---

## FAQ

### Q: Can I mix live and non-live components?

**A:** Yes! Live and HTMX components work side-by-side.

```python
# Non-live
<{Header} />

# Live
<{LiveChat} />

# Non-live
<{Footer} />
```

### Q: How many connections can one server handle?

**A:** ~1000-5000 depending on activity. Use Redis + multiple processes for more.

### Q: Does it work without JavaScript?

**A:** Yes, with `fallback="htmx"` option.

### Q: What about mobile apps?

**A:** WebSockets work great in mobile web views. For native apps, expose a REST API instead.

### Q: How to deploy?

**A:** Any Python server with WebSocket support:
- Uvicorn (recommended)
- Gunicorn + uvicorn workers
- Hypercorn
- Daphne

### Q: How to scale horizontally?

**A:** Use Redis for shared state + message broadcasting:

```python
# config.py
LIVE_CONFIG = {
    "state_backend": "redis",
    "redis_url": "redis://localhost:6379"
}
```

---

## Summary

The entire API surface:

```python
# Core
from hyper import live

@live                    # Makes component stateful
def component():
    pass

# State
shared(value)            # Shared across connections
persistent(Model, id=1)  # DB-backed state

# Broadcasting
broadcast()              # Update all clients
broadcast_to([...])      # Update specific clients

# Rendering
await render()           # Force re-render

# Events
@click="handler"         # Event binding
@event.prevent           # Prevent default
@event.debounce.300      # Debounce 300ms

# Lifecycle
def on_mount(): pass     # On connect
def on_unmount(): pass   # On disconnect
def on_error(e): pass    # On error
```

**That's it.** Simple, powerful, pure Python.
