# Technical Implementation Sketch

A concrete (but simplified) implementation path for Hyper Live.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │   Hyper Live Runtime (hyper-live.js)        │  │
│  │   - WebSocket connection                     │  │
│  │   - Event serialization                      │  │
│  │   - DOM morphing                             │  │
│  └──────────────────┬──────────────────────────┘  │
│                     │                              │
└─────────────────────┼──────────────────────────────┘
                      │ WebSocket
                      │ (JSON messages)
┌─────────────────────┼──────────────────────────────┐
│                     │                              │
│  ┌──────────────────▼──────────────────────────┐  │
│  │   WebSocket Handler                         │  │
│  │   - Connection management                    │  │
│  │   - Event routing                            │  │
│  │   - State serialization                      │  │
│  └──────────────────┬──────────────────────────┘  │
│                     │                              │
│  ┌──────────────────▼──────────────────────────┐  │
│  │   Live Component                             │  │
│  │   - State tracking                           │  │
│  │   - Event handlers                           │  │
│  │   - Template rendering                       │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│                 Python Server                       │
└─────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. The `@live` Decorator

```python
# hyper/live.py
from functools import wraps
from typing import Callable
import inspect

def live(func: Callable):
    """
    Marks a component function as "live" (stateful, WebSocket-connected).

    Wraps the function to:
    1. Extract state variables and handlers
    2. Set up connection lifecycle
    3. Enable automatic re-rendering on state changes
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the component's local variables
        frame = inspect.currentframe()
        local_vars = frame.f_locals

        # Create a LiveComponent instance
        component = LiveComponent(
            render_func=func,
            initial_args=args,
            initial_kwargs=kwargs
        )

        # Track state variables
        for name, value in local_vars.items():
            if not name.startswith('_') and not callable(value):
                component.state[name] = value

        # Track event handlers
        for name, value in local_vars.items():
            if callable(value) and not name.startswith('_'):
                component.handlers[name] = value

        # Execute initial render
        return component.render()

    # Mark function as "live" for framework detection
    wrapper.__is_live__ = True

    return wrapper
```

### 2. LiveComponent Class

```python
# hyper/live.py
from typing import Any, Dict, Callable
import json
import hashlib

class LiveComponent:
    """
    Represents a stateful, live-updating component.

    Responsibilities:
    - Track component state
    - Handle events from client
    - Re-render on state changes
    - Diff and send updates to client
    """

    def __init__(self, render_func: Callable, initial_args, initial_kwargs):
        self.render_func = render_func
        self.args = initial_args
        self.kwargs = initial_kwargs

        # Component state
        self.state: Dict[str, Any] = {}
        self.handlers: Dict[str, Callable] = {}

        # Connection info
        self.component_id = self._generate_id()
        self.connection = None  # Set by WebSocket handler

        # Rendered HTML cache
        self._last_html = ""

    def _generate_id(self) -> str:
        """Generate unique component ID based on source location"""
        source = inspect.getsource(self.render_func)
        return hashlib.sha256(source.encode()).hexdigest()[:16]

    def render(self) -> str:
        """
        Execute the render function and return HTML.

        Injects state variables into the function's scope.
        """
        # Create a namespace with state variables
        namespace = {**self.state, **self.handlers}

        # Execute render function
        html = self.render_func(**namespace)

        # Wrap with live component markers
        html = f'''
        <div data-live-component="{self.component_id}">
            {html}
        </div>
        '''

        self._last_html = html
        return html

    async def handle_event(self, event_name: str, params: dict):
        """
        Handle an event from the client.

        1. Find the handler
        2. Execute with params
        3. Re-render
        4. Send diff to client
        """
        handler = self.handlers.get(event_name)
        if not handler:
            raise ValueError(f"Unknown event: {event_name}")

        # Execute handler (may modify state)
        if inspect.iscoroutinefunction(handler):
            await handler(**params)
        else:
            handler(**params)

        # Re-render
        new_html = self.render()

        # Compute diff
        diff = self._compute_diff(self._last_html, new_html)

        # Send to client
        if self.connection:
            await self.connection.send_json({
                "type": "update",
                "component_id": self.component_id,
                "diff": diff
            })

    def _compute_diff(self, old_html: str, new_html: str) -> dict:
        """
        Compute minimal diff between old and new HTML.

        For V1: just send full HTML (client-side diffing)
        For V2: could do server-side diffing for efficiency
        """
        return {
            "type": "morph",
            "html": new_html
        }
```

### 3. WebSocket Handler

```python
# hyper/live_handler.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json

class LiveConnectionManager:
    """
    Manages WebSocket connections for live components.
    """

    def __init__(self):
        # component_id -> LiveComponent
        self.components: Dict[str, LiveComponent] = {}

        # connection_id -> WebSocket
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, component_id: str):
        """Handle new WebSocket connection"""
        await websocket.accept()

        connection_id = str(id(websocket))
        self.connections[connection_id] = websocket

        # Get or create component instance
        component = self.components.get(component_id)
        if component:
            component.connection = websocket

        return component

    async def handle_message(self, websocket: WebSocket, message: dict):
        """
        Handle incoming message from client.

        Message format:
        {
            "type": "event",
            "component_id": "abc123",
            "event": "increment",
            "params": {}
        }
        """
        msg_type = message.get("type")

        if msg_type == "event":
            component_id = message["component_id"]
            event_name = message["event"]
            params = message.get("params", {})

            component = self.components.get(component_id)
            if component:
                await component.handle_event(event_name, params)

    async def disconnect(self, websocket: WebSocket):
        """Handle disconnection"""
        connection_id = str(id(websocket))
        self.connections.pop(connection_id, None)

        # Call component lifecycle hook
        for component in self.components.values():
            if component.connection == websocket:
                if hasattr(component, 'on_unmount'):
                    await component.on_unmount()

# Global manager instance
live_manager = LiveConnectionManager()

# WebSocket endpoint
async def live_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for live components.

    Route: /_live/ws
    """
    component = None

    try:
        # Initial connection
        await websocket.accept()

        # First message should be "connect" with component_id
        message = await websocket.receive_json()
        if message["type"] == "connect":
            component_id = message["component_id"]
            component = await live_manager.connect(websocket, component_id)

            if component and hasattr(component, 'on_mount'):
                await component.on_mount()

        # Message loop
        while True:
            message = await websocket.receive_json()
            await live_manager.handle_message(websocket, message)

    except WebSocketDisconnect:
        await live_manager.disconnect(websocket)
```

### 4. Client Runtime (JavaScript)

```javascript
// hyper/static/hyper-live.js

/**
 * Hyper Live Runtime
 *
 * Responsibilities:
 * 1. Detect live components on page
 * 2. Establish WebSocket connection
 * 3. Bind event listeners
 * 4. Send events to server
 * 5. Receive and apply updates
 */

class HyperLive {
  constructor() {
    this.ws = null;
    this.components = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  init() {
    // Find all live components
    document.querySelectorAll('[data-live-component]').forEach(el => {
      const componentId = el.dataset.liveComponent;
      this.components.set(componentId, el);
      this.bindEvents(el, componentId);
    });

    // Connect WebSocket
    this.connect();
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/_live/ws`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[Hyper Live] Connected');
      this.reconnectAttempts = 0;

      // Send "connect" message for each component
      this.components.forEach((el, componentId) => {
        this.send({
          type: 'connect',
          component_id: componentId
        });
      });
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('[Hyper Live] Disconnected');
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('[Hyper Live] Error:', error);
    };
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[Hyper Live] Max reconnection attempts reached');
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    console.log(`[Hyper Live] Reconnecting in ${delay}ms...`);

    setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  bindEvents(el, componentId) {
    // Find all elements with @event attributes
    el.querySelectorAll('[\\@click], [\\@submit], [\\@input], [\\@change]').forEach(target => {
      // Parse event binding
      const attrs = target.attributes;
      for (let attr of attrs) {
        if (attr.name.startsWith('@')) {
          const [eventType, ...modifiers] = attr.name.slice(1).split('.');
          const handler = attr.value;

          this.bindEvent(target, eventType, handler, modifiers, componentId);
        }
      }
    });
  }

  bindEvent(el, eventType, handler, modifiers, componentId) {
    el.addEventListener(eventType, async (e) => {
      // Handle modifiers
      if (modifiers.includes('prevent')) {
        e.preventDefault();
      }
      if (modifiers.includes('stop')) {
        e.stopPropagation();
      }

      // Extract parameters from handler expression
      const params = this.extractParams(handler, e, el);

      // Send event to server
      this.send({
        type: 'event',
        component_id: componentId,
        event: this.extractHandlerName(handler),
        params: params
      });
    }, {
      // Debounce if specified
      debounce: modifiers.find(m => m.startsWith('debounce'))
    });
  }

  extractHandlerName(expression) {
    // "increment" -> "increment"
    // "add_todo(text)" -> "add_todo"
    return expression.split('(')[0].trim();
  }

  extractParams(expression, event, el) {
    // Parse parameters from expression
    // "handler(name, email)" -> { name: inputValue, email: inputValue }

    const match = expression.match(/\((.*?)\)/);
    if (!match) return {};

    const paramNames = match[1].split(',').map(s => s.trim());
    const params = {};

    for (let paramName of paramNames) {
      if (paramName === 'value') {
        // Special case: use element value
        params.value = el.value;
      } else if (paramName.match(/^\d+$/)) {
        // Literal number
        params[paramName] = parseInt(paramName);
      } else if (paramName.match(/^['"].*['"]$/)) {
        // Literal string
        params[paramName] = paramName.slice(1, -1);
      } else {
        // Form input
        const form = el.closest('form');
        if (form) {
          const input = form.querySelector(`[name="${paramName}"]`);
          if (input) {
            params[paramName] = input.value;
          }
        }
      }
    }

    return params;
  }

  handleMessage(message) {
    if (message.type === 'update') {
      const componentId = message.component_id;
      const el = this.components.get(componentId);

      if (!el) return;

      // Apply diff
      if (message.diff.type === 'morph') {
        this.morphDOM(el, message.diff.html);
      }

      // Re-bind events (since DOM changed)
      this.bindEvents(el, componentId);
    }
  }

  morphDOM(el, newHTML) {
    // Use morphdom library for efficient DOM updates
    // For V1: just innerHTML replacement
    const parser = new DOMParser();
    const doc = parser.parseFromString(newHTML, 'text/html');
    const newEl = doc.querySelector('[data-live-component]');

    if (newEl) {
      el.innerHTML = newEl.innerHTML;
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

// Auto-initialize on DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.hyperLive = new HyperLive();
    window.hyperLive.init();
  });
} else {
  window.hyperLive = new HyperLive();
  window.hyperLive.init();
}
```

---

## Integration with Hyper

### 1. Auto-inject Runtime Script

```python
# hyper/templates/base.py

def render_page(content: str, has_live_components: bool = False):
    """Wraps page content with <html>, <head>, <body>"""

    scripts = []
    if has_live_components:
        scripts.append('<script src="/_live/runtime.js"></script>')

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        {content}
        {''.join(scripts)}
    </body>
    </html>
    """
```

### 2. Detect Live Components

```python
# hyper/compiler.py

def compile_component(source: str) -> Component:
    """Compile a component from source code"""

    # Parse AST
    tree = ast.parse(source)

    # Check if component has @live decorator
    is_live = any(
        isinstance(node, ast.FunctionDef) and
        any(d.id == 'live' for d in node.decorator_list if isinstance(d, ast.Name))
        for node in ast.walk(tree)
    )

    # ... rest of compilation

    component.is_live = is_live
    return component
```

### 3. Route Registration

```python
# hyper/app.py

from fastapi import FastAPI
from hyper.live_handler import live_websocket

app = FastAPI()

# Register WebSocket endpoint
app.websocket("/_live/ws")(live_websocket)

# Serve runtime script
app.get("/_live/runtime.js")(serve_runtime_js)
```

---

## State Management

### Per-Connection State (Default)

```python
@live
def counter():
    count = 0  # Unique per WebSocket connection

    # Each user has their own count
```

**Storage:** In-memory Python dict (fast, simple)

### Shared State

```python
from hyper import shared

# Shared across ALL connections
messages = shared([])

@live
def chat():
    def send(text: str):
        messages.append(text)
        broadcast()  # Updates all clients
```

**Storage:**
- V1: In-memory Python dict with locks
- V2: Redis for multi-process scaling

### Persistent State

```python
from hyper import persistent

@live
def profile():
    # Persisted to database
    user = persistent(User, id=current_user.id)

    def update_name(name: str):
        user.name = name
        user.save()  # Auto-saves
```

---

## Performance Considerations

### Message Size

**Bad:** Send full HTML every time (10KB+)
```json
{
  "type": "update",
  "html": "<div>...</div>"
}
```

**Good:** Send minimal diffs (< 1KB)
```json
{
  "type": "update",
  "patches": [
    { "path": "div/p/text", "value": "5" }
  ]
}
```

### Connection Scaling

- **< 1000 connections:** Single Python process OK
- **< 10K connections:** Multiple processes + Redis
- **> 10K connections:** Consider dedicated WebSocket server (Go/Rust)

### Memory per Connection

Estimate: ~5-10KB per connection (state + overhead)
- 1K connections = 5-10MB
- 10K connections = 50-100MB
- Totally reasonable!

---

## Next Steps

1. **Prototype `@live` decorator** (2-3 hours)
2. **Build WebSocket handler** (4-6 hours)
3. **Write client runtime** (6-8 hours)
4. **Test with counter example** (1-2 hours)
5. **Add `shared()` state** (2-3 hours)
6. **Polish DX** (ongoing)

**Total: ~20-30 hours for V1**

---

## Open Questions

1. **Session management:** How to tie WebSocket to HTTP session?
2. **Auth:** How to authenticate WebSocket connections?
3. **Scaling:** When to add Redis? How to handle multi-process?
4. **Error handling:** What happens if handler throws?
5. **Testing:** How to test live components?

Let's discuss! 🚀
