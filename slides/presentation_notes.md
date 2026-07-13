# Defense notes — Imagining the Target
Asma Hoseinpour Siouki · MSc Data Science · University of Padova · July 2026
**20-minute slot, script paced for ≈14:20** — leaves generous buffer for
questions, transitions, and running over. 21 talk slides + thank-you (22) +
11 backups (23–33). Slide 19 is the flex valve: cut it if you are behind.
During Q&A: type a backup slide's number + Enter to jump straight to it.

## 1. Title | 0:20 | cum 0:20
Good morning everyone, and thank you for being here.

My name is Asma, and today I will be presenting my thesis work on
**instance-level composed image retrieval** — and specifically, on how we can
use a multimodal language model to imagine the target image before we search
for it.

This work was supervised by Professor Ballan and co-supervised by
Professor Fiorucci.

## 2. Composed Image Retrieval | 0:55 | cum 1:15
Let me start with the task itself.

Imagine you see a chair online that you really like, and you want to find a
dining set that includes that exact chair together with a table.

Searching with the image alone returns the same chair, or chairs that look
similar — but not as part of a dining set. Searching with text alone, "a dining
table and chairs", returns many dining sets — but not your specific chair.

You need both: the image identifies the object, the text describes the context
you want to find it in.

This is composed image retrieval. The query has two parts — a reference image
and a modification text — and the goal is to retrieve images that preserve the
reference object while satisfying the modification.

> Naming note: these are simply the two halves of the query, so from here on I
> call them the **query image** and the **query text**.

## 3. Instance-level composed retrieval | 0:40 | cum 1:55
My thesis focuses on the instance-level version of this task.

In category-level retrieval, any object of the right class counts as correct —
any chair around a table would do. At the instance level that is not enough:
the system must retrieve the exact same chair from the query image, while also
satisfying the query text.

So the challenge is to detect that one specific instance among many
look-alikes, even when its context, viewpoint, or visual domain changes.

## 4. The i-CIR benchmark | 0:50 | cum 2:45
We work on i-CIR, the benchmark built specifically for this task.

Each object instance comes with several composed queries — a query image plus a
query text. Importantly, a single query can have **multiple correct targets**,
so evaluation is about ranking all of them highly, not finding one right
answer.

Each instance also comes with curated hard negatives: images that look very
similar but fail the modification, or that satisfy the modification but show a
different object. That is what makes the benchmark hard — you cannot succeed by
using only one half of the query.

## 5. The i-CIR benchmark — scale | 0:25 | cum 3:10
Briefly, the scale. Around 752 thousand images in total, 202 instances, and
1,883 composed queries.

The three histograms show the distributions: the hard negatives per instance,
the number of correct targets per composed query — confirming that many queries
have more than one — and the composed queries per instance, with a median of
six.

## 6. A zero-shot setting | 0:40 | cum 3:50
We work in a zero-shot setting: we never train or fine-tune any model on i-CIR.
The benchmark itself is designed this way — it provides no training split, only
the queries and their retrieval pools.

And this is the right choice for the task. Supervised composed retrieval needs
labelled triplets, so at the instance level every new object would need new
annotation. Worse, a model trained on a fixed set of instances would not
necessarily generalize to instances it has never seen — and in practice new
objects appear all the time. Supervision would hurt both scalability and
generalizability.

With frozen pre-trained models, the system applies directly to unseen
instances.

## 7. Problem formulation | 0:25 | cum 4:15
Formally: given a query image and a query text, the retrieval system scores
every image in the instance's pool and ranks them from most to least relevant.

One detail specific to this benchmark: each instance has its **own** retrieval
pool — its positives plus its curated hard negatives — and the pool size varies
from instance to instance.

So for each instance we rank that instance's pool, and return the top-k as the
retrieval result.

## 8. Evaluation metric | 0:40 | cum 4:55
Every metric here is evaluated at a cut-off k.

Precision-at-k is the fraction of the top-k results that are correct. AP-at-k
builds on it and is high when the correct images sit near the top of the
ranking. mAP averages that over all queries.

But instances have different numbers of queries, so a plain average would let
the big instances dominate. Our main metric is therefore **macro-mAP**: we
average within each instance first, then across instances, so every instance
counts equally.

Throughout the thesis we set **k = 100** — the standard cut-off in this
literature, which keeps our numbers comparable.

## 9. Vision–language models: CLIP and SigLIP | 0:55 | cum 5:50
Now, the core technical challenge: to retrieve anything, we need to represent
images and texts in a way that lets us actually measure how similar they are.

That is what vision–language models give us. Both CLIP and SigLIP are
dual-encoders: an image encoder and a text encoder that map their inputs into
the **same** shared embedding space. Once an image and a text are vectors in
one space, their similarity is just the cosine of the angle between them.

We use these models completely frozen — we only extract embeddings.

The two differ in how they were trained. CLIP compares all image–text pairs
within a batch through a softmax contrastive objective. SigLIP treats each pair
independently with a sigmoid loss — no global softmax, which scales better to
large batches.

We test both families to check that our contribution does not depend on one
particular model.

## 10. The baseline: BASIC | 0:55 | cum 6:45
Our baseline is BASIC, the zero-shot method released with the benchmark by
Psomas and colleagues.

BASIC has two branches, and it processes the two halves of the query
separately: the query image goes through the visual encoder, the query text
through the text encoder.

For every image in the pool it computes two similarities — one to the query
image, one to the query text — and **the score used for ranking is the product
of these two similarities**. The multiplication acts like a soft logical AND: a
candidate only scores high if it matches both halves of the query.

BASIC uses CLIP ViT-L/14 as its main backbone, which is also the standard in
this literature, so we adopt the same one and our results stay directly
comparable.

## 11. Two refinements: centering and contextualisation | 0:50 | cum 7:35
BASIC adds two refinements, and we keep both. One acts on the embeddings, one
on the query text.

**Centering.** Embedding spaces carry a large component that is common to
almost everything — generic visual and linguistic patterns rather than what
makes a specific image distinctive. We subtract a per-modality mean, computed
on a separate corpus, and re-normalise. That isolates the semantic content.

**Contextualisation** acts on the raw query text, so it is a query-side step,
not score post-processing. The text encoder was trained on full captions, so a
bare fragment like "sculpture" is out of distribution and gives a weak text
feature. We enrich the query with terms from a subject corpus, before and
after — "sculpture dog" — then embed and average the variants.

## 12. Limitation of the baseline — our proposal | 0:55 | cum 8:30
Here is the key limitation. In BASIC, the query image and the query text are
**never processed jointly**. Each branch only ever sees half of the query, so
the complete composed query is never actually represented anywhere.

Our proposal is to add a third branch. This is the full pipeline: the image and
text branches as before — and in addition, both halves of the query go together
into a multimodal language model, which **imagines the target** and writes a
caption describing it. That caption is embedded by the same frozen text
encoder, and becomes a third similarity score.

The three scores are normalised and multiplied — a soft logical AND across all
three branches.

> Fusion formulas and the Harris penalty → backup 23.

## 13. The captioner: InternVL 3.5-8B | 0:40 | cum 9:10
For caption generation we use InternVL 3.5, at eight billion parameters, frozen
— an open-source multimodal model that takes an image and a text together, at a
practical balance of quality and cost. No fine-tuning anywhere in this
pipeline.

In the chair example it sees the chair image plus "placed around a table", and
writes: "White metallic chair with scrolled armrests placed around a table."

Notice that this single caption carries **both** the visual identity of the
object and the requested context — exactly the signal the two separate branches
cannot represent on their own.

## 14. Designing the instruction | 0:35 | cum 9:45
Caption quality depends strongly on how we instruct the model to generate it. I
tested more than twenty instructions, varying the level of detail, the use of
examples, the order of constraints, and restrictions against irrelevant
information.

From these I selected five complementary strategies. Each describes the
imagined target from a different angle, and we average their caption
embeddings.

> What each strategy does → backup 33.

## 15. Effect of the caption branch | 0:45 | cum 10:30
And this is the payoff. A single caption lifts macro-mAP from 17.95 to 23.83 —
almost six points — which says the caption is carrying compositional
information the two branches miss on their own.

Averaging five captions from the five strategies does better still: it
suppresses wording specific to any one prompt and keeps what they agree on.
That reaches 25.41 — about seven and a half points over the image–text
baseline.

> All results from here on are CLIP ViT-L/14 unless stated otherwise.

## 16. Adding the steps on top of each other | 0:30 | cum 11:00
Here we add each step cumulatively — the baseline in blue, our caption pipeline
in red, on CLIP-L.

The caption pipeline stays above the baseline at every single rung. Centering
gives the baseline its big jump, and contextualisation gives the largest single
gain.

> Why it stops at contextualisation: projection and query expansion do not help
> once the caption branch is present → backup 25.

## 17. Does it transfer? Four frozen backbones | 0:45 | cum 11:45
Next: does this depend on the backbone? We test four frozen ones — CLIP ViT-L,
our main backbone; the larger CLIP ViT-H; SigLIP ViT-L; and the recent SigLIP2.

The caption branch improves **every single one**. The biggest jump is on
SigLIP-L, where macro-mAP roughly doubles, from 21 to 43. And SigLIP2 is
clearly the strongest backbone overall.

So the contribution is not a CLIP-specific trick.

## 18. Our best overall system | 0:40 | cum 12:25
Putting the best pieces together: SigLIP2, the caption branch with five
averaged captions, and centering plus contextualisation. Every component
frozen.

That reaches **61.98 macro-mAP** — four point three above the strongest BASIC
configuration.

And recall@100 is 93.8%: for almost every query, a correct target *is*
somewhere in the retrieved shortlist. Hold onto that number — I come back to it
in the future work.

> The SigLIP2 ladder behind 61.98 → backup 27.

## 19. Qualitative example — success | 0:25 | cum 12:50 (flex)
One example of it working. Homer Simpson, "as a plushie".

The plain product scores 4% — it drifts off to generic plushies: SpongeBob,
minions, a teddy bear. BASIC gets 33%. Our caption — "Homer Simpson as a
plushie, with the same facial features" — pins the search to actual Homer
plushies and reaches 88%.

That is the caption branch doing exactly its job: holding onto the identity
while honouring the modification.

## 20. Limitations and future work | 0:45 | cum 13:35
Limitations. The main one is compute: caption generation dominates the online
cost. And the results are sensitive to prompt design — averaging five captions
mitigates that, but does not remove it.

For future work, the fixed product could be replaced by a learned or weighted
fusion of the three similarities, trading the zero-shot constraint for
accuracy.

But the direction I find most promising follows from that recall number.
Because recall is already so high, a correct target is nearly always in the
shortlist — which means most of the remaining error is in the **ordering** of
candidates we have already retrieved. That is exactly what a second-stage
reranker fixes, and a caption-conditioned reranker would keep the modification
in the loop at that stage too.

Finally, the caption-as-a-third-modality idea is benchmark-agnostic, so it
could be tested well beyond i-CIR.

## 21. Conclusions | 0:30 | cum 14:05
Two conclusions.

First, the **caption is the single most effective component** — adding the
target caption improves every backbone we tested, on the full dataset.

And second, **SigLIP2 is the strongest backbone** for this pipeline, reaching
61.98 macro-mAP — the best result in the thesis, and fully zero-shot.

> If pushed: the caption alone beats the plain product on CLIP-L → backup 28;
> centering and the caption stack rather than overlap → backup 29.

## 22. Thank you | 0:15 | cum 14:20
Thank you for your attention. I am happy to take any questions.

## Q&A map | — | —
Score fusion + Harris penalty → **23**. Failure case → **24**. Full CLIP-L
ablation, every rung incl. projection and query expansion → **25**. Same
ablation on SigLIP2 → **26**. SigLIP2 ladder (produces 61.98) → **27**.
Single-branch baselines → **28**. Centering + caption complementary → **29**.
"The paper reports 34.35 for BASIC" → **30**. Latency / "is 15 s per query
practical?" → **31**. The five instructions: sample captions → **32**, what
each one does → **33**.

In the talk: problem formulation slide 7 · metric slide 8 · pipeline figure
slide 12 · backbone table slide 17.

---

# Backup-slide notes

## 23. Combining the three scores
Min-normalisation puts the three branches on comparable scales, and negative
residuals are clamped to zero — they count as no evidence. The normalised
scores are then multiplied: a soft logical AND. On top of that, a
Harris-inspired penalty, borrowed from the Harris corner detector, where a
strong response in only one direction is not enough. A candidate must not win
on one branch alone — the exact chair *not* around a table, or a table with the
wrong chairs, are both suppressed. λ is a hyperparameter, fixed across every
experiment. The surface shows the effect: the score is high only when both
arguments are large at once.

## 24. Qualitative example — failure
Gold metal eyeglasses, "worn by a dog". All three methods score near zero. The
single ground truth is a photo of a dog actually wearing these glasses, and
every method instead returns glasses on tables. This is the characteristic
failure mode: when the modification demands a drastic, rarely-photographed
context, the image branch dominates and the caption cannot rescue it.

## 25. Full ablation — CLIP ViT-L/14
Every rung, all three pipelines. Two extra BASIC steps appear here: projection
barely helps BASIC (32.25 → 32.48) and actively *hurts* the caption pipelines;
query expansion hurts everything. That is why our pipeline stops at
contextualisation. Best triplet: 35.76.

## 26. Full ablation — SigLIP2 g/16-384
The same ladder on the best backbone; 61.98 at contextualisation against 57.69
for BASIC at the same rung. Note the single-caption column here is instruction
**H** (the strongest single instruction on SigLIP2), whereas the CLIP-L table
uses instruction J — so that one column is not strictly like-for-like across
the two tables.

## 27. SigLIP2 ladder
The same story as CLIP-L in chart form: the caption pipeline leads at every
rung, and contextualisation gives the final jump — 61.98, against 57.69 for
BASIC and 38.1 for the plain product.

## 28. Baselines — what each branch contributes
Each branch alone, then the combinations; raw similarity, no post-processing.
Image only 2.75, text only 3.26 — neither works alone. But the **caption alone
reaches 19.51**, already beating the full image × text product at 17.95,
because it is the only signal that has seen both halves of the query. Adding it
to the product gives 25.41.

## 29. Centering and the caption are complementary
The caption's gain is not absorbed by centering. At the raw product the caption
adds +7.5; after centering it still adds +4.1. The two contributions stack,
which is why the best configuration keeps both.

## 30. Reproducing BASIC
The paper reports 34.35; our re-run of the released code gives 32.48. The gap
sits in the image branch and is consistent with re-extracting features on a
newer software stack — image decoding and resizing differ across library
versions. Contextualisation also draws fresh nouns per query, adding a little
run-to-run variance. Crucially, BASIC and our method run in the *same*
environment, so every comparison in the thesis is unaffected.

## 31. Inference latency — the cost of the caption
Online cost per query on CLIP-L; database embeddings are precomputed offline.
BASIC costs ~254 ms, most of which is its own contextualisation step (196 ms).
Our caption branch is what dominates: one caption costs 3.11 s, five cost
15.13 s. Embedding is negligible either way — tens of milliseconds, and only
2–4 ms to encode the captions themselves.

The useful point: this is a real accuracy-vs-latency knob. A **single** caption
already gives 23.83 macro-mAP against BASIC's 17.95, at a fifth of the caption
cost; avg-5 buys only 1.6 points more for five times the compute. If latency
mattered in deployment, K=1 is the operating point to pick.

## 32. The five instructions — sample captions
The five strategies on the Tintin example, "as an iconic rooftop sign". Each
phrases the same imagined target differently; their embeddings are averaged.

## 33. The five instructions — explained
Adaptive precision scales the detail to the query. Constraint-priority states
the modification first so it is never dropped. The anti-noise contract forbids
inventing attributes not visible in the image. The slot-fill template keeps
captions uniform and comparable. Draft–refine adds a self-correction pass. They
were selected from twenty-plus candidates precisely because each one controls a
different failure mode.
