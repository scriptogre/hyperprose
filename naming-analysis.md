# Hyper Framework Naming Analysis

## Framework Purpose & Identity

### Core Purpose
Hyper is a **Python-powered static site generator** (with future SSR capabilities) that uses Python 3.14's t-strings for templating, built for speed with a Rust CLI.

### Scope
- **Primary**: Static Site Generation (SSG) with file-based routing
- **Future**: Server-Side Rendering (SSR) with dependency injection
- **Content**: Markdown/JSON/YAML collections with Python dataclasses
- **Build**: Rust CLI for millisecond builds and instant hot reload
- **Deploy**: Zero runtime dependencies, pure static output

### Distinguishing Characteristics

1. **Python-First Philosophy**
   - Full Python ecosystem at build time (not a template language)
   - Native Python 3.14 t-strings for templates
   - Type-safe with IDE autocomplete and type hints
   - Any PyPI package available at build time

2. **Simplicity Principles**
   - Convention over configuration (file structure = URL structure)
   - "Simple things simple, powerful when needed"
   - No boilerplate (unlike Astro's `getStaticPaths()`)
   - Start with dicts, upgrade to dataclasses when needed

3. **Performance Architecture**
   - Compile-time structure, runtime values
   - HTML parsing happens once during compilation
   - Generated code is readable Python (no magic)
   - Minimal runtime dependencies (just escape + format utilities)

4. **Developer Experience**
   - Clear error messages (Rust/Elm compiler style: show, not tell)
   - `.pyi` stub generation for IDE support
   - Inspectable generated code
   - Hot reload and incremental builds

5. **Hypermedia-Driven**
   - Built for HTMX patterns
   - Fragments for partial rendering
   - Dependency analysis for minimal re-renders
   - Future hyper-diff integration

### Key Technical Innovations

- **Fragments**: Render parts independently with automatic dependency tracking
- **Content Collections**: Python dataclasses for structured content
- **Dynamic Routes**: `[param]` syntax with type-safe injection
- **Compile-time Optimization**: Structure parsed once, values interpolated at runtime

---

## Proposed Names

### Tier 1: Strongest Candidates

#### 1. **Loom**
- **Meaning**: A tool for weaving fabric; creates interconnected structures
- **Relevance**: Perfect metaphor for weaving templates, content, and components into websites
- **Strengths**:
  - Directly relates to web development (the "web" metaphor)
  - Short, memorable, one syllable
  - Evokes craft and precision
  - Distinctive enough to be searchable
  - .com available in various forms (getloom.com, loomhq.com exist, but loom.dev might be available)
- **Brand Feel**: Craftsman-like, purposeful, structural

#### 2. **Forge**
- **Meaning**: A place where metal is heated and shaped; to create or form
- **Relevance**: Building and crafting static sites with precision
- **Strengths**:
  - Strong association with creation and building
  - Implies heat/speed (fast builds)
  - Craftsmanship and quality
  - Very searchable and distinctive
  - Tech-friendly (many dev tools use forge/build metaphors)
- **Brand Feel**: Powerful, professional, maker-focused

#### 3. **Prism**
- **Meaning**: An optical element that refracts light; transforms and clarifies
- **Relevance**: Transforms Python/content into HTML, clarifies structure
- **Strengths**:
  - Modern, technical feel
  - Suggests transformation and clarity
  - Unique in the SSG space
  - Highly searchable
  - Relates to compile-time optimization (light/clarity)
- **Brand Feel**: Modern, precise, transformative

### Tier 2: Strong Alternatives

#### 4. **Beam**
- **Meaning**: A ray of light; a structural support
- **Relevance**: Speed (light speed), structure (HTML structure), clarity
- **Strengths**:
  - Short, punchy (one syllable)
  - Dual meaning (light + structure) fits framework
  - Fast/performant connotation
  - Simple and memorable
- **Brand Feel**: Fast, clean, structural

#### 5. **Volt**
- **Meaning**: Unit of electrical potential; energy and power
- **Relevance**: Speed, energy, the "charge" of fast builds
- **Strengths**:
  - Tech/electrical theme fits Rust CLI speed
  - Short and punchy
  - Energetic and modern
  - Highly distinctive
- **Brand Feel**: Energetic, fast, powerful

#### 6. **Quill**
- **Meaning**: A writing instrument; tool for creating content
- **Relevance**: Writing content, creating pages, authoring
- **Strengths**:
  - Perfect for content-focused SSG
  - Elegant and refined
  - Distinctive in tech space
  - Easy to remember
- **Brand Feel**: Elegant, content-focused, writerly

### Tier 3: Worthy Contenders

#### 7. **Rift**
- **Meaning**: A break or split; a portal between spaces
- **Relevance**: Bridge between Python and HTML, fast/instant
- **Strengths**:
  - Modern, edgy
  - Short (one syllable)
  - Gaming/tech associations
  - Very distinctive
- **Brand Feel**: Modern, fast, dynamic

#### 8. **Zephyr**
- **Meaning**: A gentle breeze; the west wind
- **Relevance**: Light, swift, smooth (like the framework's DX)
- **Strengths**:
  - Poetic and elegant
  - Suggests lightness and speed
  - Unique in dev tools space
  - Classical reference
- **Potential Issue**: Might be used by other projects
- **Brand Feel**: Elegant, swift, gentle

#### 9. **Stride**
- **Meaning**: A long step; confident progress
- **Relevance**: Moving forward, progress, momentum
- **Strengths**:
  - Action-oriented
  - Suggests efficiency and confidence
  - Developer-friendly
  - Memorable
- **Brand Feel**: Confident, progressive, efficient

#### 10. **Crisp**
- **Meaning**: Firm and fresh; clear and sharp
- **Relevance**: Clean code, sharp builds, fresh approach
- **Strengths**:
  - Describes the framework's philosophy perfectly
  - Modern and appealing
  - Easy to say and remember
- **Brand Feel**: Clean, modern, precise

---

## Evaluation Criteria

Each name evaluated on:

1. **Searchability**: Can you find it by name alone? (No "python" needed)
2. **Memorability**: Easy to remember and spell?
3. **Relevance**: Does it reflect the framework's purpose?
4. **Availability**: Likely to have domain/package names available?
5. **Brand Potential**: Does it sound professional and appealing?

---

## Top 3 Recommendations

### 🥇 **Loom**
**Best overall fit**: Weaving metaphor perfectly captures template composition, component integration, and the "web" nature. Short, memorable, distinctive.

### 🥈 **Forge**
**Best for power users**: Strong builder/maker connotations. Implies quality, precision, and the transformative process of building sites.

### 🥉 **Prism**
**Best for modern appeal**: Transformation and clarity align with compile-time optimization and the Python→HTML transformation. Modern and unique.

---

## Alternative Considerations

If the above are taken or don't resonate:
- **Beam**: Fast, structural, clear
- **Volt**: Energetic, powerful, tech-forward
- **Quill**: Elegant, content-focused, writerly

---

## Search Validation Recommendations

Before final decision, verify:
1. PyPI availability: `pip search <name>`
2. GitHub organization: `github.com/<name>`
3. Domain availability: `<name>.dev`, `<name>.io`
4. Existing projects: Google search for "<name> python framework"
5. Trademark check: USPTO database

---

*Analysis completed: 2025-12-27*
