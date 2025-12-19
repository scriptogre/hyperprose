# Minimalist Server State Binding API Proposal

A LiveView/Livewire-style API for Hyper that maintains the framework's core principles: pure Python, type hints as API, zero boilerplate.

## Core Concept

**State lives on the server. Events trigger server-side updates. Client auto-syncs.**

## Design Options

### Option 1: The "Type Hint" Approach (Most Hyper-like)

```python
# app/components/Counter.py
from hyper import Live

count: Live[int] = 0  # Magic: Live[T] makes state reactive

def increment():
    count += 1

def decrement():
    count -= 1

t"""
<div>
    <h2>Count: {count}</h2>
    <button @click="increment">+</button>
    <button @click="decrement">-</button>
</div>
"""
```

**How it works:**
- `Live[T]` type hint signals: "this is server state"
- `@event="handler"` attributes bind to Python functions
- Component automatically connects via WebSocket on mount
- State changes auto-send diffs to client
- No explicit renders, no lifecycles, no boilerplate

**Pros:**
- Pure type hint API (most Hyper-like)
- Zero decorators or classes
- Works with existing component system
- Type-safe: `Live[int]` enforces types

**Cons:**
- Type annotation isn't really a type (it's runtime behavior)
- Might confuse static analyzers

---

### Option 2: The "Context Variable" Approach

```python
# app/components/TodoList.py
from hyper import live_state

todos = live_state([])  # Returns a special reactive proxy

def add_todo(text: str):
    todos.append({"text": text, "done": False})

def toggle(index: int):
    todos[index]["done"] = not todos[index]["done"]

t"""
<div>
    <form @submit="add_todo(text)">
        <input name="text" required />
    </form>

    <ul>
        {% for todo in todos %}
        <li>
            <input
                type="checkbox"
                checked={todo["done"]}
                @change="toggle({loop.index})"
            />
            {todo["text"]}
        </li>
        {% endfor %}
    </ul>
</div>
"""
```

**How it works:**
- `live_state(initial)` creates reactive state
- State changes tracked via proxy
- Auto-diffs and sends updates
- Event handlers can take arguments from client

**Pros:**
- Explicit state declaration
- Natural Python syntax (no type tricks)
- Easy to understand for beginners

**Cons:**
- Need to import `live_state()`
- Slightly more boilerplate

---

### Option 3: The "Ultra-Minimal" Approach (My Favorite)

```python
# app/live/chat.py
from hyper import live

messages = []
username: str  # Injected per-connection

@live  # Single decorator to make component "live"
def send(text: str):
    messages.append({"user": username, "text": text})

t"""
<div>
    <div id="messages">
        {% for msg in messages %}
        <p><b>{msg.user}:</b> {msg.text}</p>
        {% endfor %}
    </div>

    <form @submit="send(text)">
        <input name="text" autofocus />
    </form>
</div>
"""
```

**How it works:**
- Place component in `/app/live/` directory → automatically "live"
- Module-level variables = reactive state (just like current props!)
- Functions = event handlers
- Optional `@live` decorator for explicit opt-in
- That's it. Nothing else.

**Pros:**
- Absolute minimal API: just `@live` decorator
- State is just variables (Hyper style!)
- Convention over configuration (directory = behavior)
- Zero type tricks or proxies

**Cons:**
- Directory-based routing might be too magical
- Harder to mix live/non-live in same component

---

## Event Binding Syntax

All options use the same event syntax:

```python
# No arguments
<button @click="handler">

# With literal arguments
<button @click="handler(1, 'hello')">

# With form data (auto-serialized)
<form @submit="handler(name, email)">
    <input name="name" />
    <input name="email" />
</form>

# With element value
<input @input="search(value)" />

# Debounced
<input @input.debounce="search(value)" />

# Prevent default
<form @submit.prevent="handler">
```

**Why `@` prefix?**
- Visually distinct from `hx-*` (different mental model)
- Short and minimal
- Familiar from Vue/Alpine
- Valid HTML5 (data attributes work too)

---

## State Scoping Options

### Per-Connection State (LiveView style)

```python
# app/live/game.py
from hyper import live

@live
def index():
    score = 0  # Unique per WebSocket connection

    def increment():
        nonlocal score
        score += 1

    return t"""<div>Score: {score}</div>"""
```

Each user gets their own state. Perfect for forms, games, dashboards.

### Shared State (Chat/Collaboration)

```python
# app/live/chat.py
from hyper import live, shared

@live
messages = shared([])  # Shared across all connections

def send(text: str):
    messages.append(text)
    broadcast()  # Updates all connected clients

t"""
<div>
    {% for msg in messages %}
    <p>{msg}</p>
    {% endfor %}
</div>
"""
```

**Auto-broadcast:** Changes to `shared()` state trigger updates to all connected clients.

---

## Connection Lifecycle

### Automatic (Zero Config)

```python
# Components are automatically connected when rendered
# No setup needed!
```

### Explicit Control

```python
@live
def counter():
    count = 0

    def on_mount():
        """Called when client connects"""
        print("User connected!")

    def on_unmount():
        """Called when client disconnects"""
        print("User left")

    # ...
```

**Convention:** `on_mount` / `on_unmount` functions are auto-detected.

---

## Type Safety

```python
from hyper import live
from typing import Literal

@live
def component():
    # Type-safe enums
    status: Literal["idle", "loading", "success"] = "idle"

    # Validated inputs
    def update_age(age: int):  # Auto-validates client sends int
        if age < 0:
            raise ValueError("Age must be positive")
        self.age = age

    # Pydantic models work too!
    from pydantic import BaseModel

    class User(BaseModel):
        name: str
        email: str

    def update_user(user: User):  # Auto-validates
        save_user(user)
```

**Security:** All client inputs are validated against type hints. Type errors = automatic rejection.

---

## Behind the Scenes

### Transport Options

```python
# config.py
LIVE_TRANSPORT = "websocket"  # Default: fastest
LIVE_TRANSPORT = "sse"         # Server-Sent Events: simpler
LIVE_TRANSPORT = "polling"     # Fallback: most compatible
```

Auto-negotiates best available transport.

### Diff Algorithm

```python
# Option A: HTML diffing (simple)
- Morph DOM like htmx/idiomorph
- Send full HTML fragments
- Client-side diffing

# Option B: JSON state sync (efficient)
- Track state changes as JSON
- Send minimal diffs: {"count": 5}
- Client patches DOM based on data-live-* bindings
```

Hyper could start with **Option A** (simpler) and optimize to **Option B** later.

### JavaScript Runtime

```python
<!-- Auto-injected by framework -->
<script src="/_live/runtime.js"></script>

<!-- Connects automatically when @event attributes detected -->
<div data-live-component="counter" data-live-id="abc123">
    ...
</div>
```

**Runtime responsibilities:**
1. Establish WebSocket connection
2. Serialize events → send to server
3. Receive diffs → patch DOM
4. Handle reconnection

**Size target:** < 5kb gzipped (like Alpine.js)

---

## Progressive Enhancement

### Works without JavaScript

```python
@live(fallback="htmx")
def counter():
    count = request.session.get("count", 0)

    def increment():
        nonlocal count
        count += 1
        request.session["count"] = count

    t"""
    <div>
        <p>Count: {count}</p>
        <form method="POST" action="?increment" @submit="increment">
            <button>+</button>
        </form>
    </div>
    """
```

**Automatic fallback:**
- With JS: WebSocket + live updates
- No JS: Form POST + full page refresh
- Same component code!

---

## Migration Path

```python
# Step 1: Standard HTMX component (current Hyper)
<button hx-post="/counter/increment">+</button>

# Step 2: Add @live decorator (minimal change)
@live
def increment():
    count += 1

<button @click="increment">+</button>

# Step 3: That's it!
```

**Backward compatible:** Mix live components with HTMX components freely.

---

## Example: Real-World Dashboard

```python
# app/live/dashboard.py
from hyper import live, shared
from datetime import datetime

@live
def index():
    # Per-user state
    selected_date = datetime.now()

    # Shared real-time data
    metrics = shared(fetch_metrics())

    def select_date(date: str):
        nonlocal selected_date
        selected_date = datetime.fromisoformat(date)

    def refresh():
        metrics.update(fetch_metrics())
        broadcast()  # Update all connected users

    t"""
    <div class="dashboard">
        <header>
            <input
                type="date"
                value={selected_date.isoformat()}
                @change="select_date(value)"
            />
            <button @click="refresh">Refresh</button>
        </header>

        <div class="metrics">
            <div class="metric">
                <h3>Revenue</h3>
                <p>${metrics['revenue']}</p>
            </div>
            <div class="metric">
                <h3>Users</h3>
                <p>{metrics['users']}</p>
            </div>
        </div>
    </div>
    """
```

---

## Comparison to Alternatives

| Feature | Hyper Live | Phoenix LiveView | Laravel Livewire |
|---------|-----------|------------------|------------------|
| **Language** | Pure Python | Elixir | PHP |
| **Syntax** | Python + t-strings | HEEx templates | Blade templates |
| **State API** | Variables + decorator | `assign()` | `$property` |
| **Event Binding** | `@event="handler"` | `phx-click="handler"` | `wire:click="handler"` |
| **Type Safety** | Full (Python types) | Some (specs) | None |
| **Boilerplate** | None | Moderate | Moderate |
| **LOC for Counter** | ~10 | ~20 | ~25 |

---

## Implementation Complexity

### Minimal Viable Implementation

1. **Runtime (~500 LOC):**
   - WebSocket handler
   - Event router
   - State tracker (simple dict)
   - HTML differ (use morphdom/idiomorph)

2. **Client JS (~300 LOC):**
   - WebSocket connection
   - Event serialization
   - DOM morphing
   - Reconnection logic

3. **Framework Integration (~200 LOC):**
   - `@live` decorator
   - `shared()` state manager
   - Auto-injection of runtime script
   - Route handler for `/_live/ws`

**Total: ~1000 LOC** to ship V1.

### Advanced Features (Later)

- Presence (who's online)
- Uploads (file upload handling)
- Streams (infinite scroll, etc.)
- Optimistic UI (client-side predictions)

---

## My Recommendation: **Option 3 (Ultra-Minimal)**

```python
from hyper import live

@live  # That's the entire API
def counter():
    count = 0  # State

    def increment():  # Handler
        nonlocal count
        count += 1

    t"""
    <div>
        <p>{count}</p>
        <button @click="increment">+</button>
    </div>
    """
```

**Why:**
1. ✅ Pure Python (no type tricks)
2. ✅ Single decorator (minimal API surface)
3. ✅ State = variables (Hyper-like)
4. ✅ Zero boilerplate
5. ✅ Type-safe by default
6. ✅ Progressive enhancement
7. ✅ Plays nice with HTMX

**The Hyper way:** Make the simple case trivial, the complex case possible.

---

## Open Questions

1. **State serialization:** JSON by default? Pickle for complex types?
2. **Scaling:** Redis for shared state? In-memory OK for V1?
3. **Security:** CSRF tokens? Rate limiting?
4. **Naming:** `@live`, `@realtime`, `@reactive`?
5. **Client runtime:** Custom or wrap Alpine/htmx?

## Next Steps

If this direction resonates:
1. Prototype the `@live` decorator
2. Build minimal WebSocket handler
3. Create proof-of-concept client runtime
4. Test with 2-3 real examples (counter, chat, form)
5. Iterate on DX

---

*This proposal maintains Hyper's DNA: pure Python, type hints, zero magic, maximum simplicity.*
