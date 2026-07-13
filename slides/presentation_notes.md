# Defense notes — Imagining the Target
Asma Hoseinpour Siouki · MSc Data Science · University of Padova · July 2026
**20-minute slot, script paced for ≈14:15** — leaves generous buffer for
questions, transitions, and running over. 22 talk slides + thank-you (23) +
9 backups (24–32). Slides 19–20 are the flex valve: if behind, show only the
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

## 6. A zero-shot setting | 0:40 | cum 3:45
We adopt a zero-shot setting — no training or fine-tuning on i-CIR.

Supervised CIR needs labelled triplets, and at the instance level every new
object would require new annotation. A model trained on fixed instances also
does not necessarily generalize to unseen ones — and new objects appear
constantly. So supervision would hurt both scalability and generalizability.

With frozen pre-trained models, the system applies directly to unseen
instances.

## 7. Problem formulation | 0:20 | cum 4:05
Formally: given a query image and a query text, retrieve the database images
relevant to both.

The system scores every database image and sorts them from most to least
relevant. This ranking is the output — evaluation checks where the correct
targets land in it.

## 8. Evaluation metric | 0:35 | cum 4:40
Per query we use Average Precision, built on Precision-at-k — the fraction of
the top-k results that are correct. AP is high when the correct images are
near the top.

Averaging AP over all queries gives mean Average Precision.

But instances have different numbers of queries, so a direct average lets
large instances dominate. Our main metric is therefore macro-mAP: average
within each instance first, then across instances — every instance counts
equally.

## 9. Vision–language models: CLIP and SigLIP | 0:55 | cum 5:35
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

## 10. The baseline: BASIC | 1:00 | cum 6:35
Our baseline is BASIC, the zero-shot method introduced with the benchmark by
Psomas and colleagues in 2025.

BASIC processes the two parts of the query separately: the query image goes
through the visual encoder, the query text through the text encoder.

For every database image it computes two similarities — visual, to the query
image, and textual, to the query text — and multiplies them. The
multiplication acts like a soft logical AND: a high score requires matching
both parts.

BASIC uses CLIP ViT-L/14 as its main backbone — the standard in the zero-shot
CIR literature — and we adopt the same one, so our results are directly
comparable.

BASIC also includes further processing steps — centering, normalization,
contextualization — which I will cover shortly.

## 11. Limitation of the baseline — our proposal | 0:55 | cum 7:30
The key limitation: the query image and query text are never processed
jointly. Each branch sees only half of the query, so the complete composed
query is never explicitly represented.

Our proposal is a third branch. This is the full pipeline: as before, the
image and text branches — and in addition, both query parts go together to a
multimodal language model, which imagines the target and writes a caption of
it. The caption is embedded by the same frozen text encoder and becomes a
third similarity score.

The three scores are normalized and multiplied — a soft logical AND across the
three branches, as the figure shows.

> Fusion formulas and the Harris penalty → backup 24.

## 12. The captioner: InternVL 3.5-8B | 0:40 | cum 8:10
For caption generation we use InternVL 3.5, eight billion parameters, frozen —
an open-source multimodal LLM that processes image and text jointly, at a
practical balance of quality and cost. No fine-tuning anywhere.

In the chair example it sees the chair image and "placed around a table", and
writes: "White metallic chair with scrolled armrests placed around a table."

Notice this single caption carries both the visual identity and the requested
context — exactly the signal the two separate branches cannot represent.

## 13. Designing the instruction | 0:35 | cum 8:45
Caption quality depends strongly on the instruction given to the model. I
tested more than twenty instructions, varying the detail level, examples,
constraint order, and restrictions against irrelevant information.

From these I selected five complementary strategies. Each describes the
imagined target from a different perspective, and we average their caption
embeddings.

> What each strategy does → backup 32.

## 14. Effect of the caption branch | 0:45 | cum 9:30
A single caption improves macro-mAP by about 5.9 points, from 17.95 to 23.83 —
it captures compositional information the two branches miss.

Averaging five captions from the five strategies goes further: it suppresses
prompt-specific wording and keeps what is consistent. That reaches 25.41 —
about 7.5 points over the image–text baseline.

> Reminder on the slide: all results from here on are CLIP ViT-L/14 unless
> stated otherwise.

## 15. Two refinements: centering and contextualisation | 0:50 | cum 10:20
Two further refinements — one on the embeddings, one on the raw query text.

Centering: embedding spaces share a large common component — generic patterns
rather than distinctive information. We subtract a per-modality mean computed
on a separate corpus and re-normalise, isolating the semantic content.

Contextualisation acts on the raw query text — a query-side step, not score
post-processing. The text encoder is trained on full captions, so a bare
fragment like "sculpture" is out-of-distribution. We enrich the query with
corpus terms before and after — "sculpture dog" — then embed and average the
variants for a more robust text feature.

## 16. Adding the steps on top of each other | 0:30 | cum 10:50
Adding each step cumulatively — baseline in blue, our caption pipeline in red,
on CLIP-L.

The caption pipeline stays above the baseline along the entire ladder.
Centering gives the baseline its big jump; contextualisation gives the largest
single gain.

> If asked why it stops here: projection and query expansion do not help once
> the caption branch is present → backup 25.

## 17. Does it transfer? Four frozen backbones | 0:45 | cum 11:35
We evaluate four frozen backbones: CLIP ViT-L — our main backbone — the larger
CLIP ViT-H, SigLIP ViT-L, and the recent SigLIP2, the best-aligned of the
four.

The caption branch improves every single one. The largest jump is SigLIP-L,
where macro-mAP roughly doubles, from 21 to 43. SigLIP2 is the strongest base
model.

So the contribution does not depend on one particular vision–language model.

## 18. Our best overall system | 0:40 | cum 12:15
The final system: SigLIP2, the caption branch with five averaged captions, and
centering plus contextualisation. Everything frozen.

It reaches 61.98 macro-mAP. Beyond mAP: the correct target is ranked first for
71% of queries and appears in the top ten for 95%. Recall at one hundred is
94%.

That high recall matters — I will come back to it in the future work.

> The SigLIP2 ladder behind 61.98 → backup 26.

## 19. Qualitative example — success | 0:25 | cum 12:40 (flex)
A success: Homer Simpson, "as a plushie".

The plain product gets 4% AP — generic plushies: SpongeBob, minions. BASIC
reaches 33%. The caption — "Homer Simpson as a plushie, same facial features"
— pins the retrieval to actual Homer plushies: 88%. The caption keeps the
identity while honouring the modification.

## 20. Qualitative example — failure | 0:25 | cum 13:05 (flex)
An honest failure: gold metal eyeglasses, "worn by a dog".

All three methods score near zero. The single ground truth is a dog actually
wearing these glasses; every method returns glasses on tables instead. When
the modification demands a drastic, rarely-photographed context, the image
branch dominates and the target never gets near the top.

## 21. Limitations and future work | 0:40 | cum 13:45
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

## 22. Conclusions | 0:30 | cum 14:15
Two conclusions.

The caption is the single most effective component — it improves every
backbone on the full dataset.

And SigLIP2 is the strongest backbone for the pipeline, reaching the
thesis-best 61.98 macro-mAP, fully zero-shot.

> If pushed: the caption alone beats the plain product on CLIP-L → backup 27;
> centering and the caption stack → backup 28.

## 23. Thank you | — | —
Thank you. I am happy to take questions.

## Q&A map | — | —
Score fusion formulas + Harris penalty → **backup 24**. Full CLIP-L ablation,
every rung (incl. projection and query expansion) → **backup 25**. SigLIP2
ladder (produces 61.98) → **backup 26**. Component contributions — image-only,
text-only, caption-only, product, triplet → **backup 27**. Centering + caption
are complementary → **backup 28**. "The paper reports 34.35 for BASIC" →
**backup 29**. Latency breakdown → **backup 30**. Five instruction strategies,
sample captions → **backup 31**; what each does → **backup 32**.

Problem formulation on slide 7; metric on slide 8; full pipeline figure on
slide 11; backbone table on slide 17.

---

# Backup-slide notes

## 24. Combining the three scores
Min-based normalization puts the three branches on comparable scales;
negative residuals are clamped to zero — no positive evidence. The normalized
scores are multiplied: a soft logical AND. On top, a Harris-inspired penalty,
from the Harris corner detector: a candidate must not win on one branch alone
— the exact chair not around a table, or tables with the wrong chair, are both
suppressed. The penalty is weighted by a hyperparameter lambda, fixed across
all experiments. The surface shows the score is high only when both arguments
are simultaneously large.

## 25. Full CLIP-L ablation
Every rung, for the three pipelines. Two extra BASIC steps appear here:
projection and query expansion. Projection barely helps BASIC (32.25 → 32.48)
and *hurts* the caption pipelines; query expansion hurts everything. That is
why our pipeline stops at contextualisation. Best triplet: 35.76.

## 26. SigLIP2 ladder
Same shape as CLIP-L: the caption pipeline stays above BASIC throughout, and
contextualisation gives the final jump. Best configuration 61.98 macro-mAP vs
57.69 for BASIC at the same rung — and 38.1 for the plain product.

## 27. Component contributions (CLIP-L)
Each branch alone, then the combinations — raw similarity, no post-processing.
Image only 2.75, text only 3.26: neither works alone. The caption alone
reaches 19.51 — it already beats the full image × text product at 17.95,
because it is the only signal that sees both query parts. Adding it to the
product: 25.41.

## 28. Centering and the caption are complementary
The caption gain is not absorbed by centering. At the raw product the caption
adds +7.5; after centering it still adds +4.1. The two contributions stack,
which is why the best configuration keeps both.

## 29. Reproducing BASIC
The paper reports 34.35; our re-run of the released code gives 32.48. The gap
is concentrated in the image branch and is consistent with re-extracting
features in a newer software stack — image decoding and resizing differ across
library versions. Contextualisation also draws fresh object nouns per query.
Both BASIC and our method run in the same environment, so every comparison in
the thesis is unaffected.

## 30. Inference latency
100 queries, RTX-6000-Ada. Caption generation — five captions — takes about
14.7 seconds and is 99.7% of the online cost; embedding the query triplet is
milliseconds, and the backbone choice does not change latency. Database
embeddings are precomputed offline. Levers: fewer captions, shorter
generations, a smaller or quantised MLLM.

## 31. The five instructions — sample captions
The five strategies on the Tintin example, "as an iconic rooftop sign". Each
phrases the same target differently; their embeddings are averaged (avg-5).

## 32. The five instructions — explained
Adaptive precision adjusts the detail level to the query. Constraint-priority
states the modification first so it is never dropped. The anti-noise contract
forbids inventing attributes not visible in the image. The slot-fill template
keeps captions uniform and comparable. Draft–refine adds a self-correction
pass. They were chosen from twenty-plus candidates because each controls a
different failure mode.
