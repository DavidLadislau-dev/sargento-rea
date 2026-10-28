---
id: evidence-ledger
title: Evidence ledger
summary: Keep every fact about a target with a match count and every open question with a status, so your code relies only on facts you can re-check.
mission: study
needs: [a way to test a claim against many samples, a place to keep two ledger files]
tools: [a scripting language for the counting scripts, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: storytold/indd-utils
    url: https://github.com/storytold/indd-utils
status: proven-upstream
---

# Evidence ledger

A study of an undocumented target produces claims faster than anyone can check them. The ledger is the discipline that keeps them honest: every fact is written with the count that supports it, every open question is written with a status that says why it is open, and code is allowed to use only what is in the ledger.

## When to use

- You study a format or a feature over many samples, and more than one recruit will make claims about it.
- You want the result to be reusable: a later reader, or a later code change, must be able to tell what is proven, what is assumed and what is unknown.
- It pairs with the `rosetta-stone` recipe, which produces the counts, and the `pinned-corpus` recipe, which fixes the samples the counts are over.

## What you need

- A method that turns a claim into a count over samples (a script that prints "matches of total").
- Two ledger files: facts, and unknowns. The Study mission already creates `ledger/facts.md` and `ledger/unknowns.md`.
- A rule that code written during the study cites ledger entries.

## Steps

1. **Write a fact only with its evidence.** An entry says what the field or rule is, which files it was checked on, how many, and what was compared. No count, no fact.
2. **Write the count as "N of M", and write the misses.** Do not round up and do not drop the entries that fail. The source's table lists a field at 1,190 of 1,194 next to one at 171 of 171 [S].
3. **Name the set the count is over.** Say whether M is all samples or only the trustworthy ones (pairs that passed the same-save check of the `rosetta-stone` recipe), and give the date of the sample set. When both numbers matter, give both, as the source does for page references: 7,523 of 7,523 on the trustworthy pairs, 7,561 in all pairs [S].
4. **Mark how sure you are.** Use the study mission's marks: `[S]` for something a source states or a count shows, `[I]` for something you inferred. Say "assumed" in the entry when a choice rests on order or on a guess.
5. **Record exceptions with the count that shows them.** Give the likely cause, worded as a guess when it is one. Where one file held 3 topics that its export lacked, the source wrote that the export "was most likely exported before these entries were made" [S].
6. **Record values that never change.** A value that is the same in every sample tells you nothing about which field it is. Write it down as an observation about the samples, and do not map it to a name.
7. **Keep unknowns in their own file, each with a status.** An unknown names where it sits, how many files it touches, and why it is open. The statuses the Study mission uses:
   - `open`: nobody has found the answer yet;
   - `no field found`: the vendor value varies, but nothing stored follows it;
   - `never varies`: the value is the same in every sample, so its field cannot be told apart;
   - `no pair`: the stored value occurs, but no sample shows its vendor value;
   - `resolved: F-<n>`: answered, and the fact has this number.

   The source also used `not explained` (a rule holds for most files, the exceptions follow nothing stored), `not examined`, `not decoded`, `not stored` and `not needed` (the value comes from the exporting computer, not from the document) [S]. Add a status like these when your project needs it, and define it once.
8. **Leave a trail when an unknown is resolved.** The source keeps a row for the part that is still left and points to the page that now describes the rest [S].
9. **Let code use facts only.** Before a recruit writes code that depends on a field, check that the ledger has the fact. If a value has no field but nearly every reference has it, write it as a default and list it as one, so a reader sees it is not decoded [S].
10. **Keep the measuring method apart from the facts.** Describe how you count (which pairs are trusted, how coverage is computed) in its own note, and keep that note out of the facts file [S].
11. **Mark what others cannot re-check.** If a fact rests on a sample you cannot share, say so in the entry [S].
12. **Re-run the counts when the sample set changes** and fix any entry whose count moved. (This step is our advice, not a rule from the source.)

## How the Sargento splits the work

- **Field recruits** (from `rosetta-stone`, one per area). Order: for each candidate field, report a fact or an unknown in the study's ledger format, with its count, the set the count is over, and the script that produced it. Illustrative lines (the field and numbers are made up): `F-012 [S] Field 0x18 is the page count. 40 of 40 pairs match. Source: reports/pairs.md` and `U-007 What sets the flag at 0x1c? Status: never varies (0 of 40 differ). Owner: pairs`.
- **The Sargento** merges the entries into `ledger/facts.md` and `ledger/unknowns.md`, so two recruits never write the same file. It sends back any entry without a count, any count without its set, and any exception without a note.
- **Audit recruit** (optional, one per milestone). Order: take a random sample of ledger entries, re-run their counting scripts, and list the entries whose count differs. Take every constant in the new code and name the ledger entry it comes from, or report that there is none. It hands back two lists: entries that failed re-checking and constants without a fact. It never edits the ledger.
- **Builder recruits** use the ledger as their only source about the target. When one needs something that is not in it, it files an unknown instead of guessing.

## How to prove it worked

What to count: facts with a "N of M" count, unknowns with a status, and code constants with a ledger entry. The method works when no fact is without a count, no unknown is without a status, and an audit finds no constant without a fact.

This recipe is `proven-upstream` because the source's published attribute table shows the recipe's own test, "every fact has a count", in practice: every row has an entry in its evidence column, most of them "N of M", misses included.

Published numbers from the source, marked [S]:

- [S] The attribute table gives the evidence per field: 171 of 171 for a stroke-weight field, 778 of 778 for a miter limit, and the imperfect 1,190 of 1,194 and 78 of 82 for two colour fields.
- [S] All 2,730 page item chunks of one stored layout "parse exactly" in the samples.
- [S] A field found by testing every candidate value matched 294 of 295 documents.
- [S] Index entries: 2,185 of 2,185 topics on the trustworthy pairs (2,223 in all pairs); 7,523 of 7,523 page references on the trustworthy pairs (7,561 in all pairs).
- [S] The defaults, written because nearly every reference has them, reproduce about 8,910 values, which is 0.031 percent of 28,956,596 values, and 55 of them differ from the reference.

## Sources and credits

Method learned from the open-source work of the storytold team on `indd-utils`. All links are permalinks to a fixed commit.

- The rule that every fact has evidence and that code uses only documented facts. [S] "Code relies only on documented facts." https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CONTRIBUTING.md#L20-L22
- What a fact page holds. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CONTRIBUTING.md#L123-L124 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CLEANROOM.md#L46-L48
- Fact written "before or alongside the code that relies on it". https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CLEANROOM.md#L95-L97
- Counts in an evidence column, including the misses. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/attributes.md#L38-L44 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/attributes.md#L47-L47
- Parse count, and a field found by searching every candidate value. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/attributes.md#L30-L30 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/attributes.md#L110-L114
- Counts named by set, an existence count, and an exception with its guessed cause. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/index.md#L13-L14, https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/index.md#L52-L56, https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/index.md#L98-L100 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/index.md#L108-L110
- Assumptions marked in the facts. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/attributes.md#L51-L51 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/attributes.md#L1077-L1079
- Invariant values recorded as such. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/index.md#L42-L42
- The unknowns page and its statuses. [S] "the rows here only record what is left of them." https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/unknowns.md#L3-L28
- Example unknown rows with counts. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/unknowns.md#L54-L55 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/unknowns.md#L84-L84
- Defaults listed apart. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/unknowns.md#L7-L9 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/measurement.md#L142-L144
- Measuring method kept apart from the facts, and the set a count is over. [S] "facts about the INDD format stay in `docs/format/`." https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/measurement.md#L5-L13
- Facts that others cannot re-check. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CLEANROOM.md#L66-L72
- Numbers go in the commit message. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CONTRIBUTING.md#L159-L161

## Notes

What the source project sets for itself, as information about the source and not as rules of this skill:

- The indd-utils project requires that a change to the converter does not lower value coverage, and that the commit message explains the output difference [S].
- It leaves privately held samples out of committed numbers and never describes their content [S].
- Its unknowns page states which set its counts are over (the trustworthy pairs of a named corpus date). Other pages of the same project give other pair counts for the same month, so always write the set next to the count.

## Example

From the source: the stroke-weight field of the attribute list is listed in the source's evidence column ("IDML value equals INDD value") as 171 of 171; the source does not state the unit of the count. That is a fact with a count. A text-wrap setting stored as `false` on every item was filed under unknowns as `never varies`, with no field name. A colour field that matched 1,190 of 1,194 was written with its four misses and not rounded up [S].
