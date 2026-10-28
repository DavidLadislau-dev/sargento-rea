---
id: rosetta-stone
title: Rosetta stone pairs
summary: Learn an undocumented file format by pairing each sample with the vendor's own interpretation of the same document, then counting field matches across every pair.
mission: study
needs: [many sample files in the format, a vendor-made interpretation of the same document for each sample, a folder outside any repository for the samples]
tools: [a hex viewer or dump script, a scripting language for the counting script, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: storytold/indd-utils
    url: https://github.com/storytold/indd-utils
  - name: storytold/photocraft
    url: https://github.com/storytold/photocraft
  - name: storytold/photocraft-corpus
    url: https://github.com/storytold/photocraft-corpus
  - name: storytold/wordcraft
    url: https://github.com/storytold/wordcraft
  - name: storytold/lightcraft
    url: https://github.com/storytold/lightcraft
status: proven-upstream
---

# Rosetta stone pairs

An undocumented format is hard to read because the bytes do not say what they mean. A Rosetta stone is a second file, made by the vendor's own program from the same document, that does say. Put the two side by side, count how often a candidate field agrees with the vendor's answer, and keep only what holds across every pair.

## When to use

- You have sample files in a format with no public specification, and the question is "what does this field mean?" or "does my reader or renderer get this right?".
- For at least some samples, the vendor's program also produced something readable that describes the same content. Typical twins:
  - an export in a documented format (InDesign's INDD with its IDML export);
  - a preview or thumbnail stored inside the file (Affinity documents, camera raw files with their embedded JPEG);
  - a flattened composite stored next to the layers (a PSD saved with its merged composite);
  - a PDF printed by the vendor app (Word documents with Word-made PDFs);
  - the same scene saved two ways (a camera shot compressed and uncompressed).
- If no twin exists for your format, this method cannot start. Look for one first: the Study mission's recon phase lists "vendor-made interpretations" for exactly this reason.

## What you need

- Samples: as many as you can get, kept outside every repository (see the `pinned-corpus` recipe).
- A twin for each sample you want to learn from, and some evidence that the twin is of the same save as the sample.
- A way to dump the sample's bytes and objects, so you can look at one object next to the twin's value for it.
- A scripting language for the counting script. Keep the script outside the sample folder and run it so that the sample folder cannot inject code (for Python, use the `-I` flag).
- Optional: REA tools, for samples that are binaries.

## Steps

1. **Inventory the twins.** Count the samples, and count how many have a twin. Write both numbers down. The source project had 357 samples and 240 of them had a twin [S].
2. **Find the join key.** You need a way to say "this object in the sample is that element in the twin". The strongest key is an identifier both sides carry. In the source, the export's `Self` attribute is the sample object's id in hexadecimal. If there is no shared identifier, use a value you can locate on both sides (a text string, a count, a colour, a page number), or compare whole pictures (see step 8).
3. **Check that each pair is the same save.** A twin is not always made from the sample's last save. Mark a pair stale when any of these holds, and count only the others:
   - the sample was saved much later than the twin was written (the source used a gap of more than 1 hour between the two files' modification dates);
   - the twin was written after the sample;
   - either file has no date;
   - the twin names an object the sample does not have, or one the sample has deleted;
   - the sample has content the twin lacks.

   Keep both counts, "trustworthy" and "all", and always say which one a number is over.
4. **Pick one candidate field.** Dump the sample's object, pick the bytes you think hold a value, and read the twin's value for the same object.
5. **Count over every pair.** Write a scratch script that compares the candidate with the twin's value in every trustworthy pair and prints "matches of total". Do not stop at a handful of examples.
6. **Decide from the count.**
   - All match, or all but explained exceptions: you have a fact. Record it with its count (see the `evidence-ledger` recipe).
   - The value is the same in every sample: you cannot tell the field from its neighbours. Do not map it. Record it as "never varies".
   - The stored value occurs but no pair shows its twin value: record "no pair" and move on.
   - Some pairs disagree: look at the exceptions before you trust the rule. Typical causes are stale pairs, a value the twin takes from the exporting computer (installed fonts, time zone), or a second rule that the first candidate hides (the last cause is our guess, not a source finding).
7. **Leave out what cannot be in the file.** Some twin values describe the machine that made the twin, not the document. Name them, leave them out of the counts, and say so.
8. **When the twin is a picture, compare pictures.** Thumbnails, composites and PDF pages cannot be matched field by field. Render your own result from the sample, then measure the difference against the vendor's picture per file (for example mean difference on a 0 to 255 scale) and keep a ceiling per file, as the source does. When you compare two renders, render both with the same program so a difference comes from the input and not from the renderer.
9. **When the twin is the same scene saved two ways,** use the plain version as the answer key for the packed one. Recover the packing rules from the pairs, then check them on more files and more makers.
10. **Try each reading against the oracle.** When a layout has a few possible readings (for instance which of several phases a sensor pattern starts at), decode with every candidate and keep the one that matches the vendor's preview.
11. **Check second-hand descriptions the same way.** If you use someone else's published description of the format, re-describe it in your own words and confirm every structure the code relies on against the samples. Prefer descriptions that fail loudly when wrong (checksums, typed fields).
12. **Re-run when the sample set grows.** A fact that was "N of N" can fall when new samples arrive. Reopen it then. (This step is our advice, not a rule from a source.)

## How the Sargento splits the work

- **Pairing recruit (1).** Order: list the samples and twins by path, join them with the key from step 2, apply the same-save rules from step 3, and write `reports/pairs.md`. Hands back: the counts (samples, with twin, trustworthy, stale, and the reason for each stale pair) and one line per pair with its verdict. It runs its scripts with the isolated flag, so the sample folder cannot inject code.
- **Field recruits (1 per area, such as text, colour, geometry or the container).** Order: own a named list of unknowns, run steps 4 to 7 on each, write the scratch scripts in `tools/`. Hands back: facts in the ledger format (`F-<n> [S]`, the count "N of M", the source), and unknowns with a status. A recruit that reports a field with no count goes back.
- **Picture recruit (optional).** Order: step 8 for one twin kind. Hands back: per-file difference numbers, the ceiling per file, and the worst files.
- **The Sargento** merges facts and unknown statuses into `ledger/facts.md` and `ledger/unknowns.md`, checks that every count says which pair set it is over, and sends back anything without a count. Two recruits never write the same file.

## How to prove it worked

Count, per field, the matches over the trustworthy pairs, and report the size of both the trustworthy set and the whole set. A good result is a table of fields with counts that are all or nearly all matches, and a short list of explained exceptions.

Published results from the source projects, marked [S]:

- [S] A stroke-weight field is listed with an evidence count of 171 of 171 (the source does not state the unit).
- [S] Page references matched in 7,523 of 7,523 on the trustworthy pairs, and index topics in 2,185 of 2,185 (2,223 in all pairs).
- [S] The same-save rule matters: stories had identical text in 99.5 percent of the trustworthy pairs (18,509 of 18,610) against 78.5 percent of the pairs stale by a presence signal (2,000 of 2,547). The rule flagged 165 of 654 pairs.
- [S] Picture twins: an Affinity reader was fitted against the thumbnails of 176 public documents. The collection later grew to 189 and the reader opens all of them. On 21 pinned documents the mean difference was 0 to 4.6 of 255.
- [S] Compressed-versus-uncompressed twins: the photocraft raw reader's notes say the Nikon decoding tables were recovered from the same scenes shot both ways for LightCraft, another storytold project, and verified there, in LightCraft, on about 45 files from about 35 camera bodies.
- [S] Word-made PDFs as twins: wordcraft's changelog entry for one font-substitution rule (Times New Roman drawn in Liberation Serif where it is not installed) reports exact page counts rising from 201 to 229 on a 251-document corpus checked against Word-made PDFs. That shows the Word-PDF twin is usable as an oracle, not that this pairing method works.

Your own run is proven when each fact you rely on has a count of this kind, and when you can say how many pairs were set aside as stale.

## Sources and credits

Method learned from the open-source work of the storytold team. All links are permalinks to a fixed commit.

- Pairing and the join key. [S] "An IDML element's `Self` identifier is the INDD object's UID in hexadecimal" (CLEANROOM.md). https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CLEANROOM.md#L37-L40
- Counting over every pair. [S] "A field whose value is the same in every sample cannot be told apart from its neighbours." https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CONTRIBUTING.md#L115-L119
- The numbers in the proof section: https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/attributes.md#L43-L43 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/index.md#L52-L55
- The same-save rule and its counts. [S] "An IDML in the corpus is not always an export of the same save as the INDD next to it." https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/measurement.md#L17-L33 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/measurement.md#L89-L99
- Same program on both sides of a render comparison. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/measurement.md#L383-L384
- Values that depend on the exporting computer. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/measurement.md#L230-L232
- Embedded thumbnail as oracle. [S] "comparing our render with the thumbnail every Affinity document embeds" (photocraft Affinity reader). https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L87-L96 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L112-L117
- Same scene shot two ways, and candidates tried against the preview. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/raw/README.md#L37-L47
- A camera-made JPEG inside every raw file. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/raw/README.md#L110-L111
- Nikon tables recovered for LightCraft and verified there. [S] "recovered by black-box analysis of CC0 raw.pixls.us samples (the same scenes shot compressed and uncompressed) for LightCraft (storytold/lightcraft#86) and verified there" (photocraft raw reader). https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/raw/README.md#L38-L40 and the merge commit of the LightCraft pull request it names: https://github.com/storytold/lightcraft/commit/92bd3aa688cd385be09dd40e065eabc2e4d95073
- Composite stored in the file. [S] "A PSD saved with Maximize Compatibility holds a merged composite" (photocraft-corpus). https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L57-L58
- Word-made PDFs as oracle, and the one font-substitution rule the page-count rise is reported under. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/docs/file-format-parity.md#L342-L342

## Notes

What the source projects set for themselves, as information about the source and not as rules of this skill:

- The indd-utils project works under clean-room rules: no Adobe software installed, no Adobe binaries read or disassembled, and only sample files made by other people for other purposes, none made to order. The Affinity reader likewise says no Affinity software was ever run and nothing was read from an Affinity installation.
- The indd-utils authors say the analysis was done with an AI model and quote: "The model may have seen InDesign SDK material in its training data." They add that absence of such knowledge cannot be proved, and that there was no two-team separation. Their answer was to rest every recorded fact on corpus evidence that anyone with similar files can re-check.
- A few indd-utils facts rest on one sample that is not public, so others cannot re-check them. The project marks each such fact. Do the same when a fact depends on a file you cannot share.
- Where the source has no oracle yet it says so. For example, the wordcraft parity page states that its DOCX fidelity "has never been checked on real-world files". Say the same when you have no twin for an area.
- Different pages of the source quote different pair counts (489, 606 and 1,251 trustworthy pairs; the last two are both labelled as the corpus of 2026-10). When you write a count, name the set it is over and the date.

## Example

The source's INDD work, in outline: collect samples made by others (357 files, 240 with an export), join each object to the export through its id, drop stale pairs, then test each candidate field over every trustworthy pair, the method the source describes. The stroke-weight field is listed with a match count of 171 of 171 in the source's evidence column (the unit is not stated) [S]; a text-wrap setting that was `false` on every item was recorded as "never varies" and not mapped.
