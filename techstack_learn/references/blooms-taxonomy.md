# Bloom's Taxonomy for Tech Learning

## Overview

Bloom's Taxonomy is a hierarchical model of cognitive skills. For tech learning, each level maps to specific competencies and project types.

## Level 1: Remember (Foundation)

**Cognitive Goal:** Recall facts, terms, basic concepts

**Tech Learning Activities:**
- Memorize syntax and keywords
- Learn CLI commands
- Understand file structure conventions
- Recognize error message patterns
- Know configuration file locations

**Assessment Questions:**
- What command does X?
- What is the syntax for Y?
- Where is the config file located?

**Example Tasks:**
```
- List 5 common CLI commands for [technology]
- Write the basic syntax for a [function/class/component]
- Identify the file extension used by [technology]
```

**Project Type:** Setup & First Run
- Install the technology
- Run "hello world"
- Verify installation works

---

## Level 2: Understand (Comprehension)

**Cognitive Goal:** Explain ideas, interpret meaning

**Tech Learning Activities:**
- Explain how components interact
- Describe the request/response cycle
- Interpret error messages
- Understand documentation examples
- Grasp design patterns rationale

**Assessment Questions:**
- Why does this pattern exist?
- What happens when X calls Y?
- How does the data flow?

**Example Tasks:**
```
- Explain in your own words how [feature] works
- Describe the lifecycle of a [component/request/process]
- Interpret this error message and explain the cause
```

**Project Type:** Guided Tutorial
- Follow official getting started guide
- Modify examples to understand effects
- Document learnings in own words

---

## Level 3: Apply (Implementation)

**Cognitive Goal:** Use knowledge in new situations

**Tech Learning Activities:**
- Build features from requirements
- Implement common patterns
- Debug issues independently
- Use documentation to solve problems
- Write code without copying examples

**Assessment Questions:**
- How would you implement X feature?
- Given this requirement, what approach would you use?
- Can you build Y without looking at examples?

**Example Tasks:**
```
- Build a [specific feature] using [technology]
- Implement CRUD operations for [entity]
- Create a [component] that handles [use case]
```

**Project Type:** Mini Application
- Build a complete small app (todo list, calculator, API)
- Handle common edge cases
- Implement user-facing features

---

## Level 4: Analyze (Architecture)

**Cognitive Goal:** Draw connections, examine structure

**Tech Learning Activities:**
- Compare architectural approaches
- Identify performance bottlenecks
- Analyze code for anti-patterns
- Examine trade-offs in design decisions
- Break complex systems into components

**Assessment Questions:**
- What are the trade-offs between A and B?
- Why might this code cause performance issues?
- How would you structure this system?

**Example Tasks:**
```
- Compare [pattern A] vs [pattern B] for [use case]
- Analyze this codebase and identify improvement areas
- Design the architecture for [complex feature]
```

**Project Type:** Integration Project
- Connect multiple services/systems
- Design database schema
- Implement authentication/authorization
- Handle external API integrations

---

## Level 5: Evaluate (Judgment)

**Cognitive Goal:** Make decisions, justify choices

**Tech Learning Activities:**
- Conduct code reviews
- Choose between technologies/libraries
- Assess security vulnerabilities
- Evaluate scalability of solutions
- Recommend optimizations

**Assessment Questions:**
- Is this the best approach? Why?
- What would you change in this code?
- How would this scale to 1M users?

**Example Tasks:**
```
- Review this PR and provide feedback
- Evaluate [library A] vs [library B] for our use case
- Assess the security of this implementation
```

**Project Type:** Production Hardening
- Add comprehensive testing
- Implement monitoring/logging
- Configure CI/CD pipeline
- Security audit and fixes
- Performance optimization

---

## Level 6: Create (Mastery)

**Cognitive Goal:** Produce original work

**Tech Learning Activities:**
- Design novel solutions
- Create reusable libraries/tools
- Architect production systems
- Mentor others
- Contribute to open source

**Assessment Questions:**
- How would you design X from scratch?
- What original solution solves this problem?
- How would you teach this to someone else?

**Example Tasks:**
```
- Design and build a [novel application]
- Create a reusable [library/component] for [problem]
- Write documentation/tutorials for others
```

**Project Type:** Production System
- Full production deployment
- Scalability planning
- Disaster recovery
- Team documentation
- Maintenance procedures

---

## Level Transitions

### Signs Ready for Next Level:

| Current | Ready When... |
|---------|---------------|
| Remember → Understand | Can recall without reference |
| Understand → Apply | Can explain concepts clearly |
| Apply → Analyze | Can build standard features independently |
| Analyze → Evaluate | Can identify trade-offs and patterns |
| Evaluate → Create | Can make and justify technical decisions |

### When to Step Back:

- Struggling with implementation → Review understanding
- Making fundamental errors → Revisit remember/understand
- Analysis paralysis → Practice more application
- Poor decisions → Strengthen analysis skills

## Time Allocation Guidelines

For a new technology (assuming ~20 hours total):

| Level | % Time | Hours | Focus |
|-------|--------|-------|-------|
| Remember | 10% | 2h | Setup, syntax, basics |
| Understand | 15% | 3h | How it works, tutorials |
| Apply | 35% | 7h | Build projects |
| Analyze | 20% | 4h | Architecture, integration |
| Evaluate | 15% | 3h | Testing, optimization |
| Create | 5% | 1h | Original solutions |

Note: Times shift based on complexity. Kubernetes needs more Remember/Understand; React needs more Apply.
