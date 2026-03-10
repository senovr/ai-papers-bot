# Paper Scoring Template

Evaluate this research paper for practical LLM usage.

## Paper Information

**Title:** {{title}}

**Abstract:**
{{abstract}}

{% if full_text %}
**Full Text (excerpt):**
{{full_text}}
{% endif %}

## Scoring Criteria

### Practical Score (0-40 points)
- Can users apply this in chat interfaces?
- Does it provide concrete techniques?
- Is it immediately useful?

Rate:
- 30-40: Highly practical, ready to use
- 20-29: Somewhat practical, needs adaptation
- 10-19: Limited practical value
- 0-9: Theaccessible or theoretical

### Novelty Score (0-30 points)
- Is this a new approach?
- Does it advance the field?
- Are results significantly better?

Rate:
- 20-30: Novel approach, significant improvement
- 10-19: Incremental improvement
- 0-9: Minor or no innovation

### Quality Score (0-30 points)
- Rigorous testing?
- Clear methodology?
- Reproducible results?

Rate:
- 20-30: Excellent rigor, clear results
- 10-19: Good testing, some gaps
- 0-9: Limited or unclear validation

## Output Format

Return JSON:
```json
{
  "rating": <total 0-100>,
  "practical_score": <0-40>,
  "novelty_score": <0-30>,
  "quality_score": <0-30>,
  "is_relevant": <true/false>,
  "summary": "<2-3 sentence summary>"
}
```

## Requirements

- Be objective and critical
- Focus on PRACTICAL value, not research contribution
- Return valid JSON
