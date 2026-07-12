# Defense notes — Imagining the Target
Asma Hoseinpour Siouki · MSc Data Science · University of Padova · July 2026
**20-minute slot, script paced for ≈15:00** — leaves ~5 min of buffer for
questions, transitions, and running over. 22 talk slides + thank-you (23) +
8 backups (24–31). Slides 19–20 are the flex valve: if behind, show only the
success case. During Q&A: type a backup slide's number + Enter to jump to it.

## 1. Title | 0:15 | cum 0:15
Good morning everyone, and thank you for being here.

## 2. Composed Image Retrieval | 0:55 | cum 1:10
Imagine you see a chair online that you really like, and you want to find a
dining set that includes that exact chair together with a table.

Searching with the image alone returns the same chair or similar chairs — but
not as a dining set. Searching with text alone, "a dining table and chairs",
returns many sets — but not your specific chair.

You need both: the image identifies the chair, the text describes the context
you want to find it in.

This is composed image retrieval, the task of my thesis. The query is a
reference image plus a modification text, and the goal is to retrieve images
that preserve the reference object while satisfying the modification.

> Naming note: these are the two parts of the query, so from here on I call
> them the **query image** and the **query text**.

## 3. Instance-level composed retrieval | 0:40 | cum 1:50
My thesis focuses on the instance-level version of this task.

In category-level retrieval, any object of the correct class can be correct —
any chair around a table would do. At the instance level, that is not enough:
the system must retrieve the exact same chair shown in the query image, while
also satisfying the query text.

So the challenge is to detect that one specific instance among many
look-alikes, even when its context, viewpoint, or visual domain changes.

## 4. The i-CIR benchmark | 0:50 | cum 2:40
We use the i-CIR benchmark, designed specifically for this task.

Each object instance has several composed queries — query image plus query
text. Importantly, each query can have multiple correct targets: every
database image showing the same object under the requested modification. So
evaluation is about ranking all of them highly, not finding one right answer.

Each instance also comes with curated hard negatives: images that are visually
similar but fail the modification, or satisfy the modification but show a
different instance. This prevents the system from succeeding on one modality
alone.

## 5. The i-CIR benchmark — scale | 0:25 | cum 3:05
On scale: about 752 thousand database images, 202 instances, and 1,883
composed queries — a median of six per instance.

The histograms show the distributions, and confirm that many queries have more
than one ground truth.

## 6. Problem formulation — a zero-shot setting | 0:45 | cum 3:50
Formally: given a query image and a query text, retrieve the database images
relevant to both.

We adopt a zero-shot setting — no training or fine-tuning on i-CIR. Supervised
CIR needs labelled triplets, and at the instance level every new object would
require new annotation. A model trained on fixed instances also does not
necessarily generalize to unseen ones — and new objects appear constantly.
So supervision would hurt both scalability and generalizability.

With frozen pre-trained models, the system applies directly to unseen
instances.

## 7. Retrieval, ranking, and the metric | 0:45 | cum 4:35
How retrieval works: the system scores every database image and sorts them
from most to least relevant. Evaluation checks where the correct targets land
in this ranking.

Per query we use Average Precision — high when the correct images are near the
top. Averaging AP over all queries gives mean Average Precision.

But instances have different numbers of queries, so a direct average lets
large instances dominate. Our main metric is therefore macro-mAP: average
within each instance first, then across instances — every instance counts
equally.

## 8. Vision–language models: CLIP and SigLIP | 0:55 | cum 5:30
To represent images and text we use frozen vision–language models: CLIP and
SigLIP.

Both are dual-encoders: an image encoder and a text encoder mapping into the
same embedding space, where similarity is cosine similarity. We use them
completely frozen — we only extract embeddings.

They differ in training. CLIP compares all image–text pairs within a batch
through a softmax contrastive objective. SigLIP classifies each pair
independently with a sigmoid loss — no global softmax, which scales better to
large batches.

We compare both families to check that our method does not depend on one
particular model.

## 9. The baseline: BASIC | 0:55 | cum 6:25
Our baseline is BASIC, the zero-shot method introduced with the benchmark by
Psomas and colleagues in 2025.

BASIC processes the two parts of the query separately: the query image goes
through the visual encoder, the query text through the text encoder.

For every database image it computes two similarities — visual, to the query
image, and textual, to the query text — and multiplies them. The
multiplication acts like a soft logical AND: a high score requires matching
both parts.

BASIC also includes further processing steps — centering, normalization,
contextualization — which I will cover shortly.

## 10. Limitation of the baseline — our proposal | 0:55 | cum 7:20
The key limitation: the query image and query text are never processed
jointly. Each branch sees only half of the query, so the complete composed
query is never explicitly represented.

Our proposal is a third branch. This is the full pipeline: as before, the
image and text branches — and in addition, both query parts go together to a
multimodal language model, which imagines the target and writes a caption of
it. The caption is embedded by the same frozen text encoder and becomes a
third similarity score.

So every database image now gets three scores — image, text, and caption —
which we combine.

## 11. The captioner: InternVL 3.5-8B | 0:40 | cum 8:00
For caption generation we use InternVL 3.5, eight billion parameters, frozen —
an open-source multimodal LLM that processes image and text jointly, at a
practical balance of quality and cost. No fine-tuning anywhere.

In the chair example it sees the chair image and "placed around a table", and
writes: "White metallic chair with scrolled armrests placed around a table."

Notice this single caption carries both the visual identity and the requested
context — exactly the signal the two separate branches cannot represent.

## 12. Designing the instruction | 0:35 | cum 8:35
Caption quality depends strongly on the instruction given to the model. I
tested more than twenty instructions, varying the detail level, examples,
constraint order, and restrictions against irrelevant information.

From these I selected five complementary strategies. Each describes the
imagined target from a different perspective, and we average their caption
embeddings.

> What each strategy does → backup 31.

## 13. Effect of the caption branch | 0:45 | cum 9:20
A single caption improves macro-mAP by about 5.9 points, from 17.95 to 23.83 —
it captures compositional information the two branches miss.

Averaging five captions from the five strategies goes further: it suppresses
prompt-specific wording and keeps what is consistent. That reaches 25.41 —
about 7.5 points over the image–text baseline.

> From here on, all results use CLIP ViT-L/14 unless stated otherwise.

## 14. Combining the three scores | 0:50 | cum 10:10
How are the three scores combined?

First, min-based normalization puts the branches on comparable scales, and
negative residuals are clamped to zero — no positive evidence.

Then the scores are multiplied — a soft logical AND across all three branches.

On top, a Harris-inspired penalty, from the Harris corner detector: a
candidate must not win on one branch alone — the exact chair not around a
table, or tables with the wrong chair, are both suppressed. The penalty is
weighted by a hyperparameter lambda.

The surface on the right shows it: the score is high only when both arguments
are large simultaneously.

## 15. Two refinements: centering and contextualisation | 0:50 | cum 11:00
Two further refinements — one on the embeddings, one on the raw query text.

Centering: embedding spaces share a large common component — generic patterns
rather than distinctive information. We subtract a per-modality mean computed
on a separate corpus and re-normalise, isolating the semantic content.

Contextualisation acts on the raw query text — a query-side step, not score
post-processing. The text encoder is trained on full captions, so a bare
fragment like "sculpture" is out-of-distribution. We enrich the query with
corpus terms before and after — "sculpture dog" — then embed and average the
variants for a more robust text feature.

## 16. Adding the steps on top of each other | 0:30 | cum 11:30
Adding each step cumulatively — baseline in blue, our caption pipeline in red,
on CLIP-L.

The caption pipeline stays above the baseline along the entire ladder.
Centering gives the baseline its big jump; contextualisation gives the largest
single gain.

> If asked why it stops here: projection and query expansion do not help once
> the caption branch is present → backup 24.

## 17. Does it transfer? Four frozen backbones | 0:45 | cum 12:15
We evaluate four frozen backbones: CLIP ViT-L — the standard in zero-shot CIR,
keeping our numbers comparable — the larger CLIP ViT-H, SigLIP ViT-L, and the
recent SigLIP2, the best-aligned of the four.

The caption branch improves every single one. The largest jump is SigLIP-L,
where macro-mAP roughly doubles, from 21 to 43. SigLIP2 is the strongest base
model.

So the contribution does not depend on one particular vision–language model.

## 18. Our best overall system | 0:40 | cum 12:55
The final system: SigLIP2, the caption branch with five averaged captions, and
centering plus contextualisation. Everything frozen.

It reaches 61.98 macro-mAP. Beyond mAP: the correct target is ranked first for
71% of queries and appears in the top ten for 95%. Recall at one hundred is
94%.

That high recall matters — I will come back to it in the future work.

> The SigLIP2 ladder behind 61.98 → backup 25.

## 19. Qualitative example — success | 0:25 | cum 13:20 (flex)
A success: Homer Simpson, "as a plushie".

The plain product gets 4% AP — generic plushies: SpongeBob, minions. BASIC
reaches 33%. The caption — "Homer Simpson as a plushie, same facial features"
— pins the retrieval to actual Homer plushies: 88%. The caption keeps the
identity while honouring the modification.

## 20. Qualitative example — failure | 0:25 | cum 13:45 (flex)
An honest failure: gold metal eyeglasses, "worn by a dog".

All three methods score near zero. The single ground truth is a dog actually
wearing these glasses; every method returns glasses on tables instead. When
the modification demands a drastic, rarely-photographed context, the image
branch dominates and the target never gets near the top.

## 21. Limitations and future work | 0:40 | cum 14:25
Limitations: caption generation costs about fifteen seconds per query and
dominates inference; results depend on prompt design — averaging mitigates but
does not remove it; and the fixed product cannot re-weight the branches.

Future work: a more efficient captioner would cut the main cost. A learned
fusion of the three scores could trade the zero-shot constraint for accuracy.
And since recall is already high, a second-stage reranker is promising — most
remaining error is in the ordering of candidates already retrieved, and a
caption-conditioned reranker keeps the modification in the loop. Finally, the
caption-as-third-modality idea is benchmark-agnostic and could be tested
beyond i-CIR.

## 22. Conclusions | 0:30 | cum 14:55
Two conclusions.

The caption is the single most effective component — it improves every
backbone on the full dataset.

And SigLIP2 is the strongest backbone for the pipeline, reaching the
thesis-best 61.98 macro-mAP, fully zero-shot.

> If pushed: the caption alone beats the plain product on CLIP-L → backup 26;
> centering and the caption stack → backup 27.

## 23. Thank you | — | —
Thank you. I am happy to take questions.

## Q&A map | — | —
Full CLIP-L ablation, every rung (incl. projection and query expansion) →
**backup 24**. SigLIP2 ladder (produces 61.98) → **backup 25**. Component
contributions — image-only, text-only, caption-only, product, triplet; the
caption alone beats the product → **backup 26**. Centering + caption are
complementary → **backup 27**. "The paper reports 34.35 for BASIC" →
**backup 28** (our reproduction gives 32.48; gap is in the image branch, from
re-extracted features in a newer software stack; both methods share the same
environment, so comparisons hold). Latency breakdown → **backup 29**. Five
instruction strategies, sample captions → **backup 30**; what each does →
**backup 31**.

Metric on slide 7; full pipeline figure on slide 10; fusion detail on
slide 14; backbone table on slide 17.
