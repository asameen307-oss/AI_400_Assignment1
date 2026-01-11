---
name: blooms-techstack-learner
description: Structured learning system for ANY computer science tech stack using Bloom's Taxonomy. Use when user wants to learn a programming language, framework, library, tool, or technology stack systematically - from hello world basics to professional production deployment and maintenance. Triggers on requests like "teach me [technology]", "learn [framework]", "master [language]", "understand [tool]", or when user wants structured learning paths for technologies like React, Python, Docker, Kubernetes, AWS, databases, etc. Always fetches official documentation first - never relies on assumed knowledge.
---

# Bloom's TechStack Learner

Systematic framework for learning any computer science technology using Bloom's Taxonomy cognitive levels, progressing from hello world to production deployment.

## Core Workflow

### Step 1: Identify the Tech Stack

Extract the specific technology/technologies the user wants to learn:
- Programming languages (Python, Rust, Go, JavaScript, etc.)
- Frameworks (React, Django, FastAPI, Spring Boot, etc.)
- Tools (Docker, Kubernetes, Git, etc.)
- Cloud platforms (AWS, GCP, Azure)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Any combination of the above

### Step 2: Research Official Documentation

**CRITICAL: Always search for and fetch official documentation before teaching anything.**

1. Use `web_search` to find official docs:
   ```
   web_search: "[technology] official documentation"
   web_search: "[technology] getting started guide"
   web_search: "[technology] tutorial site:official-domain"
   ```

2. Use `web_fetch` to retrieve documentation content:
   - Getting started guides
   - Installation instructions
   - API references
   - Best practices
   - Official tutorials

3. Document sources used - cite official docs in responses.

### Step 3: Assess Current Level

Determine user's starting point:
- **Absolute beginner**: No prior experience
- **Familiar**: Basic exposure, needs structured learning
- **Intermediate**: Working knowledge, wants depth
- **Advanced**: Production experience, seeks mastery

### Step 4: Apply Bloom's Taxonomy Learning Path

For detailed level descriptions, see [references/blooms-taxonomy.md](references/blooms-taxonomy.md).

**Quick Reference - 6 Cognitive Levels:**

| Level | Verb | Learning Goal |
|-------|------|---------------|
| 1. Remember | Recall | Terminology, syntax, basic commands |
| 2. Understand | Explain | How things work, why patterns exist |
| 3. Apply | Use | Build projects, solve problems |
| 4. Analyze | Compare | Architecture decisions, trade-offs |
| 5. Evaluate | Judge | Best practices, code reviews, optimization |
| 6. Create | Design | Original solutions, production systems |

### Step 5: Execute Project Progression

For detailed progression phases, see [references/project-progression.md](references/project-progression.md).

**Quick Reference - 7 Project Phases:**

1. **Hello World** → Basic setup and first output
2. **Core Concepts** → Fundamental features
3. **Mini Project** → Combine concepts into working app
4. **Integration** → Connect with other systems
5. **Testing & Quality** → Automated testing, CI/CD
6. **Production Deployment** → Deploy to real environment
7. **Maintenance & Scale** → Monitor, optimize, iterate

## Coding Assistance Protocol

When helping with code:

1. **Always verify against official docs** - search before coding
2. **Show complete, runnable examples** - no pseudocode fragments
3. **Explain the "why"** - connect to Bloom's level
4. **Progressive complexity** - start simple, add layers
5. **Include error handling** - production-ready from the start

For coding patterns and templates, see [references/coding-patterns.md](references/coding-patterns.md).

## Session Management

### Starting a New Tech Stack

```
1. "What technology do you want to learn?"
2. Search official documentation
3. "What's your current experience level?"
4. Begin at appropriate Bloom's level
5. Propose first project milestone
```

### Continuing Learning

```
1. Review current Bloom's level and project phase
2. Assess recent progress
3. Identify gaps or struggles
4. Adjust pace/complexity
5. Propose next milestone
```

### Handling Questions Mid-Learning

```
1. Answer the immediate question
2. Connect answer to current Bloom's level
3. Note if question suggests readiness for next level
4. Return to structured progression
```

## Example Learning Plan Generation

When user requests a learning plan, produce structured output:

```markdown
# [Technology] Learning Path

## Current Assessment
- Starting level: [Beginner/Intermediate/Advanced]
- Target goal: [User's stated goal]
- Estimated timeline: [Realistic estimate]

## Phase 1: [Name] (Bloom's Level 1-2: Remember & Understand)
- [ ] Project: [Specific deliverable]
- [ ] Key concepts: [List]
- [ ] Official resources: [Links]

## Phase 2: [Name] (Bloom's Level 3: Apply)
- [ ] Project: [Specific deliverable]
- [ ] Skills practiced: [List]

[Continue through phases...]

## Milestone Checkpoints
- [ ] Checkpoint 1: [Criteria]
- [ ] Checkpoint 2: [Criteria]
```

## Quality Principles

1. **Documentation-first**: Never assume - always verify with official sources
2. **Practical focus**: Every concept tied to a buildable project
3. **Progressive disclosure**: Reveal complexity as comprehension grows
4. **Production mindset**: Build deployment-ready from Phase 4 onwards
5. **Active learning**: User writes code, not just reads explanations
