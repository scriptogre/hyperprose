# Hyper Live: Minimalist Server State Binding

> **"What if Phoenix LiveView was just Python?"**

This directory contains a complete proposal for adding real-time, stateful components to Hyper using the most minimalist API possible: **a single decorator**.

## The Vision

```python
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

That's it. No classes, no lifecycle methods, no state management libraries. Just Python.

## What's Inside

### 📖 Documentation

- **[live-state-proposal.md](./live-state-proposal.md)** - Full proposal with 3 design options, comparisons, and philosophy
- **[api-reference.md](./api-reference.md)** - Complete API documentation
- **[technical-sketch.md](./technical-sketch.md)** - Implementation details and architecture
- **[comparison.md](./comparison.md)** - Side-by-side comparison with LiveView, Livewire, React, Vue

### 💻 Example Components

- **[counter.py](./counter.py)** - Ultra-minimal counter (the "Hello World")
- **[todo_list.py](./todo_list.py)** - Todo list with validation
- **[search.py](./search.py)** - Debounced search with loading states
- **[chat.py](./chat.py)** - Real-time chat with shared state
- **[form_validation.py](./form_validation.py)** - Live form validation with Pydantic

## Key Features

### 1. **Pure Python**
No custom syntax, no DSL. Just type hints and decorators.

```python
count: int = 0  # State
def increment(): pass  # Handler
```

### 2. **Type-Safe**
Full type checking and validation, powered by Python's type system.

```python
def save(age: int, email: str):
    # Runtime validation: age must be int, email must be str
    pass
```

### 3. **Zero Boilerplate**
Single decorator, no classes, no lifecycle ceremony.

```python
@live  # That's all you need
def component():
    pass
```

### 4. **Plays Nice with HTMX**
Mix and match live components with regular HTMX components.

```python
# Regular HTMX component
<{Header} />

# Live stateful component
<{LiveChat} />
```

### 5. **Progressive Enhancement**
Works without JavaScript using automatic HTMX fallback.

```python
@live(fallback="htmx")
def form():
    # With JS: WebSocket + real-time
    # No JS: Form POST + refresh
    pass
```

## How It Works

```
┌─────────────┐                    ┌─────────────┐
│   Browser   │◄─── WebSocket ────►│   Server    │
│             │                    │             │
│  @click     │  {"type": "event"} │  handler()  │
│    └──────► │  ─────────────────►│  ─────────► │
│             │                    │  state += 1 │
│   DOM       │  {"type": "update"}│  render()   │
│  ◄────────  │  ◄─────────────────│  ◄────────  │
│   morph     │                    │             │
└─────────────┘                    └─────────────┘
```

1. User clicks button
2. Event sent to server via WebSocket
3. Python handler updates state
4. Component re-renders
5. Diff sent back to browser
6. DOM updates (morphed)

All automatically. No manual wiring.

## Comparison

### Lines of Code for a Counter

| Framework | LOC | Boilerplate |
|-----------|-----|-------------|
| **Hyper Live** | **10** | **1 decorator** |
| React | 12 | Import, export, useState |
| Vue | 17 | Script setup, ref, .value |
| Phoenix LiveView | 20 | Module, mount, assigns |
| Laravel Livewire | 25 | Class + separate view |
| HTMX + Flask | 22 | Multiple routes, session |

### Features

| Feature | Hyper | LiveView | Livewire | React |
|---------|-------|----------|----------|-------|
| Pure host language | ✅ | ✅ | ✅ | ⚠️ JSX |
| Type-safe | ✅ Full | ⚠️ Some | ❌ None | ⚠️ TS only |
| Server state | ✅ | ✅ | ✅ | ❌ Client |
| Zero boilerplate | ✅ | ❌ | ❌ | ❌ |
| Real-time | ✅ | ✅ | ✅ | ⚠️ Manual |
| Progressive enhancement | ✅ | ❌ | ❌ | ❌ |

## Design Philosophy

### 1. **Make the Server Do the Work**
State lives on the server. Client is a thin view layer.

### 2. **Type Hints as API**
Types aren't just documentation—they're the API.

```python
def handler(name: str, age: int):
    # Type validation happens automatically
    pass
```

### 3. **Convention Over Configuration**
```python
def on_mount():  # Special name = lifecycle hook
    pass

@click="handler"  # Special syntax = event binding
```

### 4. **Optimize for the Common Case**
Most components are simple. Make simple things trivial:

```python
@live
def component():
    state = value
    def handler(): pass
    t"""..."""
```

### 5. **Escape Hatches for Power Users**
Need manual rendering? `await render()`
Need shared state? `shared()`
Need persistence? `persistent()`

But you don't need them for 80% of cases.

## Real-World Examples

### Todo App (50 lines)
Complete todo app with add, toggle, delete, and filter.

```python
@live
def todos():
    items = []

    def add(text: str):
        items.append({"text": text, "done": False})

    def toggle(i: int):
        items[i]["done"] = not items[i]["done"]

    # ... template
```

### Live Search (30 lines)
Debounced search with loading states.

```python
@live
async def search():
    results = []

    async def search_items(query: str):
        nonlocal results
        results = await api.search(query)

    t"""<input @input.debounce="search_items(value)" />"""
```

### Real-Time Chat (40 lines)
Multi-user chat with presence.

```python
messages = shared([])

@live
def chat():
    def send(text: str):
        messages.append(text)
        broadcast()
```

## Performance

### Benchmarks (Estimated)

- **Event latency:** ~10-50ms (WebSocket round-trip)
- **Memory per connection:** ~5-10KB
- **Connections per server:** ~1,000-5,000 (single process)
- **With Redis:** ~10,000-50,000 (multi-process)

### Comparison to HTMX

| Metric | HTMX | Live |
|--------|------|------|
| Latency | 50-200ms | 10-50ms |
| Server load | Low | Medium |
| Stateful | ❌ | ✅ |
| Real-time | ❌ | ✅ |

### When to Use What

**Use Live for:**
- Interactive forms
- Real-time dashboards
- Collaborative tools
- Multi-step flows
- Games/simulations

**Use HTMX for:**
- Content sites
- Blogs/marketing
- SEO-critical pages
- Simple interactions

**Mix them!** Use Live for the interactive parts, HTMX for the rest.

## Implementation Status

### ✅ Designed
- API surface
- Event binding syntax
- State management
- Lifecycle hooks
- Type safety
- Progressive enhancement

### 🚧 Prototyping
- `@live` decorator
- WebSocket handler
- Client runtime
- DOM morphing

### 📋 Todo
- Redis backend
- Testing utilities
- Deployment guides
- Performance optimization
- Error reporting

## Getting Started (Future)

Once implemented:

```bash
# Install Hyper with Live support
pip install hyper[live]

# Create a live component
mkdir -p app/live
cat > app/live/counter.py << EOF
from hyper import live

@live
def counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
    t"""
    <div>
        <p>{count}</p>
        <button @click="increment">+</button>
    </div>
    """
EOF

# Run dev server
hyper dev

# Open http://localhost:8000/live/counter
```

## FAQ

**Q: Why not just use htmx?**
A: HTMX is great for request/response. Live is for stateful, real-time interactions.

**Q: Why not just use React?**
A: React requires client-side state management, API design, data fetching, etc. Live is server-rendered with automatic state sync.

**Q: How does it compare to Hotwire/Turbo?**
A: Similar goals, but Hyper Live uses WebSockets (faster) and has a more minimal API (single decorator vs. multiple libraries).

**Q: Can I use it in production?**
A: Not yet! This is a proposal. But the implementation is straightforward (~1000 LOC).

**Q: Will it be slow?**
A: No! WebSockets have ~10-50ms latency. Phoenix LiveView handles 10K+ connections per server.

**Q: What about scaling?**
A: Single server: 1-5K connections. With Redis: 10-50K. That's plenty for most apps.

## Contributing

This is a proposal! Feedback welcome:

1. **API Design:** Does the API feel Hyper-like?
2. **Use Cases:** What examples should we add?
3. **Implementation:** Want to help prototype?
4. **Documentation:** What's unclear?

## Inspiration

- **Phoenix LiveView** (Elixir) - Pioneered the server-state-over-WebSocket pattern
- **Laravel Livewire** (PHP) - Brought LiveView ideas to PHP
- **HTMX** (JS) - Proved hypermedia-driven apps are viable
- **Alpine.js** (JS) - Showed minimalist syntax can be powerful
- **SolidJS** (JS) - Fine-grained reactivity without VDOM
- **Svelte** (JS) - Compiler-based approach to reactivity

## License

Same as Hyper core (likely MIT or Apache 2.0).

---

## The Pitch

**Hyper Live is:**
- ✅ Simpler than LiveView (no Elixir)
- ✅ More type-safe than Livewire (Python!)
- ✅ More real-time than HTMX (WebSockets)
- ✅ More server-centric than React (no client state)
- ✅ More Pythonic than anything else (it's just Python!)

**One decorator. Zero ceremony. Pure Python.**

```python
@live
```

That's the whole API.

---

*Built with ❤️ by the Hyper community*
