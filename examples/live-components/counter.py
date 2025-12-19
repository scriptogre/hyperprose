"""
Ultra-minimal live counter component

This demonstrates the core concept: state is just a variable,
handlers are just functions, @live makes it reactive.
"""

from hyper import live

@live
def counter():
    count = 0

    def increment():
        nonlocal count
        count += 1

    def decrement():
        nonlocal count
        count -= 1

    def reset():
        nonlocal count
        count = 0

    t"""
    <div class="counter">
        <h2>Count: {count}</h2>
        <div class="controls">
            <button @click="decrement">−</button>
            <button @click="reset">Reset</button>
            <button @click="increment">+</button>
        </div>
    </div>
    """
