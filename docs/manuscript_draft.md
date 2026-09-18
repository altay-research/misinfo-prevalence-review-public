# Rare on screens but on everyone's mind: a systematic review of misinformation prevalence, exposure, and concentration



<!-- Working draft (adopted 2026-07-29). All numbers computed from the frozen dataset (1050 estimates / 444 studies; **v1.7.23**, MD5 in docs/FROZEN.md) by scripts/phaseB_*.{py,R}; count definitions in docs/counts_crosswalk.md. Internal provenance note — never rendered. -->

---

## Abstract

How much misinformation do people encounter? Published estimates range from a fraction of one percent to strong majorities. We systematically reviewed 443 studies reporting 1048 estimates of misinformation prevalence, exposure, sharing, and concentration. In behavioural studies, misinformation is a median 1.3% of what people consume online; it reaches 12.0% of people at least once and makes up 13.0% of what they share. In surveys, 57.7% say they have seen misinformation and 19.8% say they have shared it. In content analyses, 23.0% of items are classified as misinformation. How misinformation was identified (by fact-checkers, domain lists, researchers, or classifiers) and at which level (sources or items) explained more of the variance between estimates than what the study was about; platform and topic explained less. The top 1% of users account for a median 70% of misinformation sharing or exposure. These results help contextualize the diversity of misinformation estimates.



---

## 1. Introduction

Numerous studies have measured the prevalence of misinformation, and they have come to widely different conclusions. Some report that almost everyone believes they encounter false news (van der Meer & Hameleers 2025), others that a third of the content on a platform is misinformation (Vincent et al. 2025), or that misinformation is only a fraction of a percent of what people read (Allen et al. 2020). These numbers are widely cited and receive a lot of attention. They make headlines, inform policy, fuel academic debates, but they diverge by orders of magnitude.

Estimates of how much misinformation circulates matter because they set the size of the problem. They tell us whether misinformation is a marginal phenomenon or a common experience, which platforms and which topics carry most of it, and where action would make the most difference. Estimates also anchor the public debate, they are cited both to argue that misinformation is a crisis and to argue that the threat is overblown (Ecker et al. 2025; Budak et al. 2024). In this review we systematically collect the published estimates, describe what each one measures, and quantify how much of their divergence is explained by how they were produced. This should help readers interpret and contextualize existing numbers, and researchers construct meaningful and appropriate misinformation estimates.

There is great heterogeneity in how misinformation is defined and measured. In broad terms, researchers agree on the concept. In a survey of over 150 experts, most defined misinformation as false or misleading information, and distinguished it from disinformation, which is spread with the intent to deceive (Altay, Berriche, Heuer et al. 2023; Wardle & Derakhshan 2017). In practice, however, implementations differ widely, and many have noted that how misinformation is measured shapes what is found (Altay, Berriche & Acerbi 2023; Nickl et al. 2025). Studies count fabricated content, false content, misleading content, "fake news", junk news, or content from unreliable sources. They also identify it in different ways. Some judge individual claims or posts, using fact-checkers, expert coders, or classifiers, while others classify entire sources using lists of unreliable domains. Beyond definitions, the estimates also measure different quantities. They fall into six families, which we call constructs (Table 1). Five of the six are measured from observed data, either corpora of content or records of what people actually saw and shared; the sixth, self-reported recall, is measured from surveys and captures whether people think they encountered misinformation. The observed constructs also differ in their denominators, which range from a person's entire information diet to a single topic or platform.

**Table 1. The six constructs, with an example of each.**

| Construct | What the percentage is a share of | Example |
|---|---|---|
| Content prevalence | items (posts, videos, articles) that are misinformation, among all items sampled | "36% of the tweets in a Brazilian COVID-19 vaccine corpus were coded as misinformation" (Kim et al. 2023) |
| Audience exposure | a person's information diet that is misinformation | "unreliable websites accounted for 0.16% of French internet users' total connected time" (Cordonier & Brest 2021) |
| Reach | people who encountered misinformation at least once, from behavioural data | "44.3% of Americans visited at least one untrustworthy website during the 2016 campaign" (Guess, Nyhan & Reifler 2020); 26.2% in 2020 on the same design (Moore, Dahlke & Hancock 2023) |
| Self-reported recall | people who say they have encountered misinformation, from surveys | "73% of US respondents said they had read or heard at least one false claim about COVID-19 vaccines in the past six months" (Neely et al. 2022) |
| Sharing | sharing acts (retweets, reposts, links) that carry misinformation | "fake news sources made up 6.7% of the political links shared on Twitter during the 2016 US election" (Grinberg et al. 2019) |
| Concentration | misinformation exposure or sharing accounted for by a small group of users | "1% of Twitter users accounted for 80% of fake-news exposure" (Grinberg et al. 2019) |

These quantities can differ by orders of magnitude for the same object of study. Every estimate is a ratio: a numerator, the misinformation that was counted, over a denominator, the universe it is compared against. Holding the numerator fixed, the denominator can have a great influence on the estimate. For instance, the same fake-news articles were 1% of Americans' news consumption and 0.15% of their total media diet (Allen et al. 2020). Holding the denominator fixed, the numerator does the same: reanalysing the same Facebook engagement data, fake news rivals mainstream news under a broad list of fake-news outlets and becomes marginal under a narrow one (Rogers 2020; see also Watts, Rothschild & Mobius 2021).

Hameleers (2025) describes a persistent gap between low measured exposure and high perceived exposure to misinformation and attributes it partly to different definitions of misinformation held by the public, practitioners, and researchers. Yet, to date no systematic account exists of what the empirical literature actually measures, what numbers result, and why they diverge. Prior systematic reviews have catalogued prevalence within single domains, most notably health misinformation on social media (Suarez-Lledo & Alvarez-Galvez 2021), but no review covers these quantities together while coding the methodological choices (denominator, sampling, definition, platform, country) that move them. Recent methodological work has called for such a comparison (Nickl et al. 2025).

This review fills that gap. Following PRISMA 2020, we systematically identified, screened, and extracted quantitative estimates of the prevalence, exposure, consumption, real-world sharing, and concentration of misinformation, broadly construed (misinformation, disinformation, fake/false news, unreliable or untrustworthy sources, junk news; Wardle & Derakhshan 2017; Altay, Berriche & Acerbi 2023), across platforms, media, and countries. We classify every estimate into the six constructs and synthesize all 1048 estimates. We also document the denominators, including in grey-literature claims, some of which report no denominator at all (e.g., "millions of views").

Three results stand out. Misinformation is a small share of what people consume, on the order of a few percent. People report encountering it far more often than measurements find. And both exposure and sharing are concentrated among a small minority of users. These results hold across a variety of robustness checks (Supplementary Note A).

---

## 2. Results

<!-- All numbers computed deterministically from the frozen dataset (estimates_v1.7.23_frozen.csv, 1050 estimates / 444 studies) by scripts/phaseB_*. Internal provenance note — never rendered. -->

### 2.1 Description of the evidence base

The search and screening are summarised in the Methods. The 443 studies contribute 1048 estimates, 934 of which enter the primary analysis, as they describe the general public, not demographic subgroups (which we report separately). Coverage is uneven across the six constructs. Counted by studies contributing a usable proportion, most studies are content analyses (k = 274), with far fewer studies of self-reported recall (k = 91), observed sharing (k = 45), reach (k = 27), behavioural audience exposure (k = 18), and concentration (k = 19). Most studies are about health: of 443 studies, 178 concern non-COVID health topics, 103 COVID-19, and 20 non-COVID vaccines (67% health-adjacent), against 72 on general news and 58 on politics; climate misinformation represents a single estimate in the whole corpus. Geographically, a third of studies (134 of 443) include the United States, 120 of them as the only country studied, and 44% cover Western countries only. The evidence is also recent and concentrated on the pandemic: dating each study by when its data were collected, 314 of the 443 fall in 2020 or later, 185 of them in 2020 and 2021 alone, against 16 before 2016.

Which platforms are studied depends on what is being measured (Figure 1). Twitter/X appears in 29 of the 45 sharing studies and 13 of the 19 concentration studies, and browsing-panel data in 8 of the 18 exposure studies and 14 of the 27 reach studies. YouTube and TikTok run the other way: 67 and 50 of the 274 content analyses, against no more than 5 studies in any other construct. Topic and construct are entangled in the same way (Figure 2). Of the 274 content analyses, 153 concern non-COVID health topics and 62 COVID-19 against 17 on politics and elections; the other constructs run the other way, with general news accounting for 14 of the 18 exposure studies, 18 of the 27 reach studies and 9 of the 19 concentration studies, and politics and elections for 17 of the 45 sharing studies. What the field measures in corpora is mostly health misinformation, and what it measures in behavioural traces is mostly political and general news.

### 2.2 How studies define and identify misinformation

The studies define and identify misinformation in different ways. Counting each individual study once (by its most frequent coding when a study mixes several), 357 of the 439 studies (81%) identify misinformation at the level of individual claims or items, while 77 (18%) classify entire sources, counting for example every article from a domain listed as unreliable; the remaining five use idiosyncratic levels of their own.

Who decides what counts as misinformation also varies. In total, 248 studies (56%) rely on the researchers' own coding, 67 (15%) on lists of unreliable domains, 17 (4%) on fact-checker verdicts, 20 (5%) on automated classifiers, and in 87 studies (20%), all surveys, the respondents themselves decided what counted as misinformation.

How misinformation is identified covaries with which construct is measured. Content analyses almost always judge individual items, of the 274 content analyses, 255 identify misinformation at the claim or item level. The behavioural constructs almost always classify whole sources: whole-source classification accounts for 18 of the 18 exposure studies, 24 of the 27 reach studies, 34 of the 45 sharing studies and 16 of the 19 concentration studies.

Who supplies the ground truth covaries with the construct in the same way. Content analyses rely on the researchers' own coding (234 of the 274), whereas the behavioural constructs rely on domain lists. In recall surveys, respondents almost always decide (90 of 91). Supplementary Fig. 1 shows the full breakdown, and Supplementary Note A5 the counts.

The definitions also differ in how much they include. Twelve studies count only fabricated content, 185 count false content, and 155 extend to misleading content, while 87 studies (20%) state no per-item veracity standard at all. The studies without a per-item standard are, with few exceptions, the studies that classify whole sources.

### 2.3 The six constructs yield different numbers

As shown in Figure 3, the constructs yield systematically different numbers. Misinformation is a median 1.3% of the information diet in behavioural exposure studies [95% CI 0.6–2.8, k = 18]. It reaches 12.0% of people at least once [8.5–21.0, k = 27] and makes up 13.0% of what people share [7.5–16.9, k = 45]. In content studies, which collect a sample of posts, videos, or articles and rate each item, 23.0% of the items are classified as misinformation [19.1–25.8, k = 274]. In surveys, 57.7% of people say they have seen misinformation [53.3–63.8, k = 71] and 19.8% say they have shared it [14.1–26.6, k = 36]. Supplementary Table 1 gives each construct with its interquartile range and certainty rating.

The same ordering appears in the grey literature. We separately catalogued the quantitative claims published on the websites of fact-checkers, regulators, think tanks, advocacy organisations, and platforms, classified them with the same construct definitions, and verified each retained figure against the producer's own publication (Supplementary Note D). Of the 117 claims collected, 35 are misinformation-prevalence estimates. Recall claims have a median of 64.0% (n = 15, against 57.7% for the corpus's self-reported exposure recall), and one claim about self-reported sharing gives 23%. Keyword-built topical content samples have a median of 10.6% (n = 12, against 19.3% for the corpus's topical content estimates), and one whole-platform content claim gives 16%. Two sharing claims give 6.7% and 25%, one reach claim gives 3.5%, and two concentration claims give 65% of fake and conspiracy links for the top 10 sites and 89% for the top 50. The highest figures are self-reported perception measures here too.

Overall, heterogeneity is high within constructs. I² is 99–100%, and the 95% prediction intervals span most of the possible range (Content 0.83–86.0%, Exposure 0.18–10.5%). This holds under a ×10 variance-inflation check (I² stays at or above 90% in every construct).

Self-reported recall is hard to interpret without knowing what period the question asks about. Only 14 of the 71 seen-recall studies ask about a bounded period, and the estimates are similar whether the window is bounded or not (55.9% against 59.0%; Supplementary Note A4).

### 2.4 What drives the estimates?

We estimated how much of the variance between estimates each methodological choice explains (df-adjusted pseudo-R² from multilevel meta-regressions on 837 estimates from 419 studies, with cluster-robust tests). The two choices that explain the most both concern how misinformation was identified. The ground-truth source, that is who decided what counts as misinformation (fact-checkers, domain lists, researchers, or a classifier), explains 22.8% of the variance. The identification level, whether misinformation was identified at the source or claim and post level, explains 21.8%. These two covary: source-level estimates use a domain list in 95% of cases, and claim-level estimates a fact-checker, classifier or human coder in 87%. They capture one underlying dimension, how loosely misinformation was defined. Each share is estimated in its own model, so two moderators that encode nearly the same choice each explain much of the same variance; adding them would count it twice. We therefore read them as one family worth about a fifth of the variance, not as two worth two fifths (Supplementary Note B2).

What the study measures comes next: the construct, which of the six quantities a study reports, explains 19.1% of the variance. Then the denominator class, what that percentage is a share of (16.6%), and the measurement type, whether the study used behavioural data, coded content, or self-report (16.6%), which groups the constructs and so overlaps with them by construction. The platform studied (14.1%), the sampling frame, how the content or the people were sampled (12.7%), and the breadth of the definition, whether it stops at fabricated content or extends to misleading content (12.0%), also explained a significant portion of the variance. The study's topic explains the least by far, 1.8%. These shares carry wide uncertainty and the leading moderators' intervals overlap, so their ordering should not be read as a ranking (Supplementary Note B2). In short, how a study identifies misinformation explains far more than what the study is about.

Figure 4 plots the median prevalence estimate across studies for each methodological choice. Studies based on behavioural traces find a median of 12.5%, studies coding content 23.0%, and studies based on self-report 43.0% (k = 446 studies across the three levels); the same gradient appears for the sampling frame (behavioural panels lowest, survey samples highest), the ground-truth source (domain lists lowest, self-report highest), the construct, and the identification level (source-level lower than claim-level). Holding the other moderators fixed in the meta-regression compresses but preserves the gradient, with predicted prevalences of 7.3% for behavioural traces, 16.6% for content coding, and 44.7% for self-report (Supplementary Note B2 reports every moderator with its interval).

Wider definitions produce higher estimates within the content analyses. Content studies that count only fabricated content report a median of 3.5%, those that count false content 21.5%, and those that also count misleading content 27.0%. How much misinformation a study finds therefore depends, in part, on where its definition draws the line. Outside the content analyses the same gradient cannot be read, because the studies that measure misinformation behaviourally classify whole sources and mostly state no per-item standard at all. The denominator matters too, but only when it is described precisely. A simple binary distinction (whole-diet versus narrower) explains almost none of the variance (0.0%, *p* = .259), while the full set of denominator categories explains 16.6% of the variance.

Larger studies report somewhat lower estimates. The rank correlation between a study's sample size and its estimate is negative within every construct (ρ between −.14 and −.57), and its interval excludes zero for Content (ρ = −.34 [95% CI −.44, −.23], *t*(269) = −5.93, *p* < .001, k = 271) and Reach (ρ = −.57 [−.78, −.23], *t*(25) = −3.43, *p* = .002, k = 27). Weighting studies by sample size lowers every construct's median except self-reported recall, which rises (Supplementary Note A6).

### 2.5 Concentration of exposure and sharing

Exposure to and sharing of misinformation are highly concentrated in a small group of users. Of the 19 concentration studies, 18 report how much of the total misinformation activity (visits, shares, or exposures) is accounted for by the most active users and one reports concentration across sources only. We standardised the 28 user-level concentration estimates to a common form: the share of all misinformation activity accounted for by the top X% of users. Ten studies report a figure for the top 1% of users or smaller. Five give exactly the top 1%, with a study-level median of 70% (Figure 5). Six give smaller groups still, from 0.001% to 0.3% of users, with shares of 24% to 81%. One study appears in both sets, and across all ten the study-level median is 62.4%. Studies of broader top groups report similar shares: 80.0% of misinformation activity for the top 15–35% of users (5 studies) and 81.0% for the top 5–15% (4 studies). These bands come from different studies, so they do not form the single rising curve that a within-study breakdown by threshold would.

Concentration also appears at the level of sources. Five estimates describe how misinformation activity distributes across sources rather than users: 5% of fake-news sources accounted for more than half of all fake-news exposures on Twitter in the United States (Grinberg et al. 2019), the ten most active sources for over 95% of low-credibility tweets in an Italian sample (Pierri, Artoni & Ceri 2020), the three most visited untrustworthy domains for about half of untrustworthy-news visits in Germany (Oswald & Munzert 2026), and a single organisation for roughly 18% of all tweets linking to low-credibility sources in an English-language vaccine sample (Pierri et al. 2023).

### 2.6 Who is exposed: demographic subgroups

Only 25 of the 443 included studies report estimates broken down by demographic group, contributing 104 estimates, and among the 62 studies whose measurement type is behavioural, only 13 do.

Of the 104 subgroup estimates, 71 split respondents by party, vote or ideology, against 19 by age, 8 by gender, 3 by education, 2 by the office a politician holds and 1 by community. Where a study reports both sides of a political contrast, the right-leaning group is usually higher. Eighteen studies report a partisan split, and eight of them give both sides on the same measure. Across those eight, the right-leaning group's figure is a median 3.73× the left-leaning group's, ranging from 0.48× to 41.7×, and one study reverses the direction. Four studies allow an age contrast between their oldest and youngest groups, giving six contrasts: three in which older users are higher (1.8×, 4.35× and 18.5×) and three in which they are lower (0.58×, 0.67× and 0.70×). These ratios are computed within studies, so they are not confounded by differences in measurement between studies.

### 2.7 Robustness

We probed these results in several ways (Supplementary Note A). We re-computed the construct medians excluding high-risk-of-bias studies, excluding abstract-only appraisals, weighting by sample size, folding quality ratings into content prevalence, re-computing the heterogeneity under a tenfold variance inflation, and miscoding a share of the construct assignments. The construct gaps survive every check except reach against sharing, whose medians differ by one point and are not separable under any of them. Two deserve mention here. Some studies rate the quality of health content (for example with DISCERN scores) rather than its truth. Treating those quality ratings as misinformation moves the content median only from 23.0% to 23.3%. And the gaps between constructs are stable across 2005–2026. Risk of bias was appraised for all 443 studies with a validated prevalence instrument (Hoy et al. 2012); because the instrument's two design items turn out to closely restate this review's own denominator and definition taxonomy, we report the appraisal descriptively in Supplementary Note A1 rather than as an independent verdict on the literature. Finally, rating the certainty of the evidence with GRADE (Guyatt et al. 2008), the constructs with the lowest estimates carry the highest certainty (MODERATE for exposure, reach, recall, concentration, and sharing) and content prevalence the lowest (VERY LOW).

---

## 3. Discussion

This article sheds light on how much misinformation people encounter, share, and report encountering. We systematically collected the published quantitative estimates of misinformation prevalence, exposure, sharing, and concentration, coded what each estimate measures, and estimated how much of the variance between estimates each methodological choice explains. We found that measured exposure to misinformation is low (a median 1.3% of what people consume online), that self-reported exposure is a majority experience (57.7%), and that content analyses of mostly topical samples fall in between (23.0% of items).

Hameleers (2025) asks how low measured exposure and high perceived exposure can be reconciled. Our synthesis suggests that the two literatures measure different things rather than contradicting each other. Surveys ask people whether they think they encountered misinformation. That judgment is made without a definition, without verification, and under intense media coverage of misinformation, which some scholars argue has exaggerated the threat (Carlson 2020; Stecula 2025). Behavioural studies measure what actually crossed people's screens, but almost all of them come from browsing panels and Twitter/X, where content is link-based and lists of unreliable domains can be applied. Behavioural exposure on video and messaging platforms such as YouTube, TikTok, WhatsApp, and Telegram remains essentially unmeasured.

Whether people over-perceive their own exposure cannot be settled by our review, as it would require panels that carry both measures for the same respondents, and no study in this corpus does. The wider literature on logged versus self-reported media use finds the two correlate only moderately (r = .38), with no consistent inflation in either direction (Parry et al. 2021), so the discrepancy could be a validity problem rather than clear evidence of over-report.

One objection to the low behavioural figures is that a narrow, falsity-based definition is what makes misinformation look rare (Ecker et al. 2025). Two things in our results speak to it, and they point in opposite directions. Within the content analyses, wider definitions do produce higher estimates, which is the objection's mechanism. But the behavioural literature is not where a narrow criterion operates: of the 81 studies contributing an estimate in a behavioural construct, 63 classify whole sources. A source list is loose inside the domains it names, counting everything they publish, and narrow across everything else. Studies that sample content from list-flagged sources and judge each item find that outright falsity is the exception: 1.7% of stories drawn from 46 sites on a fake-news list were completely false, and 11.8% mostly or completely false, while 43.5% departed from fact in some way (Mourão & Robertson 2019). Widen the verdict to false or misleading and the same instrument returns a majority, from just under 55% to about 76% across four studies (Allcott & Gentzkow 2017; Tai, Lin & Desmarais 2026; Shao et al. 2018; Pierri et al. 2023). Narrow it to what a professional fact-checker has actually adjudicated and it falls to 5%, because 95% of flagged material is never fact-checked at all (Wirtschafter et al. 2024). Read against outright falsity, then, a source list is loose: most of what it flags is not completely false, and only a small fraction is. What it captures reliably is material that departs from fact in some way. How high the resulting figure is depends largely on the standard applied to what the list flags, which is the dependence on measurement choices that this review finds everywhere else (Supplementary Note E).

These findings have implications for interventions against misinformation. First, if the measured problem is a few percent of the diet while the perceived problem is a majority experience, interventions calibrated to perception may be calibrated to the wrong quantity. Perceived prevalence predicts distrust of information across countries (Matthes et al. 2023; Boulianne & Humprecht 2023), media attention to misinformation can itself undermine trust in reliable sources (Hoes et al. 2025), and such distrust appears to be at least partly a symptom of broader institutional distrust rather than its cause (Altay & Mercier 2026; Tay, Lewandowsky et al. 2024). Second, our results help interpret the experimental literature. Forced-exposure experiments, in which participants are shown misinformation and asked whether they would believe or share it, report far higher rates than the observed sharing (13.0%) and behavioural exposure (1.3%) reported here, though we did not review that literature systematically and so do not put a figure on the gap. Experimental effect sizes are conditional on contact with misinformation, and in the wild that contact is rare (Altay, Berriche & Acerbi 2023; Berriche & Altay 2020), so they should not be read as unconditional estimates. Establishing what misinformation does at these low base rates requires causal-inference designs the field still largely lacks (Tay, Hurlstone et al. 2024). Third, exposure and sharing are concentrated in a very small group of users: the top 1% account for a median 70%. Misinformation looks less like a population-wide phenomenon than like the behaviour of a small minority. This conclusion rests on 19 studies, and concentration deserves far more research attention than it has received. Similarly, few studies have reported clear demographic breakdowns of misinformation exposure.

Which construct should researchers, journalists, and policymakers use? The six constructs answer different questions, and we see them as complementary rather than competing. A content analysis of vaccine posts after an outbreak describes the informational supply on a platform and can be produced quickly, but it cannot say what people saw; its number describes the sample, and belongs with the sampling procedure in the headline. A behavioural exposure or reach estimate answers the question most public concern is about, what people actually encountered, but it requires platform or panel data that are often unavailable. No study in this corpus produces one for TikTok, and only a handful do for YouTube, WhatsApp and Telegram. A recall survey is the cheapest to field and the only construct available in most countries, but it measures perception, which is informative about trust and concern rather than contact. Concentration estimates identify where interventions would act, on a small group of accounts rather than on the whole population. In practice we suggest matching the construct to the claim. Claims about what circulates need content analyses with stated denominators, claims about what people encounter need behavioural data, and claims about perceived exposure need surveys.

Four reporting practices could help prevent some of the problems this review documents, in the grey literature especially (Supplementary Note D). First, name the denominator, in words, in the abstract, for example "X% of first-page search results for vaccine queries" rather than "X% of content". Second, when the denominator was built by a selection procedure (top-N, most-shared, engagement-ranked), say so whenever the percentage is reported. Rank-truncated corpora, samples restricted to the most-viewed items, were the single most common coding error in our own pipeline, and the studies we reviewed have the same problem. Abstracts in this corpus often headline a percentage without saying how the sample was selected, so the number travels without its denominator (Supplementary Note A7). Third, report absolute counts only alongside a rate: a "million views" claim without a base is a count, not a rate, and cannot support a prevalence claim. Fourth, when measuring perception through survey recall, say so. Perception is a legitimate construct about beliefs rather than a measurement of exposure, and headlines that present one as the other create the gap described above.

Four limitations qualify the synthesis. First, the review is English-only, a documented bias whose direction is unknown. Second, the pipeline was AI-assisted at every stage, from screening to extraction and risk-of-bias appraisal. No AI-assisted pipeline is error-free, but this one is transparent and has been validated and audited repeatedly. Screening was validated against a gold set, a blind re-screen of 300 exclusions, a re-screen under a second prompt, and a human re-screen of 310 records by two coders. Extraction was checked by a second pass of the same model, by a different model family reading the whole corpus blind, by a full blind re-extraction of every study, and by two human coders; every disagreement was adjudicated against the source paper by the author, and the corrections these checks forced are listed in §4.8 and Supplementary Note B. Third, the meta-regression's sampling-variance model assumes independent draws that the large behavioural studies violate, so we lean on medians and report the model as variance explained only. Fourth, the review was not prospectively registered; every analytic decision is instead recorded, with its rationale and a timestamp, in an append-only research log that is released with the data. Supplementary Note B3 discusses each limitation in full.

How much misinformation is out there? The question has no single answer, because each estimate is the product of what was counted as misinformation and what it was compared against. Measured exposure, identified mostly at the level of unreliable sources rather than misleading claims, is low and concentrated, in line with a growing body of work (Pennycook & Rand 2026; Altay 2026; Budak et al. 2024). What this review adds is an account of why the field's numbers disagree so widely. These results do not settle the debate about harm. Misleading-but-true content falls outside every falsity denominator and may carry the larger aggregate harm (Allen, Watts & Rand 2024), and effects on trust and on the information environment do not require anyone to be duped (Van Doorn 2023). Whether one considers misinformation a pressing threat (Ecker et al. 2025) or an overblown one (Budak et al. 2024; Williams 2026), progress requires the same thing from the measurement literature: numbers whose denominators are stated, and that match the claims built on them.

## 4. Methods

### 4.1 Protocol and reporting

We followed PRISMA 2020 (Page et al. 2021); the flow of records is shown in Figure 6. The review was not registered and no protocol was published in advance. Instead, an append-only, version-controlled research log records each analytic decision, its rationale and every deviation, with commit timestamps, and serves as the protocol record (Supplementary Note B3). Every database query is a parameterised, version-controlled script, search snapshots are dated and frozen, and the complete pipeline (scripts, data, decisions) is in a git repository (see Data and code availability), so all reported numbers regenerate from the released dataset. Most of title screening ran on Claude Sonnet-class models; the screening validation batches, every adjudication of a disputed screen, and all of extraction, construct coding and risk-of-bias appraisal ran on Claude Opus-class models (Anthropic), with one same-family quality pass on Claude Fable. They operated as in-session agents whose instructions are preserved in the repository. Because the agents ran inside interactive sessions, their sampling parameters cannot be pinned, and the upstream coding steps are not deterministic.

### 4.2 Eligibility criteria

We included empirical studies reporting a quantitative estimate, with a denominator, of any of the six constructs this review analyses: content prevalence, audience exposure or consumption, reach, observed real-world sharing, self-reported recall of having encountered or shared misinformation, and the concentration of any of these. The construct is set by the denominator, what the percentage is a share of, not by the topic or the wording of the numerator. Studies qualify on any platform or medium (online and traditional), in any country, at any date. Preprints were eligible, enter the main analysis, and are flagged as such.

We excluded correction and intervention experiments, studies of belief in or susceptibility to misinformation (a distinct construct our search was not designed to capture), detection and classification algorithm papers, purely theoretical or commentary pieces, and experimental sharing (e.g., “how likely would you be to share”). Only English-language reports were included. The restriction is on the language of the report, not of what it studies: the corpus covers 66 countries, most of them not anglophone, and many of its studies code non-English content. Grey literature surfaced by the systematic search was screened under the same criteria; grey-literature claims collected outside the search were handled in a separate track that is never pooled with the corpus.

### 4.3 Information sources

We searched five streams, all frozen and dated, yielding 30,958 database records plus a citation-searching arm (Figure 6). Scopus was the primary database (searched 2026-06-20), queried with a broad Boolean string combining misinformation terms with measurement terms and deliberately favouring recall (Supplementary Note C). It was validated against a 16-study seed set (recovering 14 of 16, 87.5%, Wilson 95% CI 64–97%) and yielded 20,344 records. OpenAlex keyword search and PubMed (2026-06-24) added 4,822 and 410 net-new records. A fifth stream was added in September 2026, after the analysis of the June corpus showed how thin the behavioural cells were: an OpenAlex query crossing the same topic terms with the terms by which behavioural studies describe their data (web tracking, clickstream, digital trace, donated data, passive metering and so on) rather than with outcome terms, run 2026-09-07. Studies built on browsing panels and donated data often frame their subject as news quality rather than misinformation, so a topic-and-outcome string under-catches them. It returned 6,972 records, 5,382 of them new to the review; 4,883 unique records were screened at title, 562 went to abstract adjudication, 188 to full-text retrieval, 89 were assessed, and 19 studies entered the dataset. OpenAlex citation snowballing, backward and forward from 224 audience-side core studies, plus a targeted venue sweep, screened 1,818 candidate records and contributed 331 advancing to full-text retrieval, reported as PRISMA's "other methods" arm. Two further queries probed the recall of the searches rather than adding a stream, and are not part of the records in the PRISMA flow: a concentration-focused Scopus query (497 results, 2026-06-21) and a hand-run Google Scholar check of self-reported recall (2026-09-04, five queries), which surfaced five studies that are in the dataset and are reported as such. In total, 66 of 443 included studies (14.9%) came from outside Scopus, mostly in journals Scopus does index, so the residual gap lies in query recall rather than in database coverage.

Separately, we catalogued the quantitative claims that circulate on the websites of four kinds of producer (fact-checkers and monitors; regulators and intergovernmental organisations; academic centres and think tanks; advocacy organisations and platform transparency reports), recording every quantitative claim about the amount of misinformation with its verbatim figure, denominator, method, and access date, 117 claims in total. Each claim was classified as a usable prevalence estimate, coded on the corpus construct grid, or into one of seven exclusion categories, and every retained estimate was verified against the producer's own publication in August 2026. This track is never pooled with the corpus, its protocol and results are in Supplementary Note D.

### 4.4 Screening

Title screening was performed by an LLM screener under a recall-protective rule (uncertain records advanced as "maybe"), in independent batches. Records advancing to full text were retrieved from open-access sources and institutional library access; 145 advancing records were never retrieved (Figure 6). Every provisional include was then read a second time by an adversarial LLM pass, with disputed cases resolved by a third. Four checks bound the screening error. The protocol was validated against a 40-title gold set (97.5% agreement; all nine known positives recovered). A random 300-record sample of exclusions was re-screened blind, with no missed include (one-sided 95% upper bound 1.0%). A 90-record subsample was screened twice under different prompts (Cohen's κ = 0.89). And after the dataset was frozen, two human coders, the author and a research assistant blind to the pipeline's decisions, independently re-screened a blinded sample drawn at each stage, 200 titles, 60 abstracts and 50 full texts, with every disagreement adjudicated against the record (Table 2; Supplementary Note B1).

That human check found no missed study among 150 title-stage exclusions (upper bound 2.0%) and
two among 40 abstract-stage exclusions (upper bound 14.9%), and it exposed a defect in the
written criteria (regarding the recall construct). This led to a re-screen of every title-stage
and abstract-stage exclusion by two independent model families working blind, with the union of
their flags adjudicated (Supplementary Note B1).

### 4.5 Data extraction

The unit of analysis is the estimate: a study reporting figures for four countries on two platforms contributes eight rows, keyed by study, country, platform or source, and measure. Each estimate was extracted from the full text (or from the abstract where no full text could be obtained, yielding only the headline figure) and coded for value, denominator, platform, country, sample size, and misinformation definition. Every candidate estimate was then re-extracted by a second LLM pass and reconciled. Unsupported values, including figures that were secondary citations of other studies, were dropped and discrepant values corrected; in the full double-extraction round, 98 of the 793 estimates re-extracted were dropped on these grounds. The final dataset comprises 1050 estimates from 444 studies, of which 934 are proportion, non-subgroup rows; the six analysed prevalence constructs draw on 897 of these. Quality-scale scores, per-capita intensity counts, and per-item ranges are retained but never pooled. Counts and their definitions are fixed in a crosswalk in the repository, and an automated check fails if any document contradicts them.

### 4.6 Construct taxonomy and the falsity–quality rule

Each estimate was classified into one construct: Content (share of items that are false), Exposure (behavioural share of a person's actual diet, visits or time), Reach (share of people who encountered misinformation at least once, measured behaviourally), Sharing (observed sharing, or the share of an actor's output), Recall (share of people who say they encountered or shared it), and Concentration (the share of activity attributable to the top X% of users or sources), or the excluded categories Quality and Other.

A pre-specified rule governed the hardest boundary. An estimate counts as Content only if it judges verifiable truth or falsity against an external ground truth (fact-check verdicts, expert-verified false claims, a validated unreliable-source list). Ratings of usefulness, completeness, reliability, overall quality, or guideline adherence, which are common in health-content studies, were coded Quality and excluded from prevalence, because in these studies low-quality items are not necessarily labeled as misinformation by the authors. Ambiguous cases were flagged for a sensitivity analysis. Inter-coder reliability on the full construct classification was κ = 0.82 between two passes of the same model.

### 4.7 Risk of bias

All 443 included studies were appraised with an adaptation of the Hoy et al. (2012) prevalence risk-of-bias tool, read from full text for 418 (94%) and from abstracts for the remainder. Hoy was chosen over a bespoke scheme because two of its ten items are this review's subject: item 10 asks whether the numerator and denominator are appropriate, and item 6 whether an acceptable case definition was used. Every rating on those two items required a verbatim supporting quote. As applied, the two design items closely restate the review's own denominator and definition coding, so we treat them as external correspondence with a validated instrument rather than as independent evidence about individual studies.

The summary rating is pre-specified and weights those two items (LOW = 0–2 items at high risk with items 6 and 10 both low; MODERATE = 3–5, or one of 6 and 10 high; HIGH = 6 or more, or both 6 and 10 high). Because weighting the two thesis-relevant items could make the bias–magnitude result circular, a sensitivity analysis recomputes the summary rating as an unweighted count over the eight remaining items (Supplementary Note A1). Sample size is not treated as a bias item, because it conflates precision with bias; it is handled by the precision-weighting analysis. Because the instrument treats unclear items as high risk, abstract-appraised studies are pushed toward HIGH by missing information rather than demonstrated bias, and a full-text-only sensitivity analysis is reported (Supplementary Note A2).

### 4.8 Reliability, and its limits

The pipeline was AI-assisted at every stage, so we checked it at every stage, and Table 2 lists every check with its sample and its result. The checks are of four kinds, and they do not measure the same thing. Two passes of the same model family (screening κ = 0.89, construct classification κ = 0.82 on 778 double-extracted rows, risk-of-bias PABAK = 0.78) measure reproducibility. A different model family reading the corpus blind (GPT-5.6 against a pipeline built on Claude models) measures agreement with a coder that does not share the pipeline's systematic errors: it recoded 647 estimates across 306 of the 315 studies the corpus then held, and the seven estimates in the two studies that entered after that sweep (construct κ = 0.80, denominator scope κ = 0.72), and the 468 rows the repair had added when the check ran (construct κ = 0.77, 85.0% raw agreement), and in a second mode checked our value, denominator and construct for each repair row against the paper, confirming 83.1% outright and sending the rest to adjudication. Every study was then re-extracted from its full text by fresh agents with no sight of the frozen coding, in 57 batches covering the whole corpus as it then stood: the blind pass agreed on eligibility for 430 of 456 studies, reproduced 712 of the 837 main-pool values, and proposed 202 candidate omissions across 123 studies. A seeded random 10% had been re-extracted the same way earlier and agrees with it. Finally, two human coders, the author and a research assistant blind to the pipeline, coded blinded samples at screening and at extraction (Table 2), and the author adjudicated every contested coding against the source paper; no model verdict was ever applied automatically.

The corrections each check forced, the agreement statistics and their decomposition, and a record of which rulings were made by the author and which were proposed by the AI assistant and approved by him, are in Supplementary Note B1.

**Table 2. Reliability and validation checks, by stage.** Same-model checks measure reproducibility; the independent-model and human checks measure agreement with a coder that cannot share the pipeline's systematic errors.

| Stage | Check | Compared against | Sample | Result | What changed |
|---|---|---|---|---|---|
| Title screening | Gold set | 40 curated titles | 40 | 97.5% agreement; all 9 positives recovered | — |
| Title screening | Blind re-screen | Same model | 300 exclusions | 0 misses (upper bound 1.0%) | — |
| Title screening | Cross-prompt re-screen | Same model | 90 records | κ = 0.89 | — |
| Title screening | Human re-screen | Two coders, adjudicated | 200 titles (150 exclusions) | 0 genuine misses of 150 (upper bound 2.0%) | — |
| Abstract screening | Human re-screen | Two coders, adjudicated | 60 abstracts (40 exclusions) | 2 misses of 40 (upper bound 14.9%) | Both studies added |
| Full-text eligibility | Human re-screen | Two coders, adjudicated | 50 studies | Pipeline upheld in all 20 contested cases | — |
| Screening criteria | Corrected-criteria re-screen | Two model families, blind, adjudicated | all title- and abstract-stage exclusions | 208 studies recovered and confirmed at full text | Corpus repaired (§4.4) |
| Repair extraction | Independent cross-check, blind | Different model family (GPT-5.6-luna) | 468 rows / 148 studies (the repair as it stood when the check ran; 131 are in the released dataset) | construct κ = 0.77, 85.0% agreement | 23 rows re-ruled by the author |
| Repair extraction | Independent cross-check, fact-check mode | Different model family, our coding shown | 468 rows | 83.1% confirmed outright | 14 rows removed |
| Repair extraction | Blind re-extraction, pilot | Fresh agents, seeded random sample | 14 of 141 studies | eligibility 14/14; 94% of rows reproduced; 1 omission (a duplicate pooled figure) | — |
| Extraction | Double extraction | Same model | 778 rows | Construct κ = 0.82 | Discrepant values corrected |
| Extraction | Blind re-extraction, whole corpus | Fresh agents, separate sessions, no sight of the frozen coding | all 456 studies as the corpus then stood | 430 of 456 eligibility agreements; 712 of 837 main-pool values reproduced (85.1%); construct κ = 0.89, ground truth κ = 0.92, breadth κ = 0.76 | 26 eligibility disputes, 125 unreproduced values and 202 candidate omissions adjudicated against the papers |
| Extraction | Blind re-extraction, pilot | Fresh agents, seeded random sample | 33 of 283 studies | 90% of findings, 94% of constructs reproduced | — |
| Extraction | Independent model, July sweep | Different model family, blind | 626 estimates | Construct κ = 0.75 (raw 0.82); breadth 0.69; denominator class 0.53 | 53 rows recoded after source adjudication |
| Extraction | Independent model, released freeze | Different model family, blind | 647 estimates | Construct κ = 0.80 (0.82 scored against the released freeze); denominator scope 0.72; breadth 0.48 | — |
| Extraction | Independent model, coverage completion | Different model family, blind | 7 estimates in the 2 studies that entered after the sweep | All 7 values, constructs and denominators agree; no omission, no extra | — |
| Extraction | Independent model, coverage completion | Different model family, blind | 38 estimates in the 22 studies no earlier pass had read | Construct κ = 0.96 (37 of 38); breadth 23 of 26; denominator class 7 of 17 | 1 breadth code adopted |
| Extraction | Human coders | Author and research assistant | 48 items in three deliveries (24 sentence-level, 24 full-paper) | Denominator κ = 0.84 and construct κ = 0.60 from full papers; construct κ = 0.48 from sentences | 2 denominators recoded; 3 fraudulent papers removed |
| Risk of bias | Double appraisal | Same model | All studies | PABAK = 0.78 | — |
| Grey literature | Blind recode | Author | 30 claims (21 scoreable) | Curation upheld in 11 of 14 disagreements | 1 construct corrected |

### 4.9 Synthesis and statistical analysis

Primary analyses use a pre-specified main-analysis set of proportion, non-demographic-subgroup estimates (934 in total). The six prevalence constructs are computed on 897 of these; Quality and Other rows are retained in the file but never pooled into any prevalence figure. Because one study can contribute many estimates, the primary summary is the study-level median: the median of a study's estimates, then the median across studies. Each median carries a 95% confidence interval from a study-cluster bootstrap (2,000 resamples, fixed seed), resampling studies rather than estimates so that within-study dependence is respected. We report the interquartile range alongside, which is spread across studies rather than uncertainty about the median. We do not pool with an inverse-variance or double-arcsine model (Barendregt et al. 2013): pooling assumes the estimates target a common quantity, which this review argues they do not. In the smallest cell (the k = 5 top-1% concentration set) percentile-bootstrap intervals can under-cover, so we read that interval as descriptive.

Per construct we fit a random-effects model (DerSimonian–Laird on logit-transformed proportions) and report I², τ², and a 95% prediction interval, the interval a new study would be expected to fall in. To quantify how much each methodological choice explains, we fit multilevel meta-regressions to logit-transformed proportions with estimates nested in studies and cluster-robust inference, and report degrees-of-freedom-adjusted pseudo-R² with study-cluster bootstrap intervals. The modelling choices and sensitivities are described in Supplementary Note B2. Software: Python 3 for data preparation and bootstrapping, R 4.3 with metafor (Viechtbauer 2010) for the meta-regression.

### 4.10 Statements

Acknowledgements: we thank Laura Hitz for her independent coding.

Funding: this project received funding from the University of Zurich, as a UZH Postdoc Grant, grant no. FK-25-078. Competing interests: the author declares no competing interests. Ethics: not applicable (no human participants; synthesis of published studies).

Use of AI: generative AI (Claude Opus 4.8, Opus 5, and Fable 5.1, Anthropic, 2026, accessed through Claude Code) was used extensively as a research assistant, and its role is reported in Methods and Supplementary Note B1. AI agents screened the records, extracted and coded the estimates, appraised risk of bias. Generative AI also helped writing the analysis code, producing the figures, checking the statistics reported in the text against the underlying data, and improving the readability of the text. All research questions, eligibility criteria, coding rules, methodological decisions, interpretations, and conclusions are the author's own. The author designed and supervised every step, adjudicated every contested screening and coding decision against the source, and reviewed every AI-assisted output, including all code, statistics, quotations, and references. The reliability of the AI-assisted steps was measured against independent models and against human coders, and the full audit trail is released with the data.

### 4.11 Data and code availability

The frozen dataset, every analysis script, the append-only research log, the full risk-of-bias appraisals with their supporting quotes, and the complete adjudication trail of the independent-model verification, including every row where our own coding was found wrong, are deposited on the Open Science Framework under DOI **[DOI TO BE INSERTED ON DEPOSIT]**. All reported numbers regenerate deterministically from that one dataset; the deposit contains the scripts and the run order that do it. The working repository from which the deposit is built also holds the full texts of the included studies, which cannot be redistributed, so the deposit is a curated subset and not a mirror of it.

---

## References


Allcott, H., & Gentzkow, M. (2017). Social media and fake news in the 2016 election. Journal of Economic Perspectives, 31(2), 211–236. https://doi.org/10.1257/jep.31.2.211
Aslett, K., Guess, A. M., Bonneau, R., Nagler, J., & Tucker, J. A. (2024a). Online searches to evaluate misinformation can increase its perceived veracity. Nature, 625, 548-556. https://doi.org/10.1038/s41586-023-06883-y


Aslett, K., Sanderson, Z., Godel, W., Persily, N., Nagler, J., Bonneau, R., & Tucker, J. A. (2024b). Testing the effect of information on discerning the veracity of news in real time. Journal of Experimental Political Science, 11(3), 262-276. https://doi.org/10.1017/XPS.2023.20


Altay, S., Berriche, M., & Acerbi, A. (2023). Misinformation on misinformation: Conceptual and methodological challenges. Social Media + Society, 9(1). https://doi.org/10.1177/20563051221150412


Berriche, M., & Altay, S. (2020). Internet users engage more with phatic posts than with health misinformation on Facebook. Palgrave Communications, 6, 71. https://doi.org/10.1057/s41599-020-0452-1


Boulianne, S., & Humprecht, E. (2023). Perceived exposure to misinformation and trust in institutions in four countries before and during a pandemic. International Journal of Communication, 17, 2024–2047.


Cordonier, L., & Brest, A. (2021). How do the French inform themselves on the Internet? Analysis of online information and disinformation behaviors. Fondation Descartes.


Parry, D. A., Davidson, B. I., Sewall, C. J. R., Fisher, J. T., Mieczkowski, H., & Quintana, D. S. (2021). A systematic review and meta-analysis of discrepancies between logged and self-reported digital media use. Nature Human Behaviour, 5(11), 1535–1547. https://doi.org/10.1038/s41562-021-01117-5
Kreps, S., George, J., Watson, N., Cai, G., & Ding, K. (2022). (Mis)information on digital platforms: a quantitative and qualitative analysis of COVID-19 content on Twitter and Sina Weibo. JMIR Infodemiology, 2(1), e31793. https://doi.org/10.2196/31793
Mourão, R. R., & Robertson, C. T. (2019). Fake news as discursive integration: an analysis of sites that publish false, misleading, hyperpartisan and sensational information. Journalism Studies, 20(14), 2077–2095. https://doi.org/10.1080/1461670X.2019.1566871
Shao, C., Hui, P. M., Wang, L., Jiang, X., Flammini, A., Menczer, F., & Ciampaglia, G. L. (2018). Anatomy of an online misinformation network. PLOS ONE, 13(4), e0196087. https://doi.org/10.1371/journal.pone.0196087
Tai, Y. C., Lin, T. H., & Desmarais, B. A. (2026). Elected officials' online sharing of misinformation: institutional and individual predictors. Political Communication, 43(1), 1–24. https://doi.org/10.1080/10584609.2026.2613661
Wirtschafter, V., Batista Pereira, F., Bueno, N. S., & Pavão, N. (2024). Beyond fact-checking: the limits of professional review in a high-volume misinformation environment. Journal of Quantitative Description: Digital Media, 4.
Godel, W., Sanderson, Z., Aslett, K., Nagler, J., Bonneau, R., Persily, N., & Tucker, J. A. (2021). Moderating with the mob: Evaluating the efficacy of real-time crowdsourced fact-checking. Journal of Online Trust and Safety, 1(1). https://doi.org/10.54501/jots.v1i1.15


Guess, A., Nyhan, B., & Reifler, J. (2020). Exposure to untrustworthy websites in the 2016 US election. Nature Human Behaviour, 4(5), 472–480. https://doi.org/10.1038/s41562-020-0833-x
Moore, R. C., Dahlke, R., & Hancock, J. T. (2023). Exposure to untrustworthy websites in the 2020 US election. Nature Human Behaviour, 7(7), 1096–1105. https://doi.org/10.1038/s41562-023-01564-2

Allen, J., Howland, B., Mobius, M., Rothschild, D., & Watts, D. J. (2020). Evaluating the fake news problem at the scale of the information ecosystem. Science Advances, 6(14), eaay3539. https://doi.org/10.1126/sciadv.aay3539

Allen, J., Watts, D. J., & Rand, D. G. (2024). Quantifying the impact of misinformation and vaccine-skeptical content on Facebook. Science, 384(6699), eadk3451. https://doi.org/10.1126/science.adk3451

Altay, S. (2026). Rethinking the problem of misinformation and its solutions. New Media & Society. https://doi.org/10.1177/14614448261428635

Altay, S., & Mercier, H. (2026). Misinformation is a symptom: Commentary on Ecker et al. (2025). American Psychologist, 81(2). https://doi.org/10.1037/amp0001550

Altay, S., Berriche, M., Heuer, H., Farkas, J., & Rathje, S. (2023). A survey of expert views on misinformation: Definitions, determinants, solutions, and future of the field. Harvard Kennedy School Misinformation Review, 4(4), 1–34. https://doi.org/10.37016/mr-2020-119

Barendregt, J. J., Doi, S. A., Lee, Y. Y., Norman, R. E., & Vos, T. (2013). Meta-analysis of prevalence. Journal of Epidemiology and Community Health, 67(11), 974–978. https://doi.org/10.1136/jech-2013-203104


Begg, C. B., & Mazumdar, M. (1994). Operating characteristics of a rank correlation test for publication bias. Biometrics, 50(4), 1088–1101. https://doi.org/10.2307/2533446

Budak, C., Nyhan, B., Rothschild, D. M., Thorson, E., & Watts, D. J. (2024). Misunderstanding the harms of online misinformation. Nature, 630(8015), 45–53. https://doi.org/10.1038/s41586-024-07417-w

Carlson, M. (2020). Fake news as an informational moral panic: The symbolic deviancy of social media during the 2016 US presidential election. Information, Communication & Society, 23(3), 374–388.

Ecker, U. K. H., Tay, L. Q., Roozenbeek, J., van der Linden, S., Cook, J., Oreskes, N., & Lewandowsky, S. (2025). Why misinformation must not be ignored. American Psychologist, 80(6), 867–878. https://doi.org/10.1037/amp0001448

Grinberg, N., Joseph, K., Friedland, L., Swire-Thompson, B., & Lazer, D. (2019). Fake news on Twitter during the 2016 US presidential election. Science, 363(6425), 374–378. https://doi.org/10.1126/science.aau2706

Guyatt, G. H., Oxman, A. D., Vist, G. E., Kunz, R., Falck-Ytter, Y., Alonso-Coello, P., & Schünemann, H. J. (2008). GRADE: An emerging consensus on rating quality of evidence and strength of recommendations. BMJ, 336(7650), 924–926. https://doi.org/10.1136/bmj.39489.470347.AD

Hameleers, M. (2025). Reconciling discrepancies between low estimates of misinformation exposure versus high perceived threats: A theoretical overview and a future research agenda. Communication Theory. https://doi.org/10.1093/ct/qtaf021

Hoes, E., Clemm von Hohenberg, B., Gessler, T., Wojcieszak, M., & Qian, S. (2025). (Media attention to) misinformation can undermine trust in scientists. Political Behavior. https://doi.org/10.1007/s11109-025-10090-y

Hoy, D., Brooks, P., Woolf, A., Blyth, F., March, L., Bain, C., Baker, P., Smith, E., & Buchbinder, R. (2012). Assessing risk of bias in prevalence studies: Modification of an existing tool and evidence of interrater agreement. Journal of Clinical Epidemiology, 65(9), 934–939. https://doi.org/10.1016/j.jclinepi.2011.11.014

Kim, J., Bak, B. R., Agrawal, A., Wu, J., Wirtz, V. J., Hong, T., & Wijaya, D. (2023). COVID-19 vaccine misinformation in middle income countries. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing. https://doi.org/10.18653/v1/2023.emnlp-main.237

Matthes, J., Corbu, N., Jin, S., Theocharis, Y., Van Aelst, P., et al. (2023). Perceived prevalence of misinformation fuels worries about COVID-19: A cross-country, multi-method investigation. Information, Communication & Society, 26(16), 3133–3156. https://doi.org/10.1080/1369118X.2022.2146983


Munn, Z., Moola, S., Lisy, K., Riitano, D., & Tufanaru, C. (2015). Methodological guidance for systematic reviews of observational epidemiological studies reporting prevalence and cumulative incidence data. International Journal of Evidence-Based Healthcare, 13(3), 147–153. https://doi.org/10.1097/XEB.0000000000000054

Neely, S. R., Eldredge, C., Ersing, R., & Remington, C. (2022). Vaccine hesitancy and exposure to misinformation: a survey analysis. Journal of General Internal Medicine, 37(1), 179–187. https://doi.org/10.1007/s11606-021-07171-z

Nickl, P. L., Sultan, M., Stinson, C., Stock, F., Hertwig, R., & Kozyreva, A. (2025). Global crisis or overblown problem? Three tools to clarify contentious issues in misinformation research. SocArXiv preprint. https://doi.org/10.31235/osf.io/4vhwq_v1

Oswald, L., & Munzert, S. (2026). Little change in a changing landscape: Tracking exposure to untrustworthy news in Germany from 2017 to 2024. Journal of Quantitative Description: Digital Media, 6. https://doi.org/10.51685/jqd.2026.006

Page, M. J., McKenzie, J. E., Bossuyt, P. M., Boutron, I., Hoffmann, T. C., Mulrow, C. D., et al. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. BMJ, 372, n71. https://doi.org/10.1136/bmj.n71

Pennycook, G., & Rand, D. G. (2026). Consensus, disagreements, and open questions in the psychology of misinformation. Annual Review of Psychology. https://doi.org/10.2139/ssrn.6752858

Pierri, F., Artoni, A., & Ceri, S. (2020). Investigating Italian disinformation spreading on Twitter in the context of 2019 European elections. PLOS ONE, 15(1), e0227821. https://doi.org/10.1371/journal.pone.0227821

Pierri, F., DeVerna, M. R., Yang, K. C., Axelrod, D., Bryden, J., & Menczer, F. (2023). One year of COVID-19 vaccine misinformation on Twitter: Longitudinal study. Journal of Medical Internet Research, 25, e42227. https://doi.org/10.2196/42227

Rogers, R. (2020). The scale of Facebook's problem depends upon how 'fake news' is classified. Harvard Kennedy School Misinformation Review, 1, 1–15.

Stecula, D. A. (2025). Getting misinformation wrong: Why content fixes can't solve structural problems. SNF Ithaca Research Scholar White Paper No. 5.

Suarez-Lledo, V., & Alvarez-Galvez, J. (2021). Prevalence of health misinformation on social media: Systematic review. Journal of Medical Internet Research, 23(1), e17187. https://doi.org/10.2196/17187

Tay, L. Q., Hurlstone, M., Jiang, Y., Platow, M. J., Kurz, T., & Ecker, U. K. H. (2024). Causal inference in misinformation and conspiracy research. Advances.in/Psychology. https://doi.org/10.56296/aip00023

Tay, L. Q., Lewandowsky, S., Hurlstone, M. J., Kurz, T., & Ecker, U. K. H. (2024). Thinking clearly about misinformation. Communications Psychology, 2, 4. https://doi.org/10.1038/s44271-023-00054-5

van der Meer, T. G. L. A., & Hameleers, M. (2025). Perceptions of misinformation salience: A cross-country comparison of estimations of misinformation prevalence and third-person perceptions. Information, Communication & Society, 28(4), 575–596. https://doi.org/10.1080/1369118X.2024.2375256

Van Doorn, M. (2023). Advancing the debate on the consequences of misinformation: Clarifying why it's not (just) about false beliefs. Inquiry. https://doi.org/10.1080/0020174X.2023.2289137

Viechtbauer, W. (2010). Conducting meta-analyses in R with the metafor package. Journal of Statistical Software, 36(3), 1–48.

Vincent, E. M., Crisan, D., & Carniel, B. (2025). Measuring the state of online disinformation in Europe on very large online platforms. First report of the SIMODS project. Science Feedback.

Wardle, C., & Derakhshan, H. (2017). Information disorder: Toward an interdisciplinary framework for research and policymaking. Council of Europe.

Watts, D. J., Rothschild, D. M., & Mobius, M. (2021). Measuring the news and its impact on democracy. Proceedings of the National Academy of Sciences, 118, e1912443118. https://doi.org/10.1073/pnas.1912443118

Williams, D. (2026). How tribes construct rival realities. Conspicuous Cognition (blog essay).


## Supplementary Note A. Risk of bias, sensitivity analyses, and certainty of evidence

### A1. Risk of bias

All 443 studies were appraised with the Hoy prevalence instrument (41% high, 47% moderate, 12% low risk; the ratings feed the GRADE assessment in B3). We report the appraisal descriptively, because its two design items closely restate this review's denominator and definition taxonomy — item 10 is rated high for 90% of topical denominators (128 of 143) and 79% of curated samples (95 of 120), against 10% of population denominators — and the eight generic quality items show no association with estimate size: recomputing the summary rating as an unweighted count over those eight items and excluding the studies it rates high moves the content median from 23.0% to 22.9%, against 15.0% when the two design items are weighted in.

### A2. Sensitivity analyses

- The falsity/quality rule: folding Quality into Content, so that quality ratings count as misinformation as much of the field practises, moves Content only from 23.0% to 23.3% (+0.6 pp). Excluding borderline-flagged rows does not change it at all.
- Excluding abstract-appraised studies moves Content −1.2 pp and leaves Exposure unchanged.
- A sixth analysis, restricting to independently re-extracted studies, has been retired. It rested on the seeded 48-study pilot, whose Content, Recall and Reach cells hold 8, 3 and 13 studies, too few to inform anything; and it has since been superseded, because every study in the corpus has now been re-extracted blind (Supplementary Note B1), which makes the restriction vacuous.
- Deliberate miscoding: because the corpus was coded by an AI-assisted pipeline, we asked how much undetected construct error the central comparison could absorb. A fraction of the 897 main-set estimates was reassigned at random to a different construct, drawn uniformly from the other five, and the medians recomputed; 200 replications at each level. This is harsher than any plausible confusion, since real disagreement concentrates on adjacent pairs while uniform reassignment moves an exposure row into recall as readily as into reach. The behavioural-exposure to self-reported-recall ratio is 32.7× uncorrupted, 8.0× with a tenth of the codes wrong, 4.4× with a fifth and 2.8× with a third, and it does not reverse even when half the codes are randomised. The separations the review rests on hold at the same levels: behavioural exposure stays below reach in 100% of draws at a tenth and 81% at a third, sharing below content in 100% and 98%, and content below recall in 100% at every level. The one comparison that does not survive is reach against sharing, whose medians are one point apart (12.0% and 13.0%): it flips in nearly half of draws at a tenth, which is why the Results report those two as indistinguishable rather than ordered.
- No secular trend (exploratory): the between-construct gaps are stable across 2005–2026: within no construct is the rank correlation between study year and prevalence significant. Behavioural exposure drifts, if anything, downward over time (medians ≈5% pre-2016 to ≈0.5% post-2022, small k, n.s.). Content-prevalence appears to rise (≈11% pre-2016 to ≈29% post-2022), but this tracks the field's shift toward topical and health-specific samples, not a real increase. Recall stays high throughout (≈52–63%) and sharing flat (≈10–16%). The exposure–perception gap is therefore not recent. (Per-era study counts are small and these *p*-values approximate; the full table is in the released data.)

### A3. Certainty of evidence (GRADE)

We rated the certainty of evidence with GRADE (Guyatt et al. 2008), adapted to prevalence questions following the methodological guidance for prevalence reviews (Munn et al. 2015). Certainty is moderate for Exposure, Reach, Recall, Concentration and Sharing, and very low for Content (downgraded for risk of bias, indirectness, imprecision, and selection bias from curated corpora). Supplementary Table 1 gives each construct with its median, interquartile range, share of high-risk-of-bias studies, and main downgrades.

**Supplementary Table 1. Construct summaries with certainty of evidence.**

| Construct | k | Median % (IQR) | % high RoB | Certainty | Main downgrades |
|---|---:|---|---:|---|---|
| Exposure | 18 | 1.3 (0.5–3.6) | 0% | MODERATE | imprecision (weighting-fragile) |
| Reach | 27 | 12.0 (7.4–26.2) | 4% | MODERATE | imprecision (weighting-fragile) |
| Sharing | 45 | 13.0 (3.9–22.5) | 20% | MODERATE | indirectness (sharing proxies exposure) |
| Recall (seen) | 71 | 57.7 (37.5–71.0) | 22% | MODERATE | indirectness (perception, not exposure); shared-recall reported separately (19.8%, k = 36) |
| Concentration | 19 | top 1%: 70.0 (k = 5); ≤1% band: 62.4 (k = 10) | 11% | MODERATE | indirectness (distributional); thresholds not poolable, reported per band |
| Content | 274 | 23.0 (7.1–39.0) | 54% | VERY LOW | RoB, indirectness, imprecision, selection |

No construct reaches high certainty, and none falls to low: the five moderate ratings are downgraded once each, for different reasons given in the table, while Content is downgraded on four grounds at once. The uniformity of the column is therefore an outcome, not a default. Behavioural exposure comes closest on risk of bias and directness, with no study in the cell rated high risk and a measure of the quantity the review is about rather than a proxy for it, but its median falls from 2.0% to 0.6% when studies are weighted by sample size, a 70% shift, and it is downgraded once for imprecision on that ground, as reach and content prevalence are. We did not apply a separate inconsistency downgrade for the near-total I² reported in §2.4: with sampling variances spanning eleven orders of magnitude, I² is close to 100% by construction and does not discriminate between constructs, and the spread it reflects is the measured effect of the coded moderators (§2.4) rather than unexplained inconsistency; the prediction intervals are reported so that readers can weigh this choice.

### A4. Time windows of the recall questions and the reach observations

We extracted the time window of the survey question from the full text of all 71 seen-recall studies (the coding file, with the question wording where printed, is in the repository). Twenty-one studies ask whether people have ever encountered misinformation (no window), 21 use an unbounded frequency scale (never to very often, or none to a lot), eight refer to a specific event or period (an outbreak, an election campaign, "since the last survey"), 14 ask about a bounded window (five past week, four past month, one past three months, two past six months, two past year), and seven are unclear, two of them because no full text could be obtained. The estimates are similar across time windows: bounded-window studies have a median of 55.9% (k = 14) against 59.0% for ever/frequency studies (k = 42); period-specific studies have a median of 54.6% (k = 8) and the unclear ones 71.0% (k = 7). The five past-week studies report 48.5%, 52.3%, 53.3%, 56.6% and 60.5% (median 53.3%), the tightest group, and the corpus-wide seen-recall median is 57.7% across 71 studies. With 14 bounded-window studies and ranges of some 60 points within each group, the similarity of the group medians is weak evidence that the window does not matter, not a demonstration of it. Four of the 71 studies are analyses of one instrument, the Health Information National Trends Survey item on the perceived share of false health information on social media, three of them on the same 2022 respondents; they are counted as four studies here, as in the corpus.

We coded the observation window of all 27 behavioural reach studies the same way, from the sentence that bounds each estimate in time. Ten cover a named event, nine of them a US election campaign and the tenth the first 150 days of the 2022 war in Ukraine; eight state a fixed observation period; three span a whole multi-year corpus; two a calendar year; two accumulate over account history with no start bound; one reports an average-day rate; and one states no window at all. The median window is 106 days (k = 23 with a derivable length, range 1 to 1,461).

The comparison runs against the intuition that reach is measured over a short window and recall over a long one. Among
studies carrying a bounded window, the reach windows are the longer ones, a median 106 days against 30 for recall, and
the asymmetry is in whether a window is bounded at all: 59% of the recall studies have none against 7% of the reach
studies. Window length does not explain what reach studies find, either: across the 23 with a derivable length the
rank correlation between window and estimate is −0.04, and two matched 39-day US election panels report 44.3% and
26.2%. What does separate them is the denominator: recruited person panels have a median of 18.5% (k = 20) and
platform corpora and elite samples 1.7% (k = 7).

Restricting both sides to bounded windows of one week to one year narrows the gap and does not close it: recall 55.9%
(k = 14) against reach 18.5% (k = 19), a ratio of 3.0 rather than the 4.8 of the unrestricted comparison. No finer
match is supportable: only the 28-to-45-day band holds four or more studies on both sides, and there the same 37-point
gap appears.

### A5. Platforms studied, by construct

Figure 1 shows which platforms each construct is studied on. Counting studies rather than
estimates, a study counts once in every platform it names, so a corpus spanning Facebook, Reddit,
Twitter and Pinterest appears four times and the bars within a panel sum to more than its k. A
study contributing two constructs is counted in both panels, so the 443 studies
produce 482 study-construct cells. Assigning each study a single modal platform instead would be
tie-dependent, since 26 of those cells have no unique mode. Bars are shares because k ranges from
18 to 274 across the panels; counts are in brackets.

The counts behind §2.2 are as follows. Identification level and ground truth are counted
over the 439 studies that contribute a usable proportion; the four remaining included studies
contribute only quality ratings and enter no prevalence figure, which is why these counts rest on
439 rather than 443. Of the 439, 357 identify misinformation at the claim or item level and 77
classify entire sources, the other five using levels of their own. The 87 studies that state no
per-item veracity standard are almost all source classifiers: 75 of the 77 state none, because a
domain list rates outlets rather than claims, and so do 11 of the 357 claim-level studies and one
of the remaining five. Ground truth follows the same split. Domain lists supply it for 16 of the 18
exposure studies, 23 of the 27 reach studies, 26 of the 45 sharing studies and 13 of the 19
concentration studies, while the content analyses rest on the researchers' own coding in 234 of
274 cases.

The construct-by-platform pattern is given in the Results; what the panels add is what falls outside
it. Browsing-panel data accounts for 8 of the 18 exposure studies, 14 of the 27 reach studies and 4
of the 19 concentration studies, and for no content analysis at all. The video platforms run the
other way and are described almost entirely by what exists on them, not by what people saw. Self-reported
recall is shown for completeness; there the platform is the frame of the survey question
("misinformation on social media") rather than a measured source, and
57 of the 91 recall studies name no platform at all. Two further breakdowns are given in the same form. Supplementary Fig. 1 shows who decided what counted as
misinformation, and Supplementary Fig. 2 the countries studied. Both reinforce the pattern in §2.2:
domain lists supply the ground truth for the exposure, reach, sharing and concentration literatures
and researchers' own coding for the content literature, with almost no overlap. Geographically the
United States dominates every construct,
most heavily in exposure (15 of 18) and concentration (12 of 19), while content analysis is the most international part of the corpus, with 81 global and 31
multi-country studies alongside 58 from the United States.

### A6. Sample size and estimate size (detail)

Within each of the five constructs with an extractable sample size, the rank correlation between a study's sample size and the share of misinformation it reports is negative (Content ρ = −.34 [95% CI −.44, −.23], *t*(269) = −5.93, *p* < .001, k = 271; Reach ρ = −.57 [−.78, −.23], *t*(25) = −3.43, *p* = .002, k = 27; Exposure ρ = −.43 [−.76, .09], *t*(15) = −1.82, *p* = .089, k = 17; Recall (seen and shared) ρ = −.12 [−.32, .09], *t*(89) = −1.16, *p* = .250, k = 91; Sharing ρ = −.29 [−.55, .01], *t*(42) = −2.00, *p* = .052, k = 44). Intervals on ρ are Fisher-z with the Bonett-Wright rank-correlation standard error. This rank-correlation analysis is also the review's small-study-effects assessment (Begg & Mazumdar 1994); Supplementary Note B2 explains why Egger's regression is not interpretable here. Giving each study a weight proportional to its sample size, computed on the studies with an extractable sample size (hence the slightly different baselines from the headline medians), the content-prevalence median falls from 23.0% (k = 270) to 0.9%; reach falls from 12.0% to 0.3%, sharing from 13.3% to 11.4%, and behavioural exposure from 2.0% to 0.6%. Self-reported recall is the exception and rises, from 43.0% to 48.5% (seen and shared pooled, k = 91). The largest studies, which analyse entire platforms or complete browsing records instead of small selected samples, sit at the low end of each construct's distribution. These weighted medians are the values implied by the very largest designs, not better pooled estimates: the single largest study holds 36–84% of the total weight depending on the construct, and the three largest 57–100%.

### A7. How abstracts report selected samples

Among the 95 studies in this corpus whose estimate rests on a rank-truncated or hand-selected sample, 64 name the selection in the abstract, 26 give only a sample size, and 5 give neither; of the 73 abstracts that headline the percentage, 23 (32%) do so without saying how the sample was selected, so the number travels without its denominator.

## Supplementary Note B. Methods details

### B1. Screening, the corpus repair, and the reliability of the AI-assisted pipeline (full detail)

**Human validation of the screening decisions.** After the dataset was closed, two coders, the author and a research assistant blind to the pipeline's decisions, independently re-screened a blinded sample drawn at each stage: 200 titles (150 pipeline exclusions and 50 advances), 60 abstracts (40 exclusions), and 50 full texts (25 included and 25 excluded studies). Every record on which either coder disagreed with the pipeline was then adjudicated against the abstract or the full paper. At the title stage the coders would have advanced 7 and 13 of the 150 excluded titles; on adjudication against the abstract none was a study the review should have included (0 of 150, one-sided 95% upper bound 2.0%). At the abstract stage the coders would have advanced 7 and 5 of the 40 excluded abstracts and agreed on two, and both of those were genuine misses (2 of 40, upper bound 14.9%): a nationally representative survey of UK social media users reporting the share who had amplified exaggerated or false news in the past month, and a content analysis reporting the share of the 100 most-liked TikTok videos on sunscreen that were inaccurate; both are included in the corpus analysed here. Both had also passed a same-model false-negative audit of all 1,120 abstract-stage exclusions run before the freeze, which is the pattern described below: an error the model makes consistently is invisible to a second pass of the same model. At full text the coders disagreed with the pipeline on 6 and 17 of the 50 studies; adjudication against the paper upheld the pipeline in all 20 contested cases (0 of 25 over-inclusions and 0 of 25 over-exclusions, upper bound 11.3% each). That adjudication was not blind to which call was the pipeline's; the adjudication tables ship with the data, so the rulings can be re-examined.

Because the title screener is recall-protective (uncertain records advance as "maybe"), agreement with a precision-minded human is structurally low even when no eligible study is lost, so we report miss rates first and agreement coefficients second. At the title stage, binary agreement (advance versus exclude) with the pipeline was 88% for the author (κ = 0.66) and 85% for the research assistant (κ = 0.59), and between the two coders 85% (κ = 0.56); of the 50 titles the pipeline advanced, both coders would have excluded 17, all of which the pipeline itself later excluded at abstract or full text. At the abstract stage agreement was 70% (κ = 0.29) and 72% (κ = 0.30), and between coders 78%; every abstract the pipeline advanced and a coder would have excluded was likewise excluded downstream, so the low coefficients measure the coders' strictness relative to a recall-protective screener rather than loss. At full text, the author agreed with the pipeline on 44 of 50 studies (κ = 0.76) and the research assistant on 33 (κ = 0.32), with the assistant more inclusive than the pipeline on excluded studies (11 of 25) and the author more inclusive on 4; adjudication against the papers resolved all 20 contested cases in the pipeline's favour, so the difference between the two coefficients tracks how strict each coder was, not how often the pipeline erred. One of the author's four would-include calls was a study he had himself ruled out, on the same grounds, two months earlier, which is the test-retest ceiling applying to human coders as much as to models. An earlier research-assistant round on the harder inclusion decision produced κ = 0.33 with the assistant systematically stricter; adjudication of the 29 contested cases found the assistant correct on 11 and the pipeline correct on 18, implying about 14% over-inclusion at that stage of the pipeline. All 29 adjudications, and the seven coding rules the round produced, were applied to the dataset before the version analysed here, so the 14% estimates the pipeline's pre-correction error, not the residual error of the released corpus.

**The protocol deviation, and the repair it required.** The screening criteria written in June 2026 named audience exposure, consumption, observed sharing, concentration, actor-level prevalence and content prevalence, but did not name self-reported recall, and listed perception-only measures as an exclusion. Recall is one of the six constructs this review analyses, so it was excluded by instruction at both the title and the abstract stage; the recall studies in the first corpus entered despite the criteria rather than because of them. Content prevalence was also under-specified: the criteria named it without stating that single-keyword, most-viewed and rank-truncated samples qualify. The defect was found by the human validation above, when two of forty sampled abstract-stage exclusions turned out to be eligible studies both coders would have advanced.

The corpus was repaired. We did not simply note the problem and move on. Every title-stage and abstract-stage exclusion was re-screened under corrected criteria naming all six constructs, by two independent model families (Claude and GPT-5.6-luna) working blind in fresh sessions of one batch each, with the union of their flags going to adjudication. That surfaced 3,379 flagged titles and 1,645 flagged abstracts; adjudication across the two stages passed 477 records to full-text retrieval, of which 335 texts were obtained (142 could not be retrieved), including 172 that required institutional access. All 335 were screened at full text and extracted to the same schema by the same protocol as the original corpus. 208 were eligible and 127 were not.

Two numbers should be read together. 477 records were judged eligible from their titles or abstracts, but only 208 of the 335 retrieved survived full-text screening. In almost every failed case the construct is present and the paper reports no share of it, giving instead a scale mean, a latent variable with only path coefficients, a value that exists only in an unlabelled figure, or descriptives deferred to a supplement. Abstract-stage screening cannot see any of that. The review therefore reports the full-text-confirmed count throughout, and the observation is itself a finding about the literature: a large class of survey studies measures self-reported exposure and never publishes a prevalence. The repair confirmed 208 studies at full text, of which 147 carry a poolable estimate; 16 of those were removed in the later dispute adjudication, leaving 131 in the released dataset. It moved one headline: at the repair freeze, self-reported recall fell from 53% to 41% as its study count rose from 27 to 96. Content prevalence does not move. The full account, including every ruling made on the recovered rows, is in the repository.

**Four kinds of check, and what each can detect.** Because the pipeline is LLM-assisted throughout, we distinguish four grades of evidence about coding quality and report all four. They are not interchangeable, and the question is not whether the pipeline was checked but what each check can and cannot detect.

Model self-consistency. Two passes of the same model, on screening (κ = 0.89), construct classification in the full double extraction (κ = 0.82, n = 778), and risk-of-bias appraisal (PABAK = 0.78). These measure reproducibility, not correctness. Two passes of one model cannot surface an error the model makes consistently, because the reading that produced the error produces it again. We report them because a pipeline that cannot reproduce itself is not usable, and we do not treat them as evidence that the coding is right.

Independent model. A different model family reading the corpus blind is the check that carries the most weight, because a different family does not share the pipeline's systematic errors. Every independent check ran on GPT-5.6 against a pipeline built on Claude models. The first sweep recoded 647 estimates across 306 of the 315 studies the corpus then held, with no sight of our coding: construct κ = 0.80, denominator scope κ = 0.72. The repair was recoded separately, as it stood when the check ran, 468 rows across 148 studies, 131 of which are in the released dataset, at construct κ = 0.77 with 85.0% raw agreement. The same coder was then shown our value, denominator and construct for each repair row and asked to check them against the paper, confirming 83.1% outright. That second figure is a confirmation rate, not an agreement statistic, and cannot be converted to a κ, because the coder saw our answer; its complement, 16.9% of rows, is the rate at which the coder flagged something to check, and each of those went to adjudication against the source.

Those sweeps left studies unread, and coverage is worth counting against the corpus as released rather than as it stood when any one check ran. Nine studies fell outside the first sweep: six carry no proportion at all, their only estimates being mean or median quality scores that enter no prevalence figure; one reports its recall figure as a range rather than a point; and two had entered in the repair after the sweep was built. A further twenty had since arrived from the behavioural-arm search. Two later passes closed both gaps, each under the sweep's own instructions. The first took the two late arrivals and agreed on all seven of their estimates. The second took the remaining twenty-two studies and their 38 estimates, giving 37 the construct we gave (κ = 0.96), 23 of 26 the same definitional breadth, and 7 of 17 the same denominator class. Each of the fourteen disagreements was ruled against the source paper: ours was upheld on twelve, ten of them the same boundary, whether a topic search that is also rank-truncated or filtered for relevance is topical or curated; the independent coder's reading was adopted on one, a survey item we had coded as false where the paper says respondents were asked about information that was “misleading or false”; and one denominator class remains a boundary the coding instructions decide rather than the paper, flagged as such in the released adjudication file. With those two passes the cross-family check reaches all 443 included studies, and the blind re-extraction reaches all 443 as well.

The July sweep read 626 of the 678 estimates then in the dataset (1048 estimates at the released freeze), the rest declined as too uncertain to code, blind to our coding, on construct, denominator class, and definitional breadth: construct κ = 0.75 (raw 0.82), breadth κ = 0.69, denominator class κ = 0.53. It doubled as an error-detection pass, since every disagreement is a candidate coding error. The sweep was then repeated on the current dataset with the same base model, in nine stratified batches in separate sessions, coding all 647 codeable estimates blind: construct κ = 0.80 (raw 0.86), denominator scope κ = 0.72, definitional breadth κ = 0.48. Two properties of that figure bound how it should be read. It is measured against the dataset as it stood before the disagreements were adjudicated, so it is not inflated by our having subsequently adopted the model's calls; scored against the released dataset it is κ = 0.82. And the 439 estimates that played no part in any adjudication agree at κ = 0.82, slightly above the corpus figure, which is what one expects if the adjudicated rows were the genuinely hard ones.

The breadth coefficient (κ = 0.48) is the lowest of the three. It is not instrument noise: on rows it coded twice the model reproduced its own breadth judgment 94% of the time, so it is stable and simply disagrees with us. The disagreements concentrate on definitions that state no veracity standard at all, or that state two. A study defining misinformation as "false or misleading" has told the coder that its criterion admits material which is not strictly false, but not how far beyond falsity it reaches; a study identifying misinformation by domain reliability has set no per-item veracity standard, and the right code is blank. Where a definition commits, to fact-check verdicts or to fabrication, agreement is high. Breadth agreement therefore measures how precisely this literature specifies what it is counting. We retain the three-value scale because the studies that do specify a standard use it consistently and it behaves as predicted (§2.4), and we leave the residual boundary cases coded as they stand, since harmonising them would manufacture the agreement the coefficient is supposed to measure.

The denominator coefficient is worth decomposing, because the field it scores collapses two axes. The denominator field fuses the denominator's scope (what universe the percentage is a share of) with its selection (whether that universe was hand-assembled or rank-truncated), so a coder who correctly identifies a topical corpus is marked wrong for not instead naming it curated. Scored on scope alone, independent agreement across the whole corpus is κ = 0.72 (raw 0.80, 458 estimates), against κ = 0.47 for the fused field. Our denominator scope coding is reliable, and essentially all of the residual sits on one judgment, whether a corpus counts as curated, where the independent coder is systematically more willing than we are to call a corpus hand-assembled.

One instrument caveat generalises beyond this review. An automated coder's agreement with a dataset cannot exceed its agreement with itself, so test-retest is a ceiling on any reported κ. Our first attempt to re-code all 647 codeable estimates in a single pass degraded: on rows it had already coded under identical instructions it reproduced only 45% of its own denominator codes and 65% of its own construct codes, and it collapsed the seven denominator categories into two defaults, using the single-source category 280 times where the dataset uses it 27. Scored naively, that run would have reported denominator κ = 0.18 and been read as evidence against our coding; it was in fact evidence about the coder. We discarded it and re-ran in stratified batches, which returned construct κ = 0.80 across all 647 estimates, with test-retest on repeated rows at 5 of 6 and 8 of 10 in the first two batches. Reliability figures from long automated coding runs should be accompanied by a test-retest measure, or they risk reporting coder fatigue as inter-rater disagreement.

The independent checks changed the dataset, twice. A first sampled round disputed 34 rows and source-anchored adjudication found our coding wrong on 20; the full-corpus sweep then triaged 263 load-bearing disagreements to the 49 rows lying in transition patterns with a confirmed track record of being ours, and we were wrong on 33 of those (67%, a hit rate within a pre-selected queue, not a corpus error rate; corpus-wide denominator agreement was 64%). A final consistency detector caught 17 further cells where a targeted correction had stranded same-instrument sibling rows in the old class. Nearly all corrections were one pattern: rank-truncated "top-N most-viewed" corpora coded as exhaustive topical searches, an error our own codebook already prohibited and that repeated same-model audits had passed over. This is the clearest demonstration of what independent checking adds: the errors a model makes systematically are invisible to itself.

Blind re-extraction. Agreement checks ask whether the rows we have are right; they cannot ask what we failed to extract. For that, every study was re-extracted from its full text by fresh agents working in separate sessions with no sight of the frozen coding: 57 batches covering all 456 studies the corpus then held, finished on 9 September 2026. The blind pass agreed that 430 of the 456 studies were eligible and disputed 26. It reproduced 712 of the 837 frozen main-pool values (85.1%), and proposed 202 candidate omissions across 123 studies. Agreement on the coded moderators was highest where the field states its choices and lowest where it does not: classification level κ = 0.96, ground truth κ = 0.92, denominator scope κ = 0.89, construct κ = 0.89, platform κ = 0.85, sampling frame κ = 0.82, topic κ = 0.79, definitional breadth κ = 0.76, population scope κ = 0.59. Every disputed eligibility call, every value the blind pass did not reproduce and every candidate omission was adjudicated against the source paper by the author. That is 592 adjudicated items: our coding was upheld on 181, the blind coder's was adopted on 172, a third reading on 12, and 5 were the same call recorded differently; 156 items were judged not codeable from the paper as published; 40 rows were added; and 26 items ruled a study ineligible, removing 24 studies. The blind pass therefore changed the dataset on about a third of the items it disputed, and the rulings are released with the data.

A seeded random 10% had been re-extracted the same way before that campaign, and its results are consistent with it: 33 of 283 original studies, with findings reproduced at 90% per study and construct agreement at 94%, and 14 of 141 repair studies, where the two passes agreed on eligibility for all 14 and 29 of our 31 pooled rows were reproduced within tolerance. The one estimate that pass found and we do not hold is a pooled figure averaging two rows we already carry, which recording would double-count.

Human coding. The author adjudicated every contested coding against the source paper; no model verdict was ever applied automatically. Two human coders, the author and a research assistant blind to the dataset (her earlier-round studies excluded), independently coded the same blinded sample: 24 items classified from the reported-quantity sentence plus the paper's definition, and 24 items coded from the full paper with the value hidden. The figure that carries weight is coder-versus-coder agreement, which bounds how hard the task intrinsically is; the author's own comparison with the dataset is reported but is not blind, and two items contaminated by mid-study disclosure were excluded from it by a rule pre-specified in the research log before scoring. The result is a two-stage evidence gradient (24 full-paper items in two batches, the second drawn from the hardest stratum, content analyses). From sentence-level evidence, the human ceiling on construct classification is κ = 0.48. Given the full paper, denominator agreement rises to κ = 0.84 (raw 91% across the 23 full-paper items both coders coded), construct to κ = 0.60, and value agreement to 65% (15 of those 23 items, counting two values as agreeing when they match after rounding). The two batches split informatively: on transparently reported designs, coder-versus-coder agreement was near-perfect (denominator 11 of 11, value 10 of 11); on the difficult stratum, content analyses, both coders independently reported before seeing any scores that some papers fit no construct and described their methods too opaquely to extract from, and agreement fell accordingly. The human ceiling inherits the literature's reporting quality: coding uncertainty concentrates where the papers' own reporting is thinnest. Residual value discrepancies were adjudicated against the sources and traced overwhelmingly to the instrument or to papers reporting several equally plausible figures rather than to coder or dataset error.

In nine of ten coder-versus-coder construct disagreements the dataset's code coincides with one of the two coders. The strongest error signal the design can produce, both coders agreeing with each other against the dataset, occurred on four items; re-adjudication from the full text upheld the dataset on all four, each traced to evidence the item's snippet had hidden.

A second adjudication round did move the dataset: on the harder batch the two coders jointly flagged three items, and re-reading upheld the taxonomy but overturned the data, with two denominator recodes and the removal of a study that proved, on full reading, to be a fraudulent, likely machine-generated paper in a predatory journal (internally contradictory methods; chatbots reported as measurement platforms). It had cleared automated screening, extraction and risk-of-bias appraisal; only two humans reading the whole paper caught it. A prompted integrity re-screen of the 87 included studies sharing that ingestion profile (open-access additions lacking an indexed metadata trail, the first fraudulent paper among them) found two further fraudulent papers with the same predatory-venue signature; the remaining 84 verified clean, and the rest of the corpus carries indexed metadata and DOIs. We report that re-screen as a bounded check; it is no guarantee: screening for fabrication is only as good as the signals a reader can see. On construct classification within jointly included studies, the earlier research-assistant round agreed 42 of 51 (82%).

The asymmetry between the two halves of the corpus should be stated. The original corpus was extracted twice by the same family and reconciled; the repair's studies were extracted once and then verified by a different family. The repair is therefore weaker on same-family reproducibility and stronger on independent coverage, and the studies that entered after both passes had run are weaker on both. Neither half rests on a single unchecked pass, but they are not checked in identical ways, and the blind re-extraction is what makes the two comparable.

**Who ruled what.** The two round-3 adjudications were the author's, with one qualification: he ruled 17 of the 20 full-text cases, 4 of the 14 grey-claim cases were settled by re-reading the producer's own publication and 3 of the 20 full-text cases by re-reading the source, in each case with the resolution put to the author and approved by him, not decided by him unaided. Those seven rulings are flagged as such in the released adjudication files, so a reader can recompute any statistic in Table 2 with them included or excluded.

**Direction of the corrections.** Because the author is a participant in the debate the review describes, two further checks address the direction of all these corrections. Across the 59 successive versions of the dataset leading to the one analysed here, the six construct medians were recomputed at every version from the released files themselves. Transitions that changed the corpus by more than five studies are corpus expansions, not corrections and are counted separately. The corrections moved a construct median up 24 times and down 22 (exact two-sided sign test, *p* = .883); counting expansions as well gives 25 up and 26 down (*p* = 1.00). Neither direction dominates. The largest single movement is the twelve-point fall in self-reported recall produced by the screening repair, which is an expansion, not a correction. Every movement is in the released data. Restricting each construct to the 157 studies that received author or research-assistant verification at some stage yields medians close to the full corpus for every construct with more than a handful of verified studies (Content 20.9% vs 23.0%, k = 114; Exposure 1.0% vs 1.3%, k = 7; Reach 11.0% vs 12.0%, k = 13; Sharing 13.5% vs 13.0%, k = 24), with the deviations running in both directions. Recall is the exception (52.7% vs 43.0%) on five verified studies, too few to compare.

### B1b. Risk-of-bias interpretive rule

A published source-level credibility list (NewsGuard, Media Bias/Fact Check, the Grinberg lists, Oxford "junk news") satisfies item 6. Penalising source-level identification here would double-count it, because definitional breadth is already a coded moderator; doing so would also render the bias rating collinear with breadth, making "high-risk studies report higher numbers" indistinguishable from a restatement of the breadth coding.

### B2. Additional statistical procedures

The four measurement moderators travel together. Cramér's V runs 0.48 to 0.97 across all six pairs
at the estimate level, which is why the main text treats them as one family. Their variance shares
are univariable, so each includes variance it shares with the others. The shares do not sum, and
should not be added.

**Uncertainty on the variance-explained ladder.** Each moderator's df-adjusted pseudo-R² was re-estimated on 200
study-cluster bootstrap resamples (studies drawn with replacement, sparse levels re-collapsed within each resample).
Percentile 95% intervals: ground-truth source 22.8% [17.4–29.1], identification level 21.8% [16.6–27.4], construct
19.1% [13.6–24.6], denominator class 16.6% [9.5–25.9], measurement type 16.6% [11.5–21.8], platform 14.1% [10.6–21.4],
sampling frame 12.7% [8.3–19.4], breadth 12.0% [6.7–18.2], topic 1.8% [0–6.7]. The leading intervals overlap one
another and the construct's, so the order is not a ranking. Topic is the exception: its interval lies entirely below
every measurement moderator's. Restrict the model to content analyses (414 estimates from 270 studies) and the ladder
becomes: ground-truth source 15.5%, identification level 13.6%, breadth 9.2%, topic 4.7%, denominator class 3.7%,
platform 3.2%, the binary denominator contrast 3.2%, sampling frame 2.6%. Measurement type has no rung there: it is
derived from the construct, so within a single construct it does not vary and cannot be fitted. Topic rises to fourth
of eight, above the denominator class, the platform and the sampling frame, but still below the ground-truth source,
the identification level and definitional breadth. The claim the main text makes is the corpus-wide contrast between
identification and topic. This within-construct model does not support it on its own, and we do not present it as
though it did.

**Meta-regression.** To quantify how much each moderator independently explains, we fit multilevel meta-regressions to logit-transformed proportions (metafor, logit-transformed proportions), with estimates nested in studies via nested random effects (estimates within studies) and cluster-robust inference clustered by study (robust omnibus tests for every reported fit, univariable and multivariable), restricted to the 837 estimates (419 studies) with an extractable sample size. Four deliberate choices govern the models.

- Moderator levels represented by fewer than ten estimates are collapsed into an "other" level before modelling, because such cells produce coefficients too unstable to report.
- Uncoded moderator cells enter as an explicit "unspecified" level rather than being dropped row by row. Dropping them would run each univariable model on a different subset, so the variance-explained ladder would compare moderators on different data. Definitional breadth is uncoded for 204 of the 837 estimates, where the source states no veracity standard.
- Measurement type is derived from the construct taxonomy rather than coded separately: content analyses code content, recall surveys are self-report, and the four audience constructs read behavioural records. It is therefore a three-level grouping of the constructs, redundant with construct in any model that carries both, and the two are one family in the same sense as the ground-truth source and the identification level.
- Pseudo-R² is reported degrees-of-freedom-adjusted as well as raw. Raw R² mechanically rewards factors with more levels, and ranking a twelve-level platform variable against a three-level measurement variable on it would mislead.
- We report variance explained rather than emphasising coefficients, because the PLO sampling variance assumes independent Bernoulli draws while the large behavioural studies count clustered units (user-days, tweets, impressions). The ratio of largest to smallest sampling variance is ~7 × 10¹¹, so those studies are over-weighted. This is a limitation of the model, not of the medians, which are our primary statistic.

**Small-study effects.** We test whether larger samples report lower prevalence with a Spearman rank correlation between study sample size and study prevalence, the rank-correlation approach to small-study effects and publication bias (Begg & Mazumdar 1994), not Egger's regression: with precisions spanning eleven orders of magnitude Egger's intercept is not interpretable (our fits returned intercepts of 200–900 on the logit scale, which are scaling artefacts). A rank correlation is invariant to that problem and tests the claim directly.

**Precision-weighting sensitivity.** We compare the unweighted study-level median with a sample-size-weighted median, each with a study-cluster bootstrap CI. Because a few very large studies dominate the weighted statistic, it is interpreted as the value implied by the largest (typically behavioural, whole-corpus) designs, not as a precision-optimal pooled estimate.

**Concentration.** Concentration estimates ("the top X% of users/sources account for Y% of exposure or sharing") are standardized to a common (population-share, activity-share) form. Because the reported thresholds differ across studies, per-threshold values rest on small and non-overlapping study sets and are reported with their study counts rather than as a single curve. User-level and source-level concentration are reported separately.

### B3. Extended limitations

Seven limitations qualify the synthesis.

**Language.** Only English-language studies were included. The bias is documented; its direction is
unknown.

**Coverage.** 15% of included studies came from outside the primary database, and they sit in
journals that database indexes. The residual gap is therefore one of query recall, not database
coverage, and a broader query is the remedy we could not exhaust.

**Pipeline.** Screening, extraction and appraisal were AI-assisted. We report reliability in four
grades (§4.8, Note B1), because the weakest grade, same-model consistency, is where most reviews
stop. Independent-model checking changed this dataset: a different model family disputed our
denominator codes, and source-anchored adjudication found us wrong on dozens of rows, almost all in
one pattern, rank-truncated corpora coded as exhaustive searches. The audit trail is public in the
repository, because the lesson generalises. Errors a model makes systematically are invisible to
same-model audits. Human coding shows the same dependence on what the evidence allows: two trained
coders agree only moderately when classifying constructs from isolated result sentences (κ = 0.48),
converge when given transparently reported full papers (denominator κ = 0.84 across 23 items), and
on the opaque stratum are capped by the papers themselves.

**Re-checkability.** 25 studies were coded from the abstract alone, no full text being obtainable.
Each is listed with its DOI in the released data, so any reader can check the coding against the
abstract at its source, and Note A2 reports construct medians with every abstract-only appraisal
excluded.

**Synthesis.** The meta-regression's sampling-variance model assumes independent draws, which the
large behavioural studies violate. We therefore lean on medians and report the model as variance
explained only. Prediction intervals spanning nearly the unit interval mean that construct labels
alone predict little. That is the paper's point, and also its ceiling: we explain the structure of
the divergence, not most of its variance.

**Scope.** The corpus is dominated by health content and a handful of Western platforms. Climate and
immigration misinformation prevalence is essentially unmeasured, and platform coverage follows data
access, not importance. One study measures something no other does: its denominator is 480 observed
face-to-face conversations during community health workers' home visits, 41.3% of which carried a
misinformation claim, and it is the corpus's only estimate of offline interpersonal transmission. We
code it as content, because the denominator is communication events each individually judged, which
is what the construct means. An independent coder reading it blind proposed a different construct,
on the reasonable ground that every other content study counts posts, videos or articles. We keep it
and flag it here instead of removing a study whose measurement is merely unusual. A reader comparing
it with the platform studies should treat it as a different measurement, not a larger one.

**Registration.** The review was not prospectively registered (§4.1). The append-only,
version-controlled research log documents each analytic decision and its rationale with commit
timestamps, but a timestamped log is a weaker guarantee than prospective registration, and we flag
it as such.

## Supplementary Note C. Full search strategy

Scopus, searched 2026-06-20, year-sliced retrieval, no language or date limits at query level:

TITLE-ABS-KEY ( ( misinformation OR disinformation OR "fake news" OR "false news" OR "unreliable news" OR "untrustworthy websites" OR "low-quality news" OR "junk news" ) AND ( exposure OR consumption OR consume* OR reach OR audience OR "news diet" OR "information diet" OR prevalence OR circulation OR sharing OR shared OR spread OR diffusion OR dissemination OR quantif* OR "how much" OR supersharer* OR "super-sharer*" OR traffic OR visits OR engagement OR scale ) ) AND NOT TITLE ( detection OR classifier OR classification OR "deep learning" OR "neural network" OR transformer )

OpenAlex keyword search and PubMed (2026-06-24) used the same term families adapted to each interface; OpenAlex citation snowballing ran backward and forward from 224 audience-side core studies. A supplementary concentration-targeted search (2026-06-21) added concentration-specific terms (concentration, Gini, superspreader, top-X%).

OpenAlex behavioural-design arm, searched 2026-09-07, two sweeps over works published from 2010:

- `title_and_abstract.search:<topic>, abstract.search:<method>` for each of nine topic terms (misinformation, disinformation, fake news, false news, unreliable news, junk news, low-quality news, news quality, untrustworthy) crossed with each of eighteen method terms (web tracking, browsing data, browsing history, clickstream, digital trace, trace data, donated data, data donation, web panel, online panel tracking, passive metering, url-level, desktop and mobile tracking, browser extension, platform data, server log, exposure log, media diet).
- `title.search:<method>` for the same eighteen method terms, with hits then filtered on the topic words, which catches papers whose topic wording we did not anticipate.

The two sweeps returned 6,972 works, 5,382 of them new to the review. This arm exists because the June search crossed topic terms with outcome terms, and studies built on browsing panels, clickstreams and donated data describe themselves by their method; the rationale, and the check that led to it, are in the arm's own instructions in the repository.

Two further searches probed recall rather than adding records to the flow. The concentration-targeted Scopus query above is one. The other is a Google Scholar check of self-reported recall, five queries run by hand on 2026-09-04 and listed with their yields in the repository; Scholar has no stable exportable result set and blocks automated querying, which we did not work around, so it is reported as a recall check and not as a source. It found that the exposure and concentration literatures were saturated and that the gap was one of venue, not of query wording, with candidates clustering in journals Scopus does not index; five of its studies are in the dataset.

All queries are parameterised scripts in the repository, each run writing a dated dump; per-record screening dispositions for the full reconciliation set ship as supplementary data (satisfying per-study exclusion reporting). Supplementary Data 1 lists every included study with its bibliographic record, the country, platform, sample size, ground-truth source, identification level and definitional breadth it was coded on, its risk-of-bias rating with the two design items shown separately, and its study-level value for each construct it contributes, so any median in this paper can be traced to the studies behind it.

## Supplementary Note D. Quantitative claims in the grey literature

Quantitative claims about the amount of misinformation also circulate outside the peer-reviewed literature, in reports and press releases from fact-checkers, regulators, think tanks, advocacy organisations, and platforms. The sweep followed a written protocol with a pre-specified producer list, fixed search strings, and a verbatim figure, source and access date recorded for each claim. It is not a systematic search in the PRISMA sense: the producer list is a purposive sample, and website search has no defined record set, so the catalogue can be audited but makes no claim to completeness. For this reason the claims are never pooled with the corpus and we draw no conclusions about their coverage. The corpus itself is not restricted to journal articles: institutional reports with full methods enter it whenever the systematic search surfaces them, as with the Cordonier & Brest 2021 panel study.

Most of the catalogued claims do not measure misinformation prevalence. After removing duplicates, only 35 of the 117 are misinformation-prevalence estimates. Of the rest, 21 are bare counts with no denominator ("3.8 billion views"), which cannot support a prevalence claim; 15 quantify something broader or other than misinformation (YouTube's violative-view rate, for example, covers all policy-violating content); 9 restate academic estimates, several from studies already in our corpus; and 7 measure attitudes or concern instead of exposure. The remainder describe the composition within misinformation, moderation performance, or figures that the producer's own report gives only as upper bounds or for subgroups. The claim-by-claim classification, with every retained estimate verified against its producer's own publication, ships with the data (§4.3).

The 35 estimates reproduce the ordering the Results report, with the same gap between self-reported perception and content classification: what a grey-literature number means is given by its construct and its denominator, not by who produced it.

## Supplementary Note E. How much of what an unreliable source publishes is false?

Almost every behavioural estimate in this review rests on source-level identification. Domain lists
supply the ground truth for 16 of the 18 exposure studies, 23 of the 27 reach studies and 26 of the
45 sharing studies (§2.2). Their known weakness is looseness inside the domains they name: not
everything an unreliable outlet publishes is false. This note collects what the literature has
actually measured about that. The quantity is almost never an estimate under this review's rules,
because its denominator is a source-labelled pool and not an audience or a content population, so it
lives in validation paragraphs and robustness appendices, never in abstracts, and it appears in no
row of the released dataset.

Twenty-seven studies bear on it, seventeen of them in this corpus. Eleven draw a sample of content
from list-flagged sources and judge each item, and eight of those give a usable number. They do not
converge. Why they do not is this review's own finding arriving from a new direction: what a source
list is found to contain depends on the standard someone applies to it.

**Supplementary Table 2. Falsity measured inside a source-labelled pool.**

| verdict standard | study | pool | value |
|---|---|---|---:|
| matched to an existing fact-check | Wirtschafter et al. 2024 | 139 flagged posts with working links | 5.0% |
| completely false | Mourão & Robertson 2019 | 646 random-week stories from 46 sites | 1.7% |
| mostly or completely false | Mourão & Robertson 2019 | same | 11.8% |
| any deviation from fact | Mourão & Robertson 2019 | same | 43.5% |
| false | Allcott & Gentzkow 2017 | random sample of articles from 65 sites | just under 55% |
| misleading or false | Tai, Lin & Desmarais 2026 | 126 flagged legislator posts | 60% |
| false or misleading | Pierri et al. 2023 | 50 randomly chosen shared links | about 76% |
| false, misleading or unverifiable | Shao et al. 2018 | 44 articles carrying a claim | 72.7% |
| false, given the item was fact-checked | Guess, Nyhan & Reifler 2020 | articles matched to professional fact checks | more than 93% |

Read down the table. The same instrument, on the same kind of material, goes from catching almost
nothing to catching almost everything, and all that changes is the question asked of each item. The
5% and the 93% are a single selection read from its two ends. Fact-checkers adjudicate claims that
already look false; Wirtschafter et al. measured what that leaves out, and found 95% of flagged
material had never been checked by anyone. Mourão & Robertson's study is the most informative of the
set, because it reports a whole distribution instead of one cut: 56.5% of the stories they sampled
contained no misinformation by any of their standards.

The same gap appears at the claim level, where it is harder to see. One study in this corpus defines misinformation against the World Health Organization's fact-check page and reports 1.1% of its coded tweets as misinformation (Kreps et al. 2022); of the eleven items it prints as examples, one corresponds to an entry on that page, two are commentary about misinformation, not instances of it, one is a news report, and one states the then-current scientific account of the virus's origin. Naming an external standard and being governed by one are different things, and the difference is visible only to a reader who checks the coded items against the standard a paper cites. Agreement statistics cannot surface it, because two coders applying the same reading agree with each other.

The composition of the flagged pool says the same thing from the other side. The tier that publishes almost exclusively fabricated material is a small part of what the lists flag: 2.6% of it in one decomposition, about 14% in a second and about 30% in a third, with the remainder made up of hyperpartisan and clickbait sources whose output is not fabricated. In one French panel, 41% of consumption inside the unreliable pool was clickbait, a category defined with no falsity claim at all.

One design would settle this better than anything in the table, and it exists. Three papers from one group (Aslett et al. 2024a; Aslett et al. 2024b; Godel et al. 2021) select popular articles from mainstream and low-quality sources within 48 to 72 hours of publication and then commission six professional fact-checkers to rate each one true, false or misleading, or undetermined. Because the articles are chosen before any fact-check exists, the design removes the selection that makes the 93% figure an outlier, and it carries a mainstream arm as a built-in comparison. The published article reports only its pooled verdicts, but the sampling stream is recorded for every article in the authors' replication data, and mainstream and low-quality sources were tracked through different services, so the two tiers separate cleanly. Over the 165 articles released, balanced at 33 from each of the five streams, the fact-checkers judged 39 of the 99 articles from low-quality sources false or misleading, **39.4%**, against 1 of the 66 from mainstream sources, **1.5%**. That contrast is measured on the same days, by the same coders, under one verdict standard, on articles chosen before anyone had decided which were worth checking, and no other estimate available to us has those properties together. We report it beside Supplementary Table 2 rather than in it, because the split is our computation from released data rather than the paper's own figure. The three papers share one pipeline and one research group, so the three amount to a single piece of evidence.

Three limits on all of this. The samples are small, from 44 to 646 items. Every pool but Mourão & Robertson's is circulation-weighted rather than a sample of what the sites published, which favours the most viral and most checkable items. And three of the composition studies reuse one published tiering, so they are three readings of one instrument, not three independent measurements. We therefore report the range and the standard attached to each number, and do not pool them: a median across these verdict categories would describe coding conventions and tell us nothing about the world.

## Figures and tables

- Figure 6. PRISMA flow diagram (§4.1).
- Figure 1. Platforms studied, by construct (§2.1).
- Figure 2. Topics studied, by construct (§2.1).
- Figure 3. Prevalence estimates by construct.
- Figure 4. What drives the estimate.
- Figure 5. Concentration of misinformation versus news in general.
- Supplementary Fig. 1. Ground truth by construct (Supplementary Note A5).
- Supplementary Fig. 2. Countries studied, by construct (Supplementary Note A5).
