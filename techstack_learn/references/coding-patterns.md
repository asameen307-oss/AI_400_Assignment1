# Coding Patterns for Teaching

## Code Example Standards

### Structure Every Example:

```
1. CONTEXT: What problem this solves
2. CODE: Complete, runnable implementation
3. OUTPUT: Expected result
4. EXPLANATION: Line-by-line breakdown (if needed)
5. VARIATIONS: Alternative approaches (if relevant)
```

### Example Template:

```markdown
**Problem:** [What we're solving]

**Code:**
\`\`\`[language]
[Complete, runnable code]
\`\`\`

**Output:**
\`\`\`
[Expected output]
\`\`\`

**Key Points:**
- [Important concept 1]
- [Important concept 2]
```

---

## Bloom's Level Code Patterns

### Level 1 (Remember) - Syntax Focus

Show minimal, isolated syntax examples:

```markdown
**Variable declaration:**
\`\`\`javascript
const name = "Alice";     // constant (can't reassign)
let count = 0;            // variable (can reassign)
\`\`\`

**Function syntax:**
\`\`\`javascript
function greet(name) {
  return `Hello, ${name}!`;
}
\`\`\`
```

### Level 2 (Understand) - Concept Focus

Explain WHY with annotated examples:

```markdown
**Why use const vs let?**

\`\`\`javascript
// Use `const` for values that shouldn't change
const API_URL = "https://api.example.com";
// API_URL = "other";  // ERROR: Can't reassign

// Use `let` for values that need to change
let retryCount = 0;
retryCount = 1;  // OK: Can reassign
\`\`\`

**Key insight:** Default to `const`. Only use `let` when
you actually need reassignment. This prevents accidental
mutations and makes code easier to reason about.
```

### Level 3 (Apply) - Problem Focus

Give requirements, show implementation:

```markdown
**Task:** Create a function that validates email addresses.

**Requirements:**
1. Must contain exactly one @
2. Must have text before and after @
3. Return true/false

**Implementation:**
\`\`\`javascript
function isValidEmail(email) {
  const parts = email.split('@');
  
  // Must have exactly one @
  if (parts.length !== 2) return false;
  
  // Both parts must have content
  const [local, domain] = parts;
  if (!local || !domain) return false;
  
  // Domain must contain a dot
  if (!domain.includes('.')) return false;
  
  return true;
}

// Test cases
console.log(isValidEmail("user@example.com"));  // true
console.log(isValidEmail("invalid"));            // false
console.log(isValidEmail("no@domain"));          // false
\`\`\`
```

### Level 4 (Analyze) - Comparison Focus

Compare approaches with trade-offs:

```markdown
**Problem:** Fetch data from API

**Approach A: Callbacks**
\`\`\`javascript
function fetchUser(id, callback) {
  http.get(`/users/${id}`, (err, data) => {
    if (err) callback(err);
    else callback(null, data);
  });
}

// Usage: callback hell with nested operations
fetchUser(1, (err, user) => {
  fetchPosts(user.id, (err, posts) => {
    // deeply nested...
  });
});
\`\`\`

**Approach B: Promises**
\`\`\`javascript
async function fetchUser(id) {
  const response = await fetch(`/users/${id}`);
  return response.json();
}

// Usage: flat, readable
const user = await fetchUser(1);
const posts = await fetchPosts(user.id);
\`\`\`

**Trade-off Analysis:**

| Aspect | Callbacks | Promises/Async |
|--------|-----------|----------------|
| Readability | Poor (nesting) | Good (flat) |
| Error handling | Manual passing | try/catch |
| Compatibility | All Node versions | Node 8+ |
| Debugging | Harder stack traces | Clear traces |

**Recommendation:** Use async/await for new code.
```

### Level 5 (Evaluate) - Review Focus

Present code for critique:

```markdown
**Code Review Exercise:**

\`\`\`javascript
function getUsers() {
  let users = [];
  fetch('/api/users')
    .then(r => r.json())
    .then(data => users = data);
  return users;  // BUG: Returns empty array!
}
\`\`\`

**Issues to identify:**
1. Race condition: returns before fetch completes
2. No error handling
3. Mixing promise styles

**Improved version:**
\`\`\`javascript
async function getUsers() {
  try {
    const response = await fetch('/api/users');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch users:', error);
    throw error;
  }
}
\`\`\`
```

### Level 6 (Create) - Design Focus

Guide through architecture decisions:

```markdown
**Design Challenge:** Build a rate limiter

**Requirements:**
- Max 100 requests per minute per user
- Should work across multiple servers
- Must be fast (< 1ms overhead)

**Design Questions:**
1. Where to store count? (Memory vs Redis)
2. How to handle distributed systems?
3. What algorithm? (Fixed window, sliding window, token bucket)

**Skeleton:**
\`\`\`javascript
class RateLimiter {
  constructor(options) {
    // TODO: What configuration needed?
  }
  
  async isAllowed(userId) {
    // TODO: Design the algorithm
  }
}
\`\`\`

**Discussion points:**
- Trade-offs of each algorithm
- Consistency vs availability
- Handling clock skew
```

---

## Error Handling Patterns

### Always Show Error Handling

**Bad (teaching):**
```javascript
const data = await fetch(url).json();
```

**Good (teaching):**
```javascript
try {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  console.error('Fetch failed:', error);
  // Handle appropriately
}
```

---

## Progressive Complexity Pattern

Start simple, add complexity in stages:

**Stage 1: Basic**
```javascript
function add(a, b) {
  return a + b;
}
```

**Stage 2: Add validation**
```javascript
function add(a, b) {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new TypeError('Arguments must be numbers');
  }
  return a + b;
}
```

**Stage 3: Add features**
```javascript
function add(...numbers) {
  if (numbers.length === 0) {
    throw new Error('At least one number required');
  }
  return numbers.reduce((sum, n) => {
    if (typeof n !== 'number') {
      throw new TypeError(`Expected number, got ${typeof n}`);
    }
    return sum + n;
  }, 0);
}
```

---

## Documentation Search Patterns

When searching official docs:

```
# Find getting started
web_search: "[tech] getting started official"
web_search: "[tech] quickstart guide"

# Find API reference
web_search: "[tech] API reference documentation"
web_search: "[tech] [specific-method] docs"

# Find best practices
web_search: "[tech] best practices official"
web_search: "[tech] style guide"

# Find examples
web_search: "[tech] examples github official"
web_search: "[tech] tutorial site:official-domain.com"
```

Always verify:
1. Source is official (company blog, official docs, GitHub org)
2. Information is current (check date)
3. Version matches learner's version
