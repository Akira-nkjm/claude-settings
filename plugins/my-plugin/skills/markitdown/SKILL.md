---
name: markitdown
description: Convert files to clean Markdown using Microsoft's markitdown CLI — PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx), images, audio, HTML, CSV, JSON, XML, ZIP, EPub, and YouTube URLs. Use this whenever the user wants to turn a document, office file, spreadsheet, slide deck, image, or other non-text file into Markdown, extract its text/structure, or get its contents into a form an LLM can read. Trigger even if the user doesn't say "markitdown" — phrases like "convert this docx to markdown", "pull the text out of this PDF", "what's in this xlsx", or "ingest this file" all apply. For studying or page-by-page summarizing a PDF, prefer the /read-pdf command instead.
origin: community
---

# markitdown

[markitdown](https://github.com/microsoft/markitdown) is Microsoft's utility for converting many file formats into Markdown that's optimized for LLMs and text pipelines. It preserves structure (headings, lists, tables, links) rather than just dumping raw text, which is what makes its output useful as context.

## When to use this skill

Reach for markitdown whenever you need the *contents* of a non-Markdown file as Markdown:

- Office documents — `.docx`, `.xlsx`, `.pptx`
- PDFs (faithful structural extraction, not summarization)
- Images and audio (EXIF/OCR/transcription where supported)
- Web/data formats — HTML, CSV, JSON, XML
- Archives and books — ZIP (recurses into contents), EPub
- YouTube URLs (transcript + metadata)

### markitdown vs. the `/read-pdf` command

These look similar for PDFs but do different jobs — pick deliberately:

| | **markitdown** (this skill) | **`/read-pdf`** command |
|---|---|---|
| What it does | Faithful 1:1 structural conversion to Markdown | Page-by-page **LLM summarization** + knowledge extraction |
| Output | One Markdown file mirroring the source | Summaries written to `book_analysis/` |
| Use when | You want the actual content to read, quote, diff, or feed downstream | You want to *study* or *digest* a long PDF/book |
| Scope | Many formats | PDF only |

If the user wants the real text/tables out of a file → markitdown. If they want it *explained or summarized* → `/read-pdf`.

## How to run it

This environment has **no `pip`, but has `uv`**, so run markitdown through `uvx`. The `[all]` extra pulls in every optional format dependency (PDF, docx, xlsx, audio, …) so all the formats above work:

```bash
uvx 'markitdown[all]' <input-file> -o <output-file>.md
```

The first invocation downloads dependencies; `uv` caches them, so later runs are fast. (If `uvx` is unavailable, `uv tool install 'markitdown[all]'` makes a persistent `markitdown` on PATH — but prefer `uvx` so nothing is installed globally without reason.)

### Core patterns

**Single file → Markdown file** (the common case):

```bash
uvx 'markitdown[all]' report.docx -o report.md
```

**Write to stdout** (to inspect, pipe, or capture inline) — omit `-o`:

```bash
uvx 'markitdown[all]' data.xlsx
```

**From stdin** — pass an extension hint with `-x` so markitdown knows how to parse it:

```bash
cat slides.pptx | uvx 'markitdown[all]' -x pptx
```

**Batch convert a directory** — loop and mirror each name to `.md`:

```bash
for f in docs/*.pdf; do
  uvx 'markitdown[all]' "$f" -o "${f%.pdf}.md"
done
```

## Workflow

1. **Confirm the input.** Check the file exists and note its type. If the user named a folder or a glob, plan a batch loop.
2. **Decide the destination.** Default to a sibling `.md` file (`report.docx` → `report.md`) unless the user wants stdout (e.g. they just want to see the contents) or a specific path.
3. **Run** the appropriate pattern above. Let the first run download deps — don't abort on the download lines.
4. **Verify** the output: open the produced `.md`, confirm it has real content (headings/tables/text), and surface anything notable — empty output, an unsupported file, or obvious extraction gaps (e.g. a scanned PDF with no OCR text).
5. **Report** the output path and a short note on what was produced. Don't paste a huge file back into the conversation unless the user asked to see it; point them to the file.

## Options worth knowing

- `-o, --output <file>` — write to a file instead of stdout.
- `-x, --extension <ext>` — extension hint, needed when reading from stdin.
- `-m, --mime-type <type>` — MIME hint when the extension is missing/ambiguous.
- `-p, --use-plugins` — enable installed 3rd-party converter plugins (`--list-plugins` to see them).
- `--keep-data-uris` — keep base64 image data URIs inline (default truncates them).
- `-d, --use-docintel -e <endpoint>` — use **Azure Document Intelligence** for extraction (better for scanned/complex PDFs). Requires an endpoint; the user must supply it. Never hardcode endpoints or keys — pass them via the command/environment.

## Notes & failure modes

- **Scanned/image-only PDFs** yield little or no text from offline conversion. If the user needs those, suggest Azure Document Intelligence (`-d -e <endpoint>`) or an OCR step — don't silently return an empty file.
- **Large spreadsheets/decks** can produce very long Markdown. Write to a file rather than stdout, and summarize what you saw rather than echoing it all.
- **Faithfulness, not summarization** — markitdown does not condense. If the user actually wanted a summary, convert first, then summarize the Markdown (or use `/read-pdf` for PDFs).
- **Secrets** — when using Azure options, keep endpoints/keys out of committed files and out of chat output.
