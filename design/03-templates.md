# Templates & Layouts

Hyper uses Python 3.14 t-strings for HTML templates with Python variables.

***

# Your First Template

```python
name = "Alice"

t"""
<h1>Hello {name}</h1>
"""
```

Put variables in curly braces.

***

# Simple Layouts

Layouts provide shared structure across pages.

## Create a Layout

Make a file: `app/pages/Layout.py`

```python
# app/pages/Layout.py

t"""
<!doctype html>
<html>
<head>
    <title>My Site</title>
</head>
<body>
    {...}
</body>
</html>
"""
```

Use `{...}` to mark where page content goes.

<details>
<summary><strong>Note:</strong> Alternative <code>slot</code> syntax</summary>

Use `slot` syntax instead of `...`:

```python
from hyper import slot

t"""
<body>
    {slot} <!-- or <{slot}/> -->
</body>
"""
```

Both are identical, except that `slot` requires an import.

This guide uses `...`.
</details>

## Use a Layout

```python
# app/pages/index.py
from app.pages import Layout

t"""
<{Layout}>
    <h1>Welcome Home!</h1>
    <p>This is the homepage.</p>
</{Layout}>
"""
```

Content between `<{Layout}>` and `</{Layout}>` replaces `{...}`.

## Layout Props

```python
# app/pages/Layout.py

title: str = "My Site"

t"""
<!doctype html>
<html>
<head>
    <title>{title}</title>
</head>
<body>
    {...}
</body>
</html>
"""
```

Pass props:

```python
# app/pages/index.py
from app.pages import Layout

t"""
<{Layout} title="Home">
    <h1>Welcome!</h1>
</{Layout}>
"""
```

Pass variables:

```python
# app/pages/index.py
from datetime import datetime
from app.pages import Layout

title = "Home | " + datetime.now().strftime("%Y")

t"""
<{Layout} title={title}>
    <h1>Welcome!</h1>
</{Layout}>
"""
```

## Shorthand Props

If a variable name matches a prop name, write `{name}`:

```python
# app/pages/index.py
from app.pages import Layout

title = "Home"

t"""
<{Layout} {title}>
    <h1>Welcome!</h1>
</{Layout}>
"""
```

This expands to `title={title}`.

## Default Slot Content

Use tag syntax to give the slot fallback content:

```python
# app/pages/Layout.py

t"""
<body>
    <{...}>
        <p>This is default content if slot is empty.</p>
    </{...}>
</body>
"""
```

***

# Advanced Layouts

## Named Slots

```python
# app/pages/Layout.py

t"""
<body>
    <aside>
        <{...} name="sidebar" />
    </aside>

    <main>
        {...}
    </main>
</body>
"""
```

```python
# app/pages/index.py
from app.pages import Layout

t"""
<{Layout}>
    <{...} name="sidebar">
        <nav>
            <a href="/settings">Settings</a>
        </nav>
    </{...}>

    <h1>Dashboard Content</h1>
</{Layout}>
"""
```

## Nest Layouts

```
app/
  pages/
  layouts/
  components/
```

```python
# app/layouts/BlogLayout.py
from app.layouts import Layout

title: str = t"Blog - {...}"

t"""
<{Layout} {title}>
    <div class="blog-container">
        {...}
    </div>
</{Layout}>
"""
```

### Exploring: inline `...` conditional (not decided)

Potential future idea (more magic, still to explore):

```python
title: str = (t"Blog - {...} if ... else "Blog")
```

***

# Components

Put reusable pieces in `app/components`.

## Create a Component

```python
# app/components/Button.py

text: str

t"""
<button {...}>
    {text}
</button>
"""
```

## Use a Component

```python
from app.components import Button

t'<{Button} text="Save" hx-post="/settings/save" class="btn btn-primary" />'
```

***

## For Loops

Use directive comments for block loops.

```python
from app.models import User

users: list[User]
user: User

t"""
<div class="users">
    <!--@ for {user} in {users} -->
        <div class="user">{user.name}</div>
    <!--@ end -->
</div>
"""
```

***

## Conditionals

```python
is_admin: bool

t"""
<nav>
    <!--@ if {is_admin} -->
        <a href="/admin">Admin</a>
    <!--@ else -->
        <a href="/account">Account</a>
    <!--@ end -->
</nav>
"""
```

***

## Advanced Attributes

### Conditional Classes
```python
classes = ["btn", {"active": is_active, "disabled": is_disabled}]
t'<button class={classes}>Click</button>'
```

### Dynamic Styles
```python
styles = {"color": "red", "font-weight": "bold"}
t'<p style={styles}>Important</p>'
```

### Data Attributes
```python
data = {"user-id": 123, "role": "admin"}
t'<div data={data}>Content</div>'
```

### Spread Attributes
```python
attrs = {"href": "https://example.com", "target": "_blank"}
t'<a {attrs}>Link</a>'
```

### Boolean Attributes
```python
t'<input disabled={True} readonly={False} />'
# <input disabled>
```

***

## Comments

HTML comments are sent to the browser.

```python
t"""
<!-- This appears in page source -->
<h1>Title</h1>
"""
```

Server-side comments are stripped from output.

```python
t"""
<!--# This won't appear in page source -->
<h1>Title</h1>
"""
```

Use directive comments for control flow.

```python
t"""
<!--@ if {show_title} -->
  <h1>Title</h1>
<!--@ end -->
"""
```

***

# Escaping & trusted HTML

Hyper escapes interpolated values by default.
To render trusted HTML, use the `:safe` format specifier:

```python
t"{post.html_content:safe}"
```

---

**[← Previous: Routing](02-routing.md)** | **[Back to Index](README.md)** | **[Next: Dependency Injection →](05-dependency-injection.md)**
