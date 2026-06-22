# Thesis draft — what you need to check / add manually

All six chapters now have a **full v1 prose draft**. The numbers in the Results
tables come straight from `thesis_cir/docs/*` and the reranking `metrics.csv`
files. This file lists everything that still needs a **human** — figures to
make, facts to verify, and decisions to take. Every item is also marked inline
in the `.tex` with a `% HIGHLIGHT:` comment, so you can `grep -rn "HIGHLIGHT"
chapters/` to jump to them.

---

## A. Figures to create (none exist yet — all captions are in place)

| # | File to add (`figures/`) | Chapter / label | What it should show |
|---|---|---|---|
| 1 | `teaser.png` *(optional)* | Intro `fig:teaser` | One query (ref img + text) → caption → top-1 result. Page-1 hook. |
| 2 | `clip.png` *(optional)* | Background `fig:clip` | CLIP dual-encoder diagram. |
| 3 | `pipeline_overview.png` **(important)** | Method `fig:pipeline` | The 3 branches → 3 scores → clamp-product → ranking. The key diagram. |
| 4 | `caption_example.png` **(important)** | Method `fig:caption_example` | Ref image + modification → generated caption. Pull a clean example from `answers_with_final_caption_8b_split6_clean.csv`. |
| 5 | `qualitative_examples.png` **(important)** | Results `fig:qualitative` | 2–3 successes + 1 failure: ref+text+caption+top-k (mark ground truth). |
| 6 | bar chart *(optional)* | Results §5.4 | BASIC vs Ours vs Ours+center per backbone — makes the headline visual. |

The `\includegraphics` lines are commented out; uncomment once the files exist.
Until then the captions float without an image (LaTeX will still compile).

## B. Facts / numbers to verify before final submission

1. **Dataset counts** — 1,883 queries / 752,092 DB (full); 400 / 143,769 (20% subset). Confirm against the i-CIR data card. (Intro, Method §4.1, Results §5.1)
2. **Embedding dimensions** in `tab:backbones` (Method §4.4): I put CLIP-L 768, CLIP-H 1024, SigLIP-L 1024, SigLIP2 1536, Qwen3-VL-Emb `—`. **Verify each** against the model cards / your configs.
3. **InternVL-8B generation settings** (Method §4.8): temperature / max-new-tokens / number of tiles are left blank. The 4B REPL used temp 0.7 / 12 tiles / 512 tokens — **confirm the 8B batch run used the same** and fill in.
4. **Macro vs micro mAP definition** (Method §4.2): I wrote macro = average per instance, micro = average per query. Confirm this is exactly how the i-CIR paper / your eval code defines it.
5. **Trapezoidal AP formula** (Method §4.2, eq:ap): matches the Oxford-style / your `compute_ap`. Sanity-check the equation renders the integration you intend.
6. **Reranking table** (`tab:res_rerank`, Results §5.6): numbers are macro/micro-mAP@100 read from `runs/reranking_experiments/clip_l_dino_top{100,200}/*/rerank/metrics.csv`. Note the top-100 DINOv3 case **ties** the baseline (18.73) — reported as "no improvement", not a win. Decide if you'd rather report @200 cutoff instead of @100.
7. **Hardware/library versions** (Method §4.8): GPUs (A5000/A100), CUDA, and torch / openclip / transformers versions are left as a HIGHLIGHT — fill the exact ones for reproducibility.
8. **References** (`references.bib`): I filled real entries, but several authors are `and others` and a few arXiv IDs/venues are best-guess. **Double-check** psomas2025icir (2510.25387), tschannen2025siglip2 (2502.14786), wang2025internvl35 (2508.18265), simeoni2025dinov3 (2508.10104), and the song2024cirsurvey entry (the survey you were given — fill in real authors/title/venue).

## C. Decisions for you to make

1. **Verbatim prompts as an appendix?** Method §4.6 (`tab:instructions`) references `Appendix~\ref{...}` for the 9 full prompts. Either create an appendix from `caption_files_Amin/prompts/internvl_instructions.md` or remove that sentence. (The `\ref{...}` is a deliberate placeholder that will throw an undefined-reference warning until resolved.)
2. **Notation**: I switched the shared macros to the i-CIR style you chose — `\qv` (q^v), `\qt` (q^t), `\DB` (X), `\encv`/`\enct` (φ^v/φ^t), plus `\sv \st \sc \qc \clamp`. Legacy `\Iq \tq` etc. still alias to the new ones so nothing breaks. Confirm you're happy with `q^v / q^t` everywhere.
3. **Qwen line**: currently mentioned only as a weak baseline (Method §4.4) and exploratory (not in results). Keep it minimal or cut entirely — your call.
4. **Page budget**: drafts are written to roughly hit your ratios (Intro 8 / Background 13 / Related 10 / Method 18 / Results 22 / Conclusion 6). After you add figures, re-check the balance.

## D. Still empty / template-only (not chapters)

- `frontmatter/` — abstract, title page personalization, acknowledgments still need your text.
- Background/Related still cite a few things lightly; add depth if you want the page count higher.

---

### How the numbers map to sources (for your own audit)
- Main + centering + full metrics tables → `docs/full_centering_and_metrics.md`, `docs/full_basic_vs_triplet_table.md`, `docs/centering_global_vs_laion.csv`.
- Backbone duplet table, component ablation, instruction ablation → `docs/meeting_2026-06-18_results.md`.
- Reranking table → `runs/reranking_experiments/.../metrics.csv` (read directly).
