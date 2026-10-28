---
id: rising-floors
title: Rising floors
summary: Make every measurement print its scores, enforce a pass floor that only goes up, fail instead of skip when a reference tool is missing, and accept a parity claim only when a real test backs it.
mission: build
needs: [a harness that compares your output with a reference, a test runner, a CI job]
tools: [your test framework, an independent reference program such as qpdf or Poppler, CI, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: storytold/pdfcraft
    url: https://github.com/storytold/pdfcraft
  - name: storytold/photocraft
    url: https://github.com/storytold/photocraft
  - name: storytold/photocraft-corpus
    url: https://github.com/storytold/photocraft-corpus
  - name: storytold/wordcraft
    url: https://github.com/storytold/wordcraft
status: proven-upstream
---

# Rising floors

A "95 percent done" claim is worth what the check behind it is worth. This recipe makes the check hard to fool in four ways: the harness prints its scores, a test fails when a score drops below a floor, a missing reference tool fails the run instead of skipping it, and a feature counts as done only when a real test says so.

## When to use

- You are re-implementing something and compare your output with a reference: the vendor's own output, an independent program, or samples with known answers (see `black-box-app` and `rosetta-stone`).
- Your pass counts move over time and you want progress to stick: no silent regressions, no checks that quietly stop running.
- You keep a feature or parity list and want its "done" marks to be checkable.

## What you need

- A harness that runs your code over a set of samples and compares each result with a reference.
- A test runner that can fail on a count, and a CI job that runs it on every push.
- The reference tools installed on the CI runner. Optional: a pinned sample set (see `pinned-corpus`).

## Steps

1. **Make the harness print.** It prints a result for each file and totals for each feature group, together with the floors [S]. A bare pass or fail hides where the work is.
2. **Compare with a tolerance that fits the thing measured.** A raw pixel difference is useless between two correct renderers, because they disagree on every glyph edge [S]. The source's pixel comparison counts a pixel as different only when it differs from every pixel in the other image's 3x3 neighbourhood by more than a tolerance [S], runs in both directions and reports the worse result [S].
3. **Set the floor from a run you saw.** For each quantity you count, such as files that pass or files that survive a round trip, set a floor at the number the harness reports now [I], and make the test assert that the count is at least the floor [S]. Keep one floor per sample set and per quantity. The photocraft test for its Photoshop-authored set (258 files) has a pass floor of 190 and a round-trip floor of 258 [S].
4. **Count only what holds everywhere.** If some files pass only on a machine with certain fonts installed, leave them out of the floor. The photocraft re-render test does this, and says its floor counts on none of those files [S].
5. **Only raise floors.** In the same change that improves a result or moves a sample pin, raise the floor to the new number [S]. Never lower a floor silently [S]. If a floor really has to go down, say why in the change and tell the user [I].
6. **Make a missing reference fail where results count.** A test that prints a line and returns reports a pass, so a suite with no reference tools installed looks like one where every tool agreed [S]. The pdfcraft project hit this: its `qpdf_agrees` test had never executed on a CI runner, while the README said saved output was independently checked with qpdf [S]. Its fix is a probe with two outcomes: a declared skip with a notice, or a failure [S]. A variable turns the skip into a failure [S], and CI sets it on the runners that install the tools [S].
7. **Report more than one score when one can hide another.** Word F1 is blind to order: a page emitted back to front scores 1.000 [S]. The source adds a reading-order score, the longest common subsequence of the two word sequences [S]. On a change that moved text, word F1 called 26 of the 29 changed files identical, while the order score separated 18 improvements from 6 regressions [S].
8. **Read a score as a disagreement, not a verdict.** The reference can be wrong. Look at both images before believing the number [S]. When the reference is unusable for a feature, pin the invariant with a test that needs no reference. For JBIG2, the source measured 1 distinct image across 96 fixtures against 8 from Poppler, and pins the invariant in a test that needs no oracle [S].
9. **Keep a parity list where "done" needs a test.** One entry per feature, with a status. An entry is `shipped` only when it works end to end and cites at least one passing test [S]. A checker run in CI rejects claims whose commands, tools or tests do not exist [S].
10. **Say what you do not measure.** The source counts files it cannot compare as unmeasurable, rather than comparing them anyway [S]. Keep a "still to do" list, for example using the real vendor app as the reference rather than other open programs [S]. A wiring checklist is not a measure of behaviour [S].

## How the Sargento splits the work

- **Harness recruit (1).** Order: build or extend the comparison harness so that it prints per-file and per-group results and exits non-zero below a floor. Hands back the harness, the printed totals of one full run and the floors file.
- **Reference-gate recruit (1).** Order: wrap each reference tool in a probe that skips with a notice locally and fails when the gate variable is set, and set the variable in CI. Hands back the probes and two runs of one test, one with the tool absent and one with the variable set.
- **Claims-audit recruit (1).** Order: read the parity list, check that every `shipped` entry cites a test that exists and passes, and write `reports/claims-audit.md`. Hands back "N of M shipped entries have a passing test" and the entries to downgrade.
- **The Sargento** sets a floor only from a run it has seen in a report, refuses any change that lowers a floor without the user's decision, records the scores in `ledger/facts.md` with their counts, and keeps unmeasured areas in `ledger/unknowns.md`.

## How to prove it worked

What to count: each floor and the count behind it, runs in CI where a reference tool was missing and the test skipped (the target is 0), shipped entries with a passing test ("N of M"), unmeasurable samples, and regressions caught by a floor.

The method works when a deliberate regression turns the build red, a removed reference tool turns the CI run red, and every `shipped` entry has a passing test.

The source publishes counts from using the method. Marked [S]:

- [S] A second score changed the verdict on a real change: word F1 called 26 of 29 changed files identical, while the order score separated 18 improvements from 6 regressions.
- [S] A measurement exposed an unusable reference: Poppler rendered 8 distinct images across the 96 JBIG2 fixtures where a correct decoder renders 1.
- [S] A silent skip happened for real: the `qpdf_agrees` test had never executed on a runner. The oracle crate's README gives this case as a reason the crate exists.
- [S] The pdfcraft parity list has 844 entries: 448 shipped, 100 partial, 273 planned and 23 not applicable. All 448 shipped entries cite at least one test (counted from the file at the cited commit; the checker's enforcement is stated in AGENTS.md).
- [S] Floors in use: 631 live menu items for the photocraft menu parity test, and for its Photoshop-authored set a pass floor of 190 and a round-trip floor of 258, for a set of 258 files.

These come from the storytold projects' own repositories, which are one team's work. This recipe has not been run on another project.

## Sources and credits

Method learned from the open-source work of the storytold team. All links are permalinks to a fixed commit.

- Missing oracle: a declared skip or a failure, never a silent pass; the old pattern; the case of `qpdf_agrees`. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L4, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L15 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L19
- The gate variable, CI setting it, a local skip. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L49, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L49-L50, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L48, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L54, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/.github/workflows/ci.yml#L86, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/.github/workflows/ci.yml#L87 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/.github/workflows/ci.yml#L3
- Corpus tests: a missing corpus fails when the feature is on; consumers may skip. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/AGENTS.md#L111, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L96 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L149
- Pixel comparison, both directions, why a raw difference is useless, report only. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L68, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L72, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L74-L75 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L81
- Scores are disagreements, and the JBIG2 measurement. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L83, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L85-L86, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L115-L116, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L91-L92 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L93
- Two scores: word F1, reading order, and the measurement on one change. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L97-L98, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L102, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L104, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L111 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L112
- Still to do, and unmeasurable files. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L121 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L125
- Parity list: shipped needs a test, the checker, the status rule, and the counts. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L103, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/parity/acrobat-features.toml#L3, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/parity/acrobat-features.toml#L2, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/parity/acrobat-features.toml#L8 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/parity/acrobat-features.toml#L16-L10220
- Menu parity floor in photocraft. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/AGENTS.md#L91, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/ui-egui/src/menus/parity.rs#L9, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/ui-egui/src/menus/parity.rs#L10 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/ui-egui/src/menus/parity.rs#L4
- Wiring is not behaviour, scorecard numbers are measured, keeping results from regressing. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/AGENTS.md#L81, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/AGENTS.md#L86, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/AGENTS.md#L102-L103 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/AGENTS.md#L66
- Corpus floors: raise when improved, never lower, the test assertion and the set it applies to. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/io/tests/it/corpus.rs#L35-L36, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/io/tests/it/corpus.rs#L157, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/io/tests/it/corpus.rs#L159 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/io/tests/it/corpus.rs#L435
- The harness prints per file, per group and its floors. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/engine/tests/it/photoshop_oracles.rs#L11 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L91
- Environment-dependent files and the re-render floor. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/engine/tests/it/photoshop_oracles.rs#L12-L13, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/engine/tests/it/photoshop_oracles.rs#L13, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/engine/tests/it/photoshop_oracles.rs#L23 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/engine/tests/it/photoshop_oracles.rs#L24
- Raising floors with a pin bump. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L186, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L187 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L86
- A parity floor in wordcraft. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/AGENTS.md#L44
- A bound per file in the Affinity corpus test. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L116-L117

## Notes

What the source projects set for themselves, as information about the source and not as rules of this skill:

- The pdfcraft CI sets the gate variable `PDFCRAFT_ORACLES_REQUIRED=1` for its Linux job [S]. The probe counts the variable as set for any value, including `0` [S], so setting it to 0 does not turn it off.
- Not every measurement gates. The pdfcraft pixel comparison against the reference only reports [S].
- The photocraft floors are minimums that tests enforce. They are not the measured results, and the source does not publish those results in the files cited here.
- The photocraft AGENTS.md names the parity floor's file as `crates/ui-egui/src/parity.rs` [S], but at the cited commit the constant is in `crates/ui-egui/src/menus/parity.rs` [S].
- The photocraft AGENTS.md says a parity checklist built from menu wiring is not a measure of behaviour, and that the scorecard's numbers are measured and to be preferred to estimates [S].
- The corpus README advises other apps that consume its files to let their tests skip when the files are absent [S], while photocraft's own CI always runs them [S]. Which runs may skip is your choice.

## Example

An illustrative run, with made-up numbers. A harness over 40 sample files prints 31 passing and sets the floor to 31. A change makes 34 pass, and the same change raises the floor to 34. A later change makes only 33 pass, and the test fails with a message that the pass count fell below the floor of 34. In CI the reference tool is missing on one runner, so the run fails with a message that names the tool and the install command, and nobody reads a skip notice as a pass.
