# Defense notes — Imagining the Target
Asma Hoseinpour Siouki · MSc Data Science · University of Padova · July 2026
**20 minutes fixed.** 22 talk slides + thank-you (23) + 8 backups (24–31).
Plan totals ≈18:50, leaving ~1:10 of margin. Slides 19–20 are the flex valve:
if you are behind, give each 20 s instead of 30 s, or show only the success case.
During Q&A: type a backup slide's number + Enter to jump straight to it.

## 1. Title | 0:20 | cum 0:20
Good morning everyone, and thank you for being here.

## 2. Composed Image Retrieval | 1:05 | cum 1:25
Imagine that you see a chair online that you really like, but you would like to
find a dining set that includes that same chair design together with a table.

Searching only with the image of the chair would mainly return the same chair or
other visually similar chairs. It would not understand that you are looking for
it as part of a dining set.

On the other hand, searching only for "a dining table and chairs" would return
many different sets, but probably not the specific chair you selected.

To express exactly what you are looking for, you need to combine both elements:
the image identifies the chair, while the text describes the context in which you
want to find it.

This is an example of composed image retrieval, which is the task I worked on in
my thesis. The query consists of a reference image and a modification text, and
the goal is to retrieve images that preserve the reference object while also
satisfying the modification described by the text.

> One naming note: the reference image and modification text are simply the two
> parts of the query, so from here on I will call them the **query image** and the
> **query text**.

## 3. Instance-level composed retrieval | 0:55 | cum 2:20
My thesis focuses specifically on the instance-level version of this task.

In category-level composed image retrieval, any object belonging to the correct
class may satisfy the query. For example, if the query asks for a chair around a
dining table, any suitable chair design might be considered correct.

In instance-level retrieval, this is not enough. The system must retrieve the
exact same chair shown in the query image, while also satisfying the query text.

So the main challenge is to detect that one specific instance among many
look-alikes of the same class — even when its context, appearance, viewpoint, or
visual domain changes.

## 4. The i-CIR benchmark | 1:05 | cum 3:25
For our experiments we use the i-CIR benchmark, which was specifically designed
for instance-level composed image retrieval.

Each object instance is associated with several composed queries, and every
composed query consists of a query image and a query text.

Importantly, each query may have multiple correct target images — several database
images can correctly depict the same object under the requested modification. So
evaluation is not about finding one right answer; it is about ranking all of them
highly.

In addition, each instance has its own database of carefully curated hard
negatives. These are designed to confuse the system. Some are visually similar to
the query image but fail to satisfy the query text. Others satisfy the query text
but depict a different object instance. Some match both parts partially while
still being incorrect. This prevents the system from succeeding by relying only on
the image or only on the text.

## 5. The i-CIR benchmark — scale | 0:35 | cum 4:00
A word on scale. i-CIR contains a database of seven hundred fifty-two thousand
images, two hundred and two object instances, and one thousand eight hundred
eighty-three composed queries, with a median of six queries per instance.

The histograms show the distributions: image and text queries per instance, hard
negatives per instance, and the number of correct targets per composed query —
which confirms that many queries have more than one ground truth.

## 6. Problem formulation — a zero-shot setting | 0:55 | cum 4:55
Formally, we are given a query image and a query text, and we want to retrieve
database images that are relevant to both.

In this thesis we adopt a zero-shot setting: we do not train or fine-tune any
model on the i-CIR dataset.

Why does this matter? Supervised composed image retrieval requires labelled
triplets — a query image, a query text, and a correct target image. At the
instance level, collecting these annotations for every new object would be
expensive and hard to scale. Worse, a model trained on a fixed set of instances
does not necessarily generalize to instances it has never seen — and in a real
system new objects appear constantly. So a supervised approach would decrease both
the scalability and the generalizability of the system.

Instead, by using frozen pre-trained models, the retrieval system applies directly
to previously unseen object instances, with no additional training.

## 7. Retrieval, ranking, and the metric | 0:55 | cum 5:50
First, how retrieval actually works. Given a query, the system assigns a relevance
score to every database image, and sorts them from most to least relevant. This
ranked list is the output; the evaluation checks where the correct targets land in
it.

For a single query we use Average Precision. AP is high when the correct images
appear near the top of the ranking; if they appear lower, the score decreases.

We then compute mean Average Precision by averaging AP across all queries.

However, the number of queries is not the same for every instance. If we averaged
directly over all queries, instances with more queries would dominate the result.

For this reason our main metric is macro-mAP: we first average within each object
instance, and then across instances — so every instance contributes equally.

## 8. Vision–language models: CLIP and SigLIP | 1:10 | cum 7:00
The main technical challenge is combining the information from the query image and
the query text. To represent both modalities we use frozen, pre-trained
vision–language models: CLIP and SigLIP.

These use a dual-encoder, or two-tower, architecture. One encoder processes
images, the other processes text, and both map their inputs into the same
embedding space. Because the representations share this space, we measure semantic
similarity with cosine similarity: an image scores high when its embedding is close
to the embedding of the corresponding text.

The models are used completely frozen — we only extract embeddings, we never update
their parameters.

CLIP and SigLIP follow the same dual-encoder principle but differ in training.
CLIP compares all image–text pairs within a batch, using a softmax contrastive
objective. SigLIP instead classifies each pair independently with a sigmoid loss —
no global softmax, which scales better to large batches.

We compare these frozen backbones to test whether our method depends on one
particular vision–language model.

## 9. The baseline: BASIC | 1:10 | cum 8:10
The baseline for our work is BASIC, the zero-shot method introduced together with
the i-CIR benchmark by Psomas and colleagues in 2025.

BASIC processes the two parts of the composed query separately. The query image is
encoded by the visual encoder, and the query text by the text encoder. The database
images are encoded in advance by the visual encoder.

For every database image, BASIC computes two similarity scores: the visual
similarity, how similar the database image is to the query image; and the textual
similarity, how well it matches the query text. Both are dot products between the
corresponding embeddings.

The two scores are then multiplied. This multiplicative fusion acts like a soft
logical AND: a database image receives a high final score only if it matches both
the query image and the query text.

The method also includes additional processing steps — centering, score
normalization, contextualization — which I will discuss later.

## 10. Limitation of the baseline — our proposal | 1:10 | cum 9:20
The main limitation of the baseline is that the query image and the query text are
never processed jointly. The image branch only sees the query image, the text
branch only sees the query text. As a result the model does not explicitly
represent the complete composed query.

To address this, we introduce a third scoring branch based on a generated target
caption.

This is the full pipeline. The query image and query text go, as before, to the
image and text branches. In addition, together, they go to a multimodal language
model that imagines the target and writes a caption of it. That caption is embedded
by the same frozen text encoder and becomes a third similarity score.

So for every database image we now compute three scores — to the image, to the
text, and to the generated caption — and combine them. I will detail the captioner
and the fusion on the next slides.

## 11. The captioner: InternVL 3.5-8B | 0:50 | cum 10:10
For target-caption generation we use the frozen eight-billion-parameter version of
InternVL 3.5 — an open-source multimodal LLM that can jointly process an image and
text, which is exactly what the caption branch requires. At eight billion
parameters it is a practical balance of quality and cost, and we use it entirely
without fine-tuning.

Concretely, it receives the query image, the query text, and our instruction to
describe the imagined target. In the chair query it sees the specific chair
together with the text "placed around a table", and generates: "White metallic
chair with scrolled armrests placed around a table."

Notice that this single caption contains information from both parts of the query —
the visual identity of the chair and the context specified by the text. That is the
signal the two separate branches cannot represent on their own. We embed it with the
same frozen text encoder to get the third similarity score.

## 12. Designing the instruction | 0:45 | cum 10:55
An important part of the caption-generation stage is the instruction given to the
multimodal model.

The quality of the generated caption depends strongly on how the task is
formulated. For this reason I carried out an extensive prompt-design process and
tested more than twenty different instructions, varying the level of detail, the use
of examples, the order of the constraints, and restrictions intended to prevent the
model from introducing irrelevant information.

Based on these experiments I selected five complementary prompting strategies. Each
describes the imagined target from a slightly different perspective, and together
they produce a diverse set of captions whose embeddings we average.

> What each strategy does → backup 31.

## 13. Effect of the caption branch | 0:55 | cum 11:50
Adding a single generated caption improves macro-mAP by about 5.9 points, from
17.95 to 23.83. This suggests the caption captures useful compositional information
that is not fully represented by the image and text branches separately.

Using multiple captions improves the result further. We generate five captions with
different prompting strategies, average their embeddings, and use the result for
retrieval. This reduces the influence of prompt-specific wording and emphasizes
information that is consistent across the captions.

With this five-caption average, macro-mAP reaches 25.41 — about 7.5 points above the
original image–text baseline.

> From this point on, all results use CLIP ViT-L/14 as the backbone, unless stated
> otherwise.

## 14. Combining the three scores | 1:00 | cum 12:50
We now have three similarity scores per database image — to the query image, the
query text, and the generated caption. How do we combine them?

First, min-based normalization puts the three branches on comparable scales, and any
negative residual values are clamped to zero — meaning they provide no positive
evidence for the candidate.

The normalized scores are then combined multiplicatively, because a good result must
match all three branches at the same time — like a soft logical AND.

On top of that we use a Harris-inspired penalty. The idea comes from the Harris
corner detector, where a strong response in only one direction is not enough.
Similarly, a candidate should not win just because it matches one branch very well
while matching the others poorly — for example an image that shows the exact chair
but not around a table, or chairs around a table that are not the specific chair. The
Harris term penalizes this imbalance, weighted by a hyperparameter lambda.

The surface on the right shows the effect: the score is only high when both arguments
are simultaneously large.

## 15. Two refinements: centering and contextualisation | 1:05 | cum 13:55
Two further techniques improve retrieval — one on the embeddings, one on the query
text itself.

**Centering**, applied to the embeddings. Vision–language embedding spaces contain a
large common component shared by many embeddings — generic visual or linguistic
patterns rather than the distinctive information needed for retrieval. We compute a
mean embedding for each modality on a separate corpus, subtract it, and re-normalise.
This isolates the semantic content from the shared distributional bias.

**Contextualisation**, applied to the raw query text — so it is a query-side step, not
a score post-processing step. The text encoder is trained mostly on full captions, so
a bare fragment such as "sculpture" or "during sunset" is out-of-distribution and
produces a text feature poorly aligned with image features. We therefore enrich the
query with terms from a subject corpus, before and after — "dog during the sunset",
"sculpture dog" — then embed and average the variants, giving a more robust textual
feature.

## 16. Adding the steps on top of each other | 0:40 | cum 14:35
Here we add each step cumulatively, for the baseline in blue and our caption pipeline
in red, on CLIP ViT-L/14.

The caption pipeline stays above the baseline along the entire ladder. Centering
gives a large jump for the baseline, and contextualisation gives the largest single
gain.

> If asked why the ladder stops here: two further BASIC steps — the contrastive
> projection and query expansion — do not help once the caption branch is present.
> Numbers → backup 24.

## 17. Does it transfer? Four frozen backbones | 0:55 | cum 15:30
We evaluate the pipeline with four frozen backbones, spanning two model families and
two capacity levels. CLIP ViT-L/14 is the backbone most commonly reported in the
zero-shot CIR literature, which makes our numbers comparable. CLIP ViT-H/14 is the
higher-capacity variant. SigLIP replaces the softmax contrastive loss with the
pairwise sigmoid loss — we use SigLIP ViT-L/16 and the more recent SigLIP2 g/16, the
best-aligned encoder of the four.

The caption branch improves every single one of them. The largest jump is on
SigLIP-Large, where macro-mAP roughly doubles, from twenty-one to forty-three.
SigLIP2 is the strongest base model.

This shows that our contribution does not depend on one particular vision–language
model.

## 18. Our best overall system | 0:50 | cum 16:20
To state the final system plainly: the SigLIP2 backbone, the caption branch with five
averaged captions, and post-processing through centering and contextualisation. Every
component is frozen.

It reaches 61.98 macro-mAP and 62.07 mAP. Beyond mAP: the correct target is ranked
first for 71% of queries, and appears in the top ten for 95% of queries. Recall at one
hundred is 94%.

That high recall is important — I will come back to it in the future work.

> The SigLIP2 ladder that produces 61.98 → backup 25.

## 19. Qualitative example — success | 0:30 | cum 16:50 (flex)
A qualitative success. The query is Homer Simpson, with the modification "as a
plushie".

The plain image-times-text product scores only 4% AP — it drifts to generic plushies:
SpongeBob, minions, a teddy bear. BASIC reaches 33%. Adding the generated caption —
"Homer Simpson as a plushie, with the same facial features" — pins the retrieval to
actual Homer plushies and lifts AP to 88%. This is the caption branch doing exactly
what it is meant to do: keeping the specific identity while honouring the
modification.

## 20. Qualitative example — failure | 0:30 | cum 17:20 (flex)
And an honest failure. Gold metal eyeglasses, "worn by a dog".

Here all three methods fail — AP near zero. The single ground truth is a photo of a
dog actually wearing these glasses. Every method instead returns glasses photographed
on tables or held up, because the visual branch anchors hard on the glasses
themselves and the caption cannot overcome a target this rare.

This is the characteristic failure mode: when the modification demands a drastic,
rarely-photographed context, the image branch dominates and the correct target is
simply not near the top.

## 21. Limitations and future work | 0:50 | cum 18:10
Three limitations. The main cost is caption generation — about fifteen seconds per
query, which dominates online inference. The results also depend on prompt design:
averaging five captions mitigates this, but does not remove it. And the fixed,
unweighted product cannot adapt when one branch should matter more than the others.

Several directions follow naturally. A stronger or more efficient captioner — or a
single high-quality caption that matches the five-caption average without five
generations — would cut the main compute cost. The fixed product could be replaced by
a learned or weighted fusion of the three similarities, relaxing the zero-shot
constraint in exchange for accuracy.

Because recall is already high — the correct instance lands in the top-ranked
shortlist for the large majority of queries — a second-stage reranker that reorders
this shortlist is a promising direction: most of the remaining error is in the
ordering of candidates that are already retrieved. A text-conditioned reranker that
reorders by similarity to the target caption, rather than to the query image, is a
natural candidate, since it keeps the modification in the loop at the reranking stage.

Finally, the caption-as-third-modality idea is benchmark-agnostic and could be
evaluated beyond i-CIR — on category-level CIR benchmarks and other instance-level
retrieval settings.

## 22. Conclusions | 0:40 | cum 18:50
Two conclusions.

First, the caption is the single most effective component. Adding the target caption
improves every backbone on the full dataset.

Second, SigLIP2 is the strongest backbone for the pipeline, reaching the thesis-best
61.98 macro-mAP, fully zero-shot.

> If pushed further: the caption alone already beats the plain image-times-text
> product on CLIP-L (backup 26), and centering and the caption are complementary —
> their gains stack (backup 27).

## 23. Thank you | — | —
Thank you. I am happy to take questions.

## Q&A map | — | —
Full CLIP-L ablation, every rung (incl. projection and query expansion) →
**backup 24**. SigLIP2 ladder (produces 61.98) → **backup 25**. Component
contributions — image-only, text-only, caption-only, product, triplet — showing the
caption alone beats the product → **backup 26**. Centering and the caption are
complementary (gains stack) → **backup 27**. "The paper reports 34.35 for BASIC" →
**backup 28** (our reproduction gives 32.48; the gap is in the image branch, from
re-extracting features in a newer software stack; both methods are evaluated in the
same environment, so the comparisons hold). Latency breakdown → **backup 29**. The
five instruction strategies with their sample captions → **backup 30**; what each
strategy does → **backup 31**.

Metric on slide 7; the full pipeline figure on slide 10; fusion detail on slide 14;
the backbone table on slide 17.
