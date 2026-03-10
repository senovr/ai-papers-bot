# Fast Relevance Filter Template

Quickly determine if this paper is relevant for practical LLM usage.

## Paper Information

**Title:** {{title}}

**Abstract:**
{{abstract}}

## Decision Criteria

Mark as RELEVANT if:
- ✅ Prompt engineering techniques
- ✅ Reasoning methods (CoT, ToT, etc.)
- ✅ RAG and retrieval methods
- ✅ LLM evaluation and benchmarks
- ✅ Practical LLM applications

Mark as NOT RELEVANT if:
- ❌ Model training/finetuning papers
- ❌ Purely theoretical research
- ❌ Infrastructure optimization only
- ❌ Computer vision only papers
- ❌ ML architecture improvements

## Output

Return ONLY: `true` or `false`

## Requirements

- Make quick decision based on title and abstract only
- Be conservative - when in doubt, return false
- Do not analyze deeply - just quick check
