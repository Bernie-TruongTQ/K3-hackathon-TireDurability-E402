# VLearn VisualRAG API

## Endpoints

- `POST /api/v1/index/upload`: upload PDF, image, Markdown or preprocessed JSON.
- `POST /api/v1/index/preprocessed`: index an OCR JSON by local path.
- `POST /api/v1/chat`: grounded response with route, sources and trace ID.
- `POST /api/v1/chat/stream`: SSE form of the same flow.
- `GET /health`: health check.

The default configuration uses:

- `local` lexical store, so the prototype boots without downloading embeddings;
- `lexical` reranker;
- an explicitly labelled `demo` generator.

For CP6, configure `VISUALRAG_LLM_PROVIDER=openai` with
`VISUALRAG_OPENAI_MODEL=gpt-4o-mini` and keep the trace
returned by the API. `demo` responses are clearly marked and do not satisfy the
real-AI requirement.

## Architecture

```text
upload
  -> DeepSeek-OCR or preprocessed Markdown/JSON
  -> page/region/bbox/image crop
  -> heading-aware text + visual chunks
  -> local or Chroma retrieval
  -> lexical or cross-encoder reranking
  -> conditional text/visual generation
  -> answer + source + trace
```

Models and cloud clients are loaded lazily. A missing cloud API key must not prevent
the API from starting in demo/local mode.

## Tests

```powershell
$env:PYTHONPATH=(Get-Location).Path
python -m unittest discover -s tests -v
```
