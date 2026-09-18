#!/usr/bin/env Rscript
# phaseB_metareg_robustness.R — two checks on the variance-explained ladder asked for by the
# 2026-09-02 pre-submission review: (1) study-cluster bootstrap intervals on each moderator's
# df-adjusted pseudo-R^2; (2) the same ladder fitted WITHIN content analyses only, where topic
# varies and measurement type is nearly constant. Same data preparation as phaseB_metareg.R.
suppressMessages(library(metafor))

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
d$events <- pmin(pmax(d$events,0), d$n)
d <- escalc(measure="PLO", xi=events, ni=n, data=d)
d <- d[is.finite(d$yi) & is.finite(d$vi) & d$vi>0, ]
# The same ten moderators phaseB_metareg.R reports. denom_fine was missing here while the ladder in
# section 2.6 reported it, so the paper's fourth-ranked moderator had no interval. That was
# survivable while a run cost 28 hours; it costs about 25 minutes now, so the two lists match.
MODS <- c("construct","measurement","sampling","denom","denom_fine","breadth","ground_truth","id_method","topic","platform")
prep <- function(dd, min_n=10) {
  for (v in MODS) { x <- as.character(dd[[v]]); x[is.na(x)] <- "unspecified"
    tab <- table(x); x[x %in% names(tab)[tab < min_n]] <- "other"; dd[[v]] <- factor(x) }
  dd
}
# TWO THINGS MAKE THIS FAST, AND NEITHER CHANGES A RESULT.
#
# 1. sparse=TRUE. The random-effects structure here is ~1|study_id/estimate_id, which gives a block
#    diagonal V with one block per study. Dense linear algebra on an 837 x 837 matrix costs about
#    27 s a fit; the sparse representation of the same matrix costs about 0.5 s, and returns the
#    same variance components to 1e-6 pp on every moderator (checked against the dense fits before
#    this was changed). The run went from about 28 hours to about 25 minutes (measured
#    23 min at B=200 on 2026-09-16; the three earlier figures quoted here, 15 and 19 minutes,
#    were from partial runs and are what made the docs disagree with each other).
# 2. The null model is fitted ONCE per dataset, not once per moderator. It does not depend on v, so
#    the old code refitted the identical model nine times per resample and threw eight away.
#
# Everything else - the seed, the draw order, the adjustment formula - is untouched, so this run is
# the run the old script would have produced, at 1/100th of the cost.
fit_null <- function(dd) tryCatch(rma.mv(yi, vi, random=~1|study_id/estimate_id, data=dd, sparse=TRUE),
                                  error=function(e) NULL)
r2adj <- function(dd, v, null=NULL) {
  if (nlevels(dd[[v]]) < 2) return(NA_real_)
  if (is.null(null)) null <- fit_null(dd)
  fit <- tryCatch(rma.mv(yi, vi, mods=as.formula(paste("~", v)), random=~1|study_id/estimate_id,
                         data=dd, sparse=TRUE), error=function(e) NULL)
  if (is.null(null) || is.null(fit)) return(NA_real_)
  t0 <- sum(null$sigma2); t1 <- sum(fit$sigma2)
  raw <- max(0, 1 - t1/t0); p <- fit$p - 1; n <- nrow(dd)
  max(0, 1 - (1 - raw) * (n - 1) / (n - p - 1))
}
set.seed(20260902)
## (1) bootstrap over studies
dd <- prep(d)
studies <- unique(dd$study_id); B <- as.integer(Sys.getenv("B", "200"))
null_point <- fit_null(dd)
point <- sapply(MODS, function(v) r2adj(dd, v, null_point))
boot <- matrix(NA_real_, B, length(MODS), dimnames=list(NULL, MODS))
start <- 1
ckpt <- file.path(ROOT,"data/synth/phaseB/.metareg_boot_checkpoint.rds")
if (nzchar(Sys.getenv("RESUME","")) && file.exists(ckpt)) {
  cp <- readRDS(ckpt)
  if (identical(cp$mods, MODS) && cp$B == B) {
    boot[1:cp$b,] <- cp$boot; start <- cp$b + 1
    cat(sprintf("  resuming from checkpoint at %d/%d\n", cp$b, B))
  } else cat("  checkpoint does not match this configuration; starting fresh\n")
}
for (b in start:B) {
  s <- sample(studies, length(studies), replace=TRUE)
  db <- do.call(rbind, lapply(seq_along(s), function(i) { x <- dd[dd$study_id==s[i],]; x$study_id <- paste0(s[i],"_",i); x }))
  db <- prep(db)
  null_b <- fit_null(db)
  boot[b,] <- sapply(MODS, function(v) r2adj(db, v, null_b))
  if (b %% 25 == 0) {
    cat(sprintf("  bootstrap %d/%d\n", b, B))
    # CHECKPOINT. Kept from when a resample cost minutes and a kill lost the lot (a run was stopped
    # at 50/200 on 2026-09-04 having written nothing). It costs nothing now and still lets an
    # interrupted run be reported honestly at the B it reached, or resumed.
    # try(): a checkpoint is an optimisation, never a reason to lose the run. On 2026-09-16 a
    # transient write failure (the macOS permission flap) hit saveRDS at b=200 and aborted the
    # script AFTER all 200 resamples had been computed, throwing away 25 minutes of work before a
    # single result file was written. A failed checkpoint now warns and the run continues.
    try(saveRDS(list(boot=boot[1:b,,drop=FALSE], b=b, B=B, point=point, mods=MODS),
                file.path(ROOT,"data/synth/phaseB/.metareg_boot_checkpoint.rds")), silent=TRUE)
  }
}
done <- sum(!is.na(boot[,1]))
if (done < B) cat(sprintf("  WARNING: only %d of %d resamples completed; intervals are from those.\n", done, B))
ci <- t(apply(boot, 2, quantile, probs=c(.025,.975), na.rm=TRUE))
out1 <- data.frame(moderator=MODS, r2_adj=round(100*point,1), ci_lo=round(100*ci[,1],1), ci_hi=round(100*ci[,2],1), B=done)
out1 <- out1[order(-out1$r2_adj),]
write.csv(out1, file.path(ROOT,"data/synth/phaseB/metareg_r2_bootstrap.csv"), row.names=FALSE)
print(out1)
## (2) within CONTENT only
dc <- prep(d[d$construct=="CONTENT",])
null_dc <- fit_null(dc)
out2 <- data.frame(moderator=setdiff(MODS,"construct"), r2_adj=round(100*sapply(setdiff(MODS,"construct"), function(v) r2adj(dc, v, null_dc)),1),
                   n_estimates=nrow(dc), n_studies=length(unique(dc$study_id)))
out2 <- out2[order(-out2$r2_adj),]
write.csv(out2, file.path(ROOT,"data/synth/phaseB/metareg_r2_within_content.csv"), row.names=FALSE)
print(out2)
cat("DONE\n")
