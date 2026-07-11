# Defense notes — Imagining the Target
Asma Hoseinpour Siouki · MSc Data Science · University of Padova · July 2026
Target: ~20 minutes talk + Q&A. Time chips show budget per slide and cumulative time.
During Q&A: type a backup slide's number + Enter to jump to it directly.

## 1. Title | 0:20 | cum 0:20
Good morning, and thank you for being here. My thesis addresses a retrieval
problem: finding one specific object among three quarters of a million images,
when the query is an image together with a textual modification — and doing so
without training any model.

## 2. Composed Image Retrieval | 1:00 | cum 1:20
The task is called Composed Image Retrieval. The query has two parts — here, a
photograph of the harbour at Portofino and the sentence "as a painting". The
correct answer is this same harbour, rendered as a painting.

The two modalities are complementary: the image fixes the subject, the text
specifies its transformation. Neither alone expresses the information need — in
product search, "this bag, but in leather"; in an archive, "this building, at
night". That composition is what makes the task interesting and hard.

## 3. From categories to instances | 0:50 | cum 2:10
The literature mostly studies the category-level version: for "a cartoon character
on a t-shirt", any such t-shirt is correct. My thesis addresses the instance-level
version: "this character on a t-shirt" — and now, of the same three results, only
the Tintin shirt is correct. The retrieved object must preserve the identity of
the reference under changes of medium, material, and context. Category-level
methods have no mechanism for that identity constraint.

## 4. The i-CIR benchmark — query structure | 1:20 | cum 3:30
All experiments use i-CIR, a recent benchmark built for the instance-level task.
One instance, Tintin, illustrates the structure: one reference image, five
modification texts — five composed queries. The first row shows one ground truth
per query — note each query actually has several, between three and fourteen here.
The second row shows hard negatives, curated per instance: a statue of a different
character; another character's figurine with a dog, deliberately parallel to
Tintin and Snowy; a rooftop without the sign; other cartoon t-shirts. These
negatives satisfy one modality but not both, so single-modality shortcuts fail by
design.

## 5. The i-CIR benchmark — scale | 0:40 | cum 4:10
The scale: two hundred and two instances, one thousand eight hundred eighty-three
composed queries — median six per instance — and a database of seven hundred
fifty-two thousand images. The histograms show the distributions. The regime is
needle-in-a-haystack: the positives are a vanishing fraction of the database.

## 6. Problem formulation — zero-shot | 1:00 | cum 5:10
Formally: given the composed query, rank the entire database by a scoring
function conditioned on both the reference image and the modification text.

The central design decision is the zero-shot constraint. Supervised CIR methods —
combiner networks trained on labelled triplets — cannot be used here: such
triplets do not exist at the instance level, and every newly added object would
require new annotation. Zero-shot alternatives from the literature, such as
textual inversion, exist — but they target the category regime and do not
preserve instance identity. So the entire pipeline uses frozen pre-trained
models: no learned parameters, no fine-tuning, immediate generalization to
unseen instances.

## 7. Evaluation protocol | 1:00 | cum 6:10
The system returns a ranked list; average precision is the area under that list's
precision–recall curve — it is high exactly when the ground truths sit near the
top. Averaging over queries gives mean average precision. The primary metric is
the macro variant: queries are first averaged within each instance, then across
the two hundred and two instances, so a query-rich instance cannot dominate the
score. Every instance counts equally.

## 8. Vision–language models | 1:20 | cum 7:30
The building block for everything that follows: CLIP, a dual-encoder
vision–language model. Two networks — one for images, one for text — are trained
contrastively on four hundred million image–caption pairs: matching pairs are
pulled together in a shared vector space, mismatched pairs pushed apart.

The consequence is the property we exploit: the relevance between any image and
any sentence reduces to the cosine similarity of two vectors. The baseline
backbone throughout is CLIP ViT-L/14, used frozen.

## 9. The BASIC method | 1:20 | cum 8:50
The benchmark's zero-shot reference method — and my baseline — is BASIC. Every
database image receives two independent scores: a visual similarity to the
reference image, and a textual similarity to the modification. Each branch has
its own post-processing — I will return to the important steps — and the scores
are fused multiplicatively. The product implements a soft logical AND: a
candidate must satisfy both conditions, which is precisely what a composed query
demands.

## 10. Score normalisation and the Harris criterion | 1:00 | cum 9:50
Two technical details of the fusion matter. First, the raw branch scores live on
different scales, so each is min-normalised — the minimum is estimated once,
offline — and negative residuals are clamped to zero. Second, the product is
augmented with a penalty inspired by the Harris corner detector: it subtracts a
term that grows when one score dominates the other. Candidates that are excellent
in one modality but mediocre in the other — exactly the benchmark's curated
negatives — are suppressed, just as the corner detector suppresses responses
dominated by a single edge direction.

## 11. The structural limitation — and the proposal | 1:20 | cum 11:10
Here is the observation the thesis builds on. In BASIC, no component ever reads
the reference image and the modification text together. Both branches are
unimodal, so the composition — this object, under this transformation — is never
modelled. "As a painting" and "next to a painting" demand different targets, yet
each branch sees only its half of the query and cannot represent the difference.

The proposal: a multimodal large language model reads both query parts jointly
and generates a caption of the imagined target — hence the thesis title. That
caption is embedded with the same frozen text encoder and enters the fusion as a
third multiplicative branch: image times text times caption.

## 12. Target-caption generation | 1:10 | cum 12:20
The captioner is InternVL, an eight-billion-parameter open multimodal model, used
frozen. Conditioned on the reference image and the modification, it is instructed
to describe the target. The instruction matters: I designed five prompting
strategies — adaptive precision, constraint-priority, an anti-noise contract, a
slot-fill template, and draft-and-refine — which produce five distinct captions
per query, two of which you see here. The caption is embedded by the same text
encoder already in the pipeline, so the zero-shot property is fully preserved.

## 13. Effect of the caption branch | 0:50 | cum 13:10
Does it help? On CLIP ViT-L/14, raw products, before any post-processing: the
image-times-text baseline reaches 17.95 macro-mAP. Adding a single generated
caption: 23.83 — plus 5.9 points, a thirty-three percent relative improvement,
the largest single contribution in this work. Averaging the five instruction
variants: 25.41 — and the average outperforms every individual prompt, so no
prompt selection on the evaluation set is needed.

## 14. Post-processing I — centering | 1:00 | cum 14:10
Now the post-processing ladder, starting with centering. Embedding spaces of
these models are anisotropic: all embeddings share a large common component —
generic visual and linguistic statistics — which inflates every similarity score.
Centering subtracts a precomputed corpus mean and re-normalises, isolating the
distinctive part of each embedding. It is computed once, offline, and costs
nothing at query time.

The gains are large for the image-times-text duplet — almost ten points on
CLIP-L, almost twelve on SigLIP2. With the caption branch the gain shrinks, and
on SigLIP2 it even dips slightly at this rung — which is informative: the caption
already supplies part of the distinctive signal that centering is designed to
isolate. The two mechanisms overlap; they are not simply additive.

> If pressed on the SigLIP2 dip: −0.6 at this rung, recovered by the later
> rungs; the full ladder still peaks at 61.98 with centering included.

## 15. Post-processing II — contextualization | 0:50 | cum 15:00
The second important step addresses the text branch. The text encoder was trained
on full captions, so a terse fragment like "during sunset" is out-of-distribution.
Contextualization wraps the modification in object nouns — "dog during sunset",
"sunset dog" — embeds all variants, and averages them. It is the single largest
post-processing gain on every backbone: over ten points for the baseline on
SigLIP2, six for the caption pipeline.

## 16. The full ladder | 1:00 | cum 16:00
The complete picture on CLIP-L, adding one step at a time for both pipelines. The
caption pipeline stays above the baseline along the entire ladder. The last two
steps — semantic projection and query expansion — were tuned for raw CLIP
features; once the caption branch is present they consistently hurt, so the
proposed pipeline stops at contextualization. I would argue this selectivity is a
finding in itself: post-processing designed around one representation does not
automatically transfer to an enriched one.

## 17. Backbone study | 0:50 | cum 16:50
Is this a CLIP-specific effect? The same pipeline runs on four frozen dual
encoders. The caption branch improves every one of them; the most striking case
is SigLIP-Large, where macro-mAP doubles, from twenty-one to forty-three. SigLIP2
— the same dual-encoder family with a sigmoid contrastive objective and an
improved training recipe — is the strongest base model.

## 18. Final results — SigLIP2 | 1:10 | cum 18:00
The final configuration: SigLIP2, the five-caption average, and post-processing
up to contextualization. The ladder has the same shape as on CLIP-L — peak at
contextualization, projection and query expansion detrimental. The headline:
61.98 macro-mAP, fully zero-shot, against 57.69 for BASIC at its own best
configuration — a gap of four point three points that persists after all of
BASIC's post-processing.

## 19. Qualitative — success | 0:45 | cum 18:45 (flex)
Qualitatively: this pink pencil case, "without sticky paper notes but filled with
pens and markers". Image similarity alone retrieves lookalike cases; it cannot
read. The caption resolves the negation and the required content, and both ground
truths reach the top of the ranking — average precision goes from fifteen to one
hundred.

## 20. Qualitative — failure | 0:45 | cum 19:30 (flex)
And an honest failure: the mask of Agamemnon, "as a painting". The target is an
abstract painting, visually remote from the reference — and every pipeline,
including ours, returns real golden masks. When the modification demands a
drastic domain shift, the visual branch dominates the product. This is the
characteristic failure mode, and it motivates the future-work directions.

## 21. Limitations and future work | 0:40 | cum 20:10
Three limitations. Cost: caption generation takes about fifteen seconds per query
— over ninety-nine percent of online latency — so interactive use needs smaller
or quantised captioners. Fusion rigidity: a fixed product cannot down-weight the
visual branch when the text demands a domain shift; query-adaptive fusion is the
natural next step. And prompt sensitivity: averaging mitigates it, but does not
remove it.

## 22. Conclusions | 0:40 | cum 20:50
To conclude. A frozen, fully zero-shot pipeline can retrieve specific object
instances among seven hundred fifty-two thousand images from an image and a
sentence. The core contribution is letting a multimodal model imagine the target
and describe it — this supplies the joint image–text reading that dual-encoder
pipelines structurally lack, gives the largest single gain, and transfers to
every backbone tested. Combined with centering and contextualization — and the
discipline to drop what stops helping — the system reaches 61.98 macro-mAP, four
point three points above the strongest baseline configuration.

Thank you — I am happy to take questions.

## Q&A map | — | —
Full CLIP-L ablation incl. paper numbers → backup 23. "The paper reports 34.35"
→ backup 24 (reproduction 32.48; gap in the image branch, library versions;
comparisons unaffected — same environment for both methods). Latency breakdown →
backup 25. The five instruction strategies with example captions → backup 26.
Metric formulas are on slide 7; fusion details on slide 10.
