#!/usr/bin/env Rscript
# phaseB_metareg.R — multilevel meta-regression of misinformation prevalence on methodological moderators.
# Model: logit-transformed proportions (metafor PLO), random effects ~1|study/estimate (estimates nested in
# studies), cluster-robust by study. Quantifies how much between-estimate variance each moderator explains.
suppressMessages(library(metafor))
# sparse=TRUE on every fit: the random structure is block diagonal by study, so the dense solve is
# ~27 s a fit against ~0.5 s sparse for the same variance components (checked to 1e-6 pp across all
# ten moderators on 2026-09-15). This run went from ten minutes to seconds.

# Repo root, resolved the same way every Python script in scripts/ resolves it: from the
# script's own location, so the pipeline runs from any checkout or worktree. MISINFO_ROOT
# overrides it; the working directory is the last resort (interactive source()).
resolve_root <- function() {
  env <- Sys.getenv("MISINFO_ROOT")
  if (nzchar(env)) return(normalizePath(env, mustWork = TRUE))
  arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(arg)) {
    return(normalizePath(file.path(dirname(sub("^--file=", "", arg[1])), ".."), mustWork = TRUE))
  }
  normalizePath(".", mustWork = TRUE)
}
ROOT <- resolve_root()
d <- read.csv(file.path(ROOT,"data/synth/phaseB/regression_data.csv"), stringsAsFactors=FALSE)
d$events <- pmin(pmax(d$events,0), d$n)                    # guard
d <- escalc(measure="PLO", xi=events, ni=n, data=d)       # logit proportion + variance
d <- d[is.finite(d$yi) & is.finite(d$vi) & d$vi>0, ]
cat(sprintf("N estimates=%d  N studies=%d\n\n", nrow(d), length(unique(d$study_id))))

# Uncoded moderator cells ("NA" in the CSV, read as real NA) become an explicit "unspecified"
# level rather than being silently dropped row-wise per fit — otherwise each univariable model
# runs on a different subset (breadth loses 204 rows) and the R^2 ladder compares moderators on
# different data. The level is disclosed in the Methods.
#
# 2026-09-18: measurement no longer reaches this rule. It used to be joined from a 22 July
# risk-of-bias file covering 317 of 443 studies, so 40% of rows arrived NA and were folded here
# into an "unspecified" level that meant "not appraised yet" rather than a measurement type. It is
# now derived from the construct taxonomy in phaseB_prep_regression.py and is complete. Because it
# is a deterministic collapse of construct, it is REDUNDANT with construct in any joint model
# (metafor drops it) and the two are one family, exactly as ground_truth and id_method are.
ALL_MODS <- c("construct","measurement","sampling","denom","topic","platform","ground_truth","id_method","breadth","denom_fine")
for (v in ALL_MODS) { x <- as.character(d[[v]]); x[is.na(x)] <- "unspecified"; d[[v]] <- x }
# Collapse sparse moderator levels BEFORE modelling — uniformly, on every modelled moderator.
# Levels represented by only a handful of estimates produce wildly unstable coefficients
# (topicwar_geopolitics had SE=1.51, i.e. an odds ratio anywhere from 0.03 to 11) and reporting
# them as findings would be indefensible. Any level with fewer than MIN_LEVEL_N estimates is
# folded into "other".
MIN_LEVEL_N <- 10
collapse_sparse <- function(x, min_n=MIN_LEVEL_N, other="other") {
  x <- as.character(x); tab <- table(x)
  x[x %in% names(tab)[tab < min_n]] <- other
  factor(x)
}
for (v in ALL_MODS) {
  before <- length(unique(d[[v]])); d[[v]] <- collapse_sparse(d[[v]])
  after <- length(unique(d[[v]]))
  if (after < before) cat(sprintf("  collapsed %-12s: %d -> %d levels (min n=%d)\n", v, before, after, MIN_LEVEL_N))
}
# Reference levels chosen so coefficients read as "vs the most rigorous / narrowest".
# relevel AFTER collapse: collapse_sparse rebuilds each factor, which resets any earlier releveling
# (releveling first silently left the multivariable breadth reference at the alphabetical default).
set_ref <- function(x, ref) { stopifnot(ref %in% levels(x)); relevel(x, ref=ref) }
d$construct   <- set_ref(d$construct,   "EXPOSURE")
d$measurement <- set_ref(d$measurement, "BEHAVIOURAL")
d$sampling    <- set_ref(d$sampling,    "representative")
d$denom       <- set_ref(d$denom,       "whole_diet")
d$breadth     <- set_ref(d$breadth,     "fabricated")
d$topic       <- set_ref(d$topic,       "general_news")

null <- rma.mv(yi, vi, random=~1|study_id/estimate_id, data=d, sparse=TRUE)
tot0 <- sum(null$sigma2)
cat(sprintf("NULL model: total between/within variance (logit) = %.3f\n", tot0))
vr <- max(d$vi)/min(d$vi)
cat(sprintf("CAVEAT: ratio of largest to smallest sampling variance = %.3g. PLO variances assume\n", vr))
cat("  n independent Bernoulli draws; for the large behavioural studies n is user-days/tweets/URL\n")
cat("  impressions, which are clustered, so those variances are UNDERSTATED and those studies are\n")
cat("  over-weighted. Interpret variance-explained, not precise coefficients.\n")
inv_logit <- function(x) 100/(1+exp(-x))
cat(sprintf("Overall pooled prevalence (back-transformed intercept) = %.1f%%\n\n", inv_logit(coef(null))))

## ---- univariable: variance explained by each moderator ----
cat("=== UNIVARIABLE — pseudo-R^2 (reduction in total variance) + cluster-robust omnibus test ===\n")
mods <- c("construct","measurement","sampling","denom","denom_fine","breadth","ground_truth","id_method","topic","platform")
uni <- data.frame()
for (m in mods) {
  f <- as.formula(paste("~", m))
  fit <- tryCatch(rma.mv(yi, vi, mods=f, random=~1|study_id/estimate_id, data=d, sparse=TRUE), error=function(e) NULL)
  if (is.null(fit)) { cat(sprintf("  %-13s : (failed)\n", m)); next }
  # Every reported omnibus test is cluster-robust by study, like the multivariable model —
  # model-based QM understates uncertainty when estimates cluster within studies.
  fitr <- robust(fit, cluster=d$study_id)
  r2 <- max(0, 100*(tot0 - sum(fit$sigma2))/tot0)
  # Raw pseudo-R^2 rewards degrees of freedom: a 17-level platform factor will "explain" more
  # than a 2-level one simply by having more parameters. Reporting them in one ranked ladder
  # (as the manuscript did) is misleading. r2_adj applies an Ezekiel-style penalty so moderators
  # with different df are comparable; BOTH are written out and the ADJUSTED one should be ranked.
  k_par <- fit$QMdf[1]; n_obs <- nrow(d)
  r2_adj <- max(0, 100*(1 - (1 - r2/100)*(n_obs - 1)/(n_obs - k_par - 1)))
  cat(sprintf("  %-13s : R2=%4.1f%%  adjR2=%4.1f%%  robust QM p=%s  (model QM p=%s, df=%d)\n", m, r2, r2_adj,
              format.pval(fitr$QMp, digits=2, eps=1e-4), format.pval(fit$QMp, digits=2, eps=1e-4), k_par))
  uni <- rbind(uni, data.frame(moderator=m, R2=round(r2,1), R2_adj=round(r2_adj,1),
                               QMp=fitr$QMp, QMp_model=fit$QMp, df=k_par))
}
write.csv(uni, file.path(ROOT,"data/synth/phaseB/metareg_univariable.csv"), row.names=FALSE)

## ---- multivariable: conceptually distinct axes (estimand + definition + denominator + topic) ----
cat("\n=== MULTIVARIABLE model: construct + breadth + denom + topic ===\n")
mv <- rma.mv(yi, vi, mods=~construct+breadth+denom+topic, random=~1|study_id/estimate_id, data=d, sparse=TRUE)
mvr <- robust(mv, cluster=d$study_id)                     # cluster-robust SEs by study
r2mv <- max(0,100*(tot0-sum(mv$sigma2))/tot0)
cat(sprintf("Multivariable pseudo-R^2 = %.1f%%   (omnibus QM p=%s)\n\n", r2mv,
            format.pval(mvr$QMp, digits=2, eps=1e-4)))
co <- data.frame(term=rownames(mvr$b), est_logit=round(as.numeric(mvr$b),3),
                 se=round(mvr$se,3), z=round(mvr$zval,2), p=signif(mvr$pval,3),
                 OR=round(exp(as.numeric(mvr$b)),2))
print(co, row.names=FALSE)
write.csv(co, file.path(ROOT,"data/synth/phaseB/metareg_multivariable.csv"), row.names=FALSE)

## ---- model-predicted prevalence for the key contrasts (measurement, holding nothing else) ----
cat("\n=== model-predicted prevalence by measurement (univariable, back-transformed) ===\n")
fm <- rma.mv(yi, vi, mods=~measurement-1, random=~1|study_id/estimate_id, data=d, sparse=TRUE)
pv <- data.frame(measurement=sub("measurement","",rownames(fm$b)),
                 pred_pct=round(inv_logit(as.numeric(fm$b)),1))
print(pv, row.names=FALSE)
write.csv(pv, file.path(ROOT,"data/synth/phaseB/metareg_measurement_pred.csv"), row.names=FALSE)
cat("\nDONE\n")
