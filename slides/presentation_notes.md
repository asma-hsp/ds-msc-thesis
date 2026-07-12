# Defense notes — Imagining the Target
Asma Hoseinpour Siouki · MSc Data Science · University of Padova · July 2026
**20 minutes fixed.** 22 talk slides + thank-you (23) + 6 backups (24–29).
Plan totals ≈19:25, leaving ~35 s of margin. Slides 19–20 are the flex valve:
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
my thesis. The query consists of a reference image and a textual modification.
The goal is to retrieve images that preserve the information provided by the
reference image while also satisfying the modification described by the text.

## 3. Instance-level composed retrieval | 0:55 | cum 2:20
My thesis focuses specifically on the instance-level version of this task.

In category-level composed image retrieval, any object belonging to the correct
class may satisfy the query. For example, if the query asks for a chair around a
dining table, any suitable chair design might be considered correct.

In instance-level retrieval, this is not enough. The system must retrieve the
exact same chair shown in the reference image, while also satisfying the textual
modification.

Therefore, the main challenge is to preserve the identity of a specific object
even when its context, appearance, viewpoint, or visual domain changes.

## 4. The i-CIR benchmark | 1:15 | cum 3:35
For our experiments, we use the i-CIR benchmark, which was specifically designed
for instance-level composed image retrieval.

Each object instance is associated with several composed queries, and every
composed query consists of a reference image and a modification text.

Each query may also have multiple correct target images. Several database images
can correctly depict the same object under the requested modification.

In addition, each instance has its own database containing carefully curated hard
negatives. These are designed to confuse the retrieval system. Some are visually
similar to the reference image but fail to satisfy the textual modification.
Others satisfy the modification but depict a different object instance. Some
appear to match both parts partially while still being incorrect.

This prevents the system from succeeding by relying only on the image or only on
the text.

The scale: seven hundred fifty-two thousand database images, two hundred and two
object instances, one thousand eight hundred eighty-three composed queries — a
median of six per instance.

> Full distributions → backup 28.

## 5. Problem formulation — zero-shot | 1:00 | cum 4:35
To summarize the task, we are given a reference image and a modification text,
and we want to retrieve database images that are relevant to both.

The system assigns a score to every image in the database and ranks the images
from the most relevant to the least relevant.

In this thesis, we adopt a zero-shot setting. This means that we do not train or
fine-tune any model on the i-CIR dataset.

This choice is important because supervised composed image retrieval requires
labelled triplets consisting of a reference image, a modification text, and a
correct target image. At the instance level, collecting these annotations for
every new object would be expensive and difficult to scale — every newly
introduced object instance could require additional labelled training data.

Instead, by using frozen pre-trained models, the retrieval system can be applied
directly to previously unseen object instances without additional training.

## 6. Evaluation metric | 0:50 | cum 5:25
Since this is a retrieval task, the system assigns a relevance score to every
image in the database, and we sort the images from the most relevant to the least
relevant. The evaluation checks where the correct target images appear in this
ranked list.

For a single query, we use Average Precision. AP gives a high score when the
correct images appear near the top of the ranking. If they appear much lower in
the list, the score decreases.

We then calculate mean Average Precision by averaging the AP scores across all
queries.

However, the number of queries is not the same for every object instance. If we
averaged directly over all queries, the instances with more queries would have a
larger influence on the final result.

For this reason, our main metric is macro-mAP. We first average the query scores
within each object instance, and then average across all instances — so every
instance contributes equally.

## 7. Vision–language models: CLIP and SigLIP | 1:10 | cum 6:35
The main technical challenge is combining the information from the reference
image and the modification text. To represent both modalities, we use frozen,
pre-trained vision–language models: CLIP and SigLIP.

These models use a dual-encoder, or two-tower, architecture. One encoder
processes images, the other processes text, and both map their inputs into the
same embedding space. Because the representations share this space, we can
measure their semantic similarity using cosine similarity. An image receives a
high score when its embedding is close to the embedding of the corresponding
text.

The models are used completely frozen. We only extract their embeddings; we do
not update or fine-tune their parameters.

CLIP and SigLIP follow the same dual-encoder principle, but they differ in how
they are trained. CLIP uses a batch-level contrastive objective based on a
softmax: for each image, the matching text must be distinguished from the other
texts in the batch, and vice versa. SigLIP instead uses a pairwise sigmoid loss.
Each image–text pair is treated independently as either matching or non-matching.
This avoids the global softmax normalization and can scale more effectively to
large training batches.

We compare these frozen backbones to test whether the proposed method depends on
one particular vision–language model.

## 8. The baseline: BASIC | 1:10 | cum 7:45
The baseline for our work is BASIC, the zero-shot method introduced together with
the i-CIR benchmark.

BASIC processes the two parts of the composed query separately. The reference
image is encoded by the visual encoder, and the modification text by the text
encoder. The database images are also encoded in advance using the visual
encoder.

For every database image, BASIC computes two similarity scores. The first is the
visual similarity, which measures how similar the database image is to the
reference image. The second is the textual similarity, which measures how well
the database image matches the modification text. These are computed using the
dot product between the corresponding embeddings.

The two resulting scores are then multiplied. This multiplicative fusion acts
like a soft logical AND: a database image should receive a high final score only
if it matches both the reference image and the textual modification.

The method also includes several additional processing steps — centering, score
normalization, contextualization — which I will discuss later.

## 9. Limitation of the baseline — our proposal | 1:20 | cum 9:05
The main limitation of the baseline is that the reference image and the
modification text are never processed jointly.

The image branch only sees the reference image, while the text branch only sees
the modification. As a result, the model does not explicitly represent the
complete composed query.

To address this limitation, we introduce a third scoring branch based on a
generated target caption.

We provide both the reference image and the modification text simultaneously to a
multimodal large language model. We then ask the model to imagine that the
requested modification has been applied to the object in the reference image, and
to describe the resulting target image.

For example, in the chair query, the model receives the image of the specific
chair together with the text "placed around a table". It then generates a caption
such as: "White metallic chair with scrolled armrests placed around a table."

This caption contains information from both parts of the query: the visual
identity of the chair and the context specified by the text.

We then encode the generated caption using the same frozen text encoder and
compute its similarity with every image in the database. The final retrieval score
therefore combines three signals: similarity to the reference image, similarity to
the modification text, and similarity to the generated target caption.

## 10. The captioner: InternVL 3.5-8B | 0:45 | cum 9:50
For target-caption generation, we use the frozen eight-billion-parameter version
of InternVL 3.5.

We selected this model because it is an open-source multimodal large language
model that can jointly process images and text.

It also provides a practical balance between performance and computational cost.
Although it is much smaller than many larger multimodal models, it achieves
competitive results across a range of vision–language benchmarks.

Most importantly, we use it without any fine-tuning. It only receives the
reference image, the modification text, and our instruction to describe the
expected target image.

## 11. Designing the instruction | 0:45 | cum 10:35
An important part of the caption-generation stage is the instruction given to the
multimodal model.

The quality of the generated caption depends strongly on how the task is
formulated. For this reason, I carried out an extensive prompt-design process and
tested more than twenty different instructions.

I varied several elements, including the level of detail requested, the use of
examples, the order of the constraints, and restrictions intended to prevent the
model from introducing irrelevant information.

Based on these experiments, I selected five complementary prompting strategies.
Each strategy encourages the model to describe the imagined target from a slightly
different perspective, and together they produce a diverse set of candidate
captions.

## 12. Effect of the caption branch | 0:55 | cum 11:30
Here we can see that adding a single generated caption improves macro-mAP by
about 5.9 points, from 17.95 to 23.83. This suggests that the caption captures
useful compositional information that is not fully represented by the image and
text branches separately.

Using multiple captions improves the result further. We generate five captions
using different prompting strategies, average their embeddings, and use the
resulting representation for retrieval. This reduces the influence of
prompt-specific wording or irrelevant details, and emphasizes information that is
consistent across the captions.

With this five-caption average, macro-mAP reaches 25.41 — an improvement of about
7.5 points over the original image–text baseline.

> From this point on, all results use CLIP ViT-L/14 as the backbone, unless
> stated otherwise.

## 13. The pipeline | 1:20 | cum 12:50
To summarize the pipeline so far, each composed query contains a reference image
and a modification text. We also generate a caption describing the imagined target
image.

These three components are encoded using frozen, pre-trained vision–language
models and mapped into a shared embedding space. For every database image, we
compute three similarity scores: to the reference image, to the modification text,
and to the generated caption.

Now, how the scores are combined. Before combining them, we apply min-based
normalization so that the three branches are on comparable scales. Any negative
residual values are clamped to zero, meaning they provide no positive evidence for
the candidate image.

The normalized scores are combined multiplicatively, because the final result
should perform well across all branches at the same time.

We also use a Harris-inspired penalty. The idea comes from the Harris corner
detector, where a strong response in only one direction is not sufficient.
Similarly, a candidate should not receive a high score just because it matches one
branch very well while matching the others poorly. For example, an image may
contain the exact chair but not show it around a table, or it may show chairs
around a table but not the specific chair from the reference image. The Harris term
penalizes this imbalance, weighted by a hyperparameter lambda.

As a result, the final score favors candidates that receive consistently high
scores from the image, text, and caption branches.

> Harris response surface and formulas → backup 29.

## 14. Post-processing: centering and contextualisation | 1:10 | cum 14:00
Two additional processing techniques further improve the retrieval performance.

**Centering.** Vision–language embedding spaces often contain a large common
component shared by many embeddings. This component represents generic visual or
linguistic patterns rather than the distinctive information required for retrieval.
To reduce this effect, we compute a mean embedding for each modality using a
separate corpus, subtract it, and normalize again. The average image feature
reflects general visual patterns, while the average text feature captures common
linguistic patterns. Subtracting them helps isolate semantic content from
distributional bias.

It should not be understood as literally removing "the sky" from every image.
Instead, it removes directions in the embedding space that are common across many
samples, such as generic visual composition, background patterns, or broad dataset
biases.

**Contextualisation.** CLIP is trained primarily on natural-language captions and
full sentences. As a result, single-word text queries, such as "sculpture", or
sentence fragments, such as "during sunset", are out-of-distribution input and may
produce text features that are not well aligned with the image features. To address
this, we enrich the text query with additional terms from a subject corpus, adding a
random set of terms before — for example "dog during the sunset" — and after — for
example "sculpture dog" — the query. These composed phrases are embedded, centered,
and averaged, giving a more robust textual feature.

## 15. Adding the steps on top of each other | 0:40 | cum 14:40
Here we add each post-processing step cumulatively, for the baseline in blue and
for our caption pipeline in red.

The caption pipeline stays above the baseline along the entire ladder. Centering
gives a large jump for the baseline, and contextualisation gives the largest single
post-processing gain.

> If asked why the ladder stops here: two further BASIC steps — the contrastive
> projection and query expansion — do not help on this benchmark once the caption
> branch is present. Numbers → backup 24.

## 16. Does it transfer? Four frozen backbones | 0:55 | cum 15:35
We evaluate the pipeline with four frozen backbones, spanning two model families
and two capacity levels. CLIP ViT-L/14 is the backbone most commonly reported in
the zero-shot CIR literature, which makes our numbers comparable. CLIP ViT-H/14 is
the higher-capacity variant. SigLIP replaces the softmax contrastive loss with the
pairwise sigmoid loss — we use SigLIP ViT-L/16 and the more recent SigLIP2 g/16,
which is the best-aligned encoder of the four.

The caption branch improves every single one of them. The largest jump is on
SigLIP-Large, where macro-mAP roughly doubles, from twenty-one to forty-three.
SigLIP2 is the strongest base model.

This shows that our contribution does not depend on one particular vision–language
model.

## 17. Final results — SigLIP2 | 0:40 | cum 16:15
This is the best backbone, with the full ladder. The shape is the same as on
CLIP-L: the caption pipeline stays above the baseline throughout, and
contextualisation gives the final jump.

Our best configuration reaches 61.98 macro-mAP, against 57.69 for BASIC at the same
rung — and against 38.1 for the plain image-times-text product.

## 18. Our best overall system | 0:50 | cum 17:05
To state the final system plainly: the SigLIP2 backbone, the caption branch with
five averaged captions, and post-processing through centering and
contextualisation. Every component is frozen.

It reaches 61.98 macro-mAP and 62.07 mAP. Beyond mAP: the correct target is ranked
first for 71% of queries, and appears in the top ten for 95% of queries. Recall at
one hundred is 94%.

That high recall is important — I will come back to it in the future work.

## 19. Qualitative example — success | 0:30 | cum 17:35 (flex)
A qualitative example. The query is this Tintin drawing, with the modification "as
an iconic rooftop sign".

The plain image-times-text product already reaches 89% AP, but it mixes in generic
Tintin drawings that are not rooftop signs. Adding the generated caption pushes the
true rooftop-sign photographs to the top of the ranking: 98% AP.

## 20. Qualitative example — failure | 0:30 | cum 18:05 (flex)
And an honest failure, on the same instance: "as a human size statue".

Here the caption branch does not help. The generated caption describes the
character correctly, but the visual branch keeps pulling in drawings and figurines
rather than life-size statues.

This is the characteristic failure mode: when the modification demands a drastic
change of visual domain, the image branch dominates the product.

## 21. Limitations and future work | 0:50 | cum 18:55
Three limitations. The main cost is caption generation — about fifteen seconds per
query, which dominates online inference. The results also depend on prompt design:
averaging five captions mitigates this, but does not remove it. And the fixed,
unweighted product cannot adapt when one branch should matter more than the others.

Several directions follow naturally. A stronger or more efficient captioner — or a
single high-quality caption that matches the five-caption average without five
generations — would cut the main compute cost. The fixed product could be replaced
by a learned or weighted fusion of the three similarities, relaxing the zero-shot
constraint in exchange for accuracy.

Because recall is already high — the correct instance lands in the top-ranked
shortlist for the large majority of queries — a second-stage reranker that reorders
this shortlist is a promising direction: most of the remaining error is in the
ordering of candidates that are already retrieved. A text-conditioned reranker that
reorders by similarity to the target caption, rather than to the reference image, is
a natural candidate, since it keeps the modification in the loop at the reranking
stage.

Finally, the caption-as-third-modality idea is benchmark-agnostic and could be
evaluated beyond i-CIR — on category-level CIR benchmarks and other instance-level
retrieval settings.

## 22. Conclusions | 0:45 | cum 19:40
Four conclusions.

The caption is the single most effective component. Adding the target caption
improves every backbone on the full dataset, and in the component ablation it is
the largest single contributor — larger than feature centering, and far larger than
the remaining BASIC preprocessing.

A simple caption can replace elaborate preprocessing. A plain text-times-image
baseline plus the caption reaches the level of the fully tuned BASIC pipeline, and
with a strong backbone exceeds it. The textual signal is better supplied by an
explicit target description than by contextualising the bare modification phrase.

Centering and the caption are complementary. Their gains add up, and the best
configuration combines both.

SigLIP2 is the strongest backbone for the pipeline, reaching the thesis-best 61.98
macro-mAP — even though CLIP-H is stronger on the bare image–text baseline. The
backbone must be judged within the full pipeline.

## 23. Thank you | — | —
Thank you. I am happy to take questions.

## Q&A map | — | —
Full CLIP-L ablation, every rung (incl. projection and query expansion) →
**backup 24**. "The paper reports 34.35 for BASIC" → **backup 25** (our reproduction
gives 32.48; the gap is in the image branch, from re-extracting features in a newer
software stack; both methods are evaluated in the same environment, so the
comparisons hold). Latency breakdown → **backup 26**. The five instruction strategies
with their captions → **backup 27**. i-CIR distributions → **backup 28**. Min-norm,
clamping, Harris formulas and the response surface → **backup 29**.

Metric formulas are on slide 6; the pipeline (incl. fusion) on slide 13; the backbone
table on slide 16.
