# Framework Comparison: Todo Counter

The same simple counter component in different frameworks.

## Hyper (Proposed)

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

**LOC:** 10 lines
**Boilerplate:** 1 decorator
**Type Safety:** ✅ Full
**DX Score:** 10/10

---

## Phoenix LiveView

```elixir
# lib/app_web/live/counter_live.ex
defmodule AppWeb.CounterLive do
  use AppWeb, :live_view

  def mount(_params, _session, socket) do
    {:ok, assign(socket, count: 0)}
  end

  def handle_event("increment", _params, socket) do
    {:noreply, assign(socket, count: socket.assigns.count + 1)}
  end

  def render(assigns) do
    ~H"""
    <div>
      <p>Count: <%= @count %></p>
      <button phx-click="increment">+</button>
    </div>
    """
  end
end
```

**LOC:** 20 lines
**Boilerplate:** Module, mount, pattern matching
**Type Safety:** ⚠️ Some (typespecs)
**DX Score:** 7/10

---

## Laravel Livewire

```php
// app/Http/Livewire/Counter.php
<?php

namespace App\Http\Livewire;

use Livewire\Component;

class Counter extends Component
{
    public $count = 0;

    public function increment()
    {
        $this->count++;
    }

    public function render()
    {
        return view('livewire.counter');
    }
}
```

```blade
<!-- resources/views/livewire/counter.blade.php -->
<div>
    <p>Count: {{ $count }}</p>
    <button wire:click="increment">+</button>
</div>
```

**LOC:** 25 lines (2 files)
**Boilerplate:** Class, namespace, separate view
**Type Safety:** ❌ None
**DX Score:** 6/10

---

## React + useState (Client-side)

```jsx
// components/Counter.jsx
import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
    </div>
  );
}
```

**LOC:** 12 lines
**Boilerplate:** Import, export, setState
**Type Safety:** ⚠️ With TypeScript
**DX Score:** 8/10
**Note:** Client-side only, no server state

---

## Vue + Composition API (Client-side)

```vue
<!-- components/Counter.vue -->
<script setup>
import { ref } from 'vue';

const count = ref(0);

function increment() {
  count.value++;
}
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <button @click="increment">+</button>
  </div>
</template>
```

**LOC:** 17 lines
**Boilerplate:** ref(), .value
**Type Safety:** ⚠️ With TypeScript
**DX Score:** 8/10
**Note:** Client-side only, no server state

---

## HTMX + Flask (Current Hyper approach)

```python
# app/routes.py
from flask import Flask, session, render_template_string

@app.route('/counter')
def counter():
    count = session.get('count', 0)
    return render_template_string("""
        <div id="counter">
            <p>Count: {{ count }}</p>
            <button hx-post="/counter/increment" hx-target="#counter">+</button>
        </div>
    """, count=count)

@app.route('/counter/increment', methods=['POST'])
def increment():
    count = session.get('count', 0) + 1
    session['count'] = count
    return render_template_string("""
        <div id="counter">
            <p>Count: {{ count }}</p>
            <button hx-post="/counter/increment" hx-target="#counter">+</button>
        </div>
    """, count=count)
```

**LOC:** 22 lines
**Boilerplate:** Multiple routes, duplicate template
**Type Safety:** ✅ Full
**DX Score:** 5/10
**Note:** Full round-trip per click, template duplication

---

## Key Observations

### Code Density
- **Hyper:** 1.0x (baseline)
- **React/Vue:** 1.2x (close!)
- **LiveView:** 2.0x
- **Livewire:** 2.5x
- **HTMX/Flask:** 2.2x

### Developer Experience

**Hyper wins on:**
1. ✅ Least boilerplate
2. ✅ Single file (no view separation)
3. ✅ Pure Python (no DSL)
4. ✅ Type-safe by default
5. ✅ Server-side state (no client state management)
6. ✅ Real-time updates (unlike HTMX)

**Trade-offs:**
- ⚠️ Requires WebSocket (HTMX works without JS)
- ⚠️ Server cost per connection (vs stateless REST)

### When to Use What

**Hyper Live:**
- Interactive forms with validation
- Real-time dashboards
- Collaborative tools (chat, docs)
- Multi-step wizards
- Admin panels

**HTMX (current Hyper):**
- Static content sites
- Progressive enhancement
- SEO-critical pages
- Zero-JS requirement

**React/Vue:**
- Complex client-side logic
- Offline-first apps
- Game-like interactions
- Mobile apps

---

## The "Aha!" Moment

```python
# This is valid Python...
count = 0

def increment():
    nonlocal count
    count += 1

# ...that's also a component!
```

**That's Hyper.** No framework ceremony, just Python.
