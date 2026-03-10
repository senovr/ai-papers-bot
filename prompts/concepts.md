# Concept Extraction Template

Extract atomic, reusable concepts from this research paper.

## Paper Information

**Title:** {{title}}

**Abstract:**
{{abstract}}

{% if full_text %}
**Full Text (excerpt):**
{{full_text}}
{% endif %}

## Task

Extract 3-5 atomic concepts from this paper. Each concept should be:

1. **Self-contained** - Can be understood without reading the whole paper
2. **Actionable** - Reader can immediately apply it
3. **Specific** - Not generic advice

## Format

For each concept, provide:

## Проблема
<What specific problem does this solve?>

## Тезис
<Main claim or insight in 1-2 sentences>

## Метод
<How does it work in 2-3 sentences>

## Когда применять
<Specific use cases where this would help>

## Пример
<Concrete example of application>

## Requirements

- Extract 3-5 concepts
- Each concept must be specific and actionable
- Use Russian language
- Return as JSON array
