---
id: black-box-app
title: Black-box app observation
summary: Learn how an installed app behaves by feeding it synthetic inputs and recording what it shows and writes, using only its screen, its exports and its scripting interface.
mission: study
needs: [the app installed on a machine you control, a way to make synthetic input files, a folder outside git for captures and exports]
tools: [the app's own UI and scripting interface, a window-capture tool, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: storytold/photocraft-corpus
    url: https://github.com/storytold/photocraft-corpus
  - name: storytold/wordcraft
    url: https://github.com/storytold/wordcraft
  - name: storytold/cadcraft
    url: https://github.com/storytold/cadcraft
  - name: storytold/soundcraft
    url: https://github.com/storytold/soundcraft
  - name: storytold/pdfcraft
    url: https://github.com/storytold/pdfcraft
status: draft
---

# Black-box app observation

Sometimes the only complete description of how an app behaves is the app. This recipe treats it as a black box: you give it inputs you made yourself, and you record what it draws, saves and exposes through its own scripting interface. Every observation is one input and one recorded output, so you can count them.

## When to use

- You need to know what an installed app does with a given input (how it renders a layer stack, what a setting changes, which options it offers), and neither documentation nor sample files answer it.
- You can run the app yourself. If you only have files the app made, use `rosetta-stone` instead. This recipe is how you produce such input and output pairs on demand.
- You want evidence you can count and check again, in the form the `evidence-ledger` recipe uses.

## What you need

- The app, installed on a machine you control. Note its exact version and the operating system.
- A way to make inputs from scratch: the app's scripting interface (for example ExtendScript or AppleScript), or a small program that writes the format.
- A tool that captures one window, and a git-ignored folder for captures and exports.
- Optional: the `rea` tools, if the study uses them for the capture.

## Steps

1. **Ask one question per run.** For example "what does the app save when this setting is on?". Put it in `ledger/unknowns.md` as an open question.
2. **Make the inputs from scratch.** One feature per file, small, and named after the feature and its parameters. The source's generator creates every file from scratch, from generated gradients, shapes and text [S]. Its guidance asks for small, single-feature files with canvases of 64 to 320 px [S], and its file names give the feature and its parameters [S]. Do not use real documents from real users [I].
3. **Pick the channels the question needs.**
   - *The app's own rendering, saved next to the data.* Look for a save option that stores a rendering in the file. In Photoshop, saving with Maximize Compatibility makes the merged composite Photoshop's own rendering of the layer stack [S]. Each test file is then a document together with the output of the application that made it [S].
   - *The scripting interface.* Drive the app from a script. The source runs an ExtendScript file in the installed Photoshop through AppleScript `do javascript` [S]. Its generator works on one document at a time, saves it and closes it [S], and puts the preferences it changed back when it finishes [S]. The script drives only the app's public scripting API and keeps its output [S].
   - *Asking the scripting interface for names.* When a value has no documentation, ask the API what it calls things. The source reports that it read the name of an undocumented text-on-path value from Photoshop's own descriptor key strings, after its first guess turned out to be wrong [S]. It keeps a diagnostic script that dumps a type layer's `textKey` descriptor [S], and that script turns key ids into names with the call `typeIDToStringID` [S]. That the undocumented name came from this script is our reading, not the source's statement [I].
   - *Window screenshots.* For questions about what the user sees. Capture one window by its window id, never the whole desktop [S], and keep the images in the git-ignored folder [S]. Check each capture before you keep it: only your synthetic content should be visible [I].
   - *Menu and option names.* List them. The source's notes keep the menu tree by name [S].
4. **Record every run.** Print one line per input. The source's script prints `ok` for a generated file, `skip` when the feature is not available in that mode, and `FAIL` when something went wrong [S]. Skip an input the app does not offer, instead of saving a file that does nothing [S].
5. **Record the environment.** App version, operating system and installed fonts. The merged composites do not depend on fonts, but re-rendering the type layers only makes sense with the same fonts installed [S]. The source names the application version in the message of each batch it commits [S].
6. **Treat the recorded output as the reference, and compare content, not bytes.** Compare your hypothesis, or your own implementation, with the recorded output input by input, and count the matches. The source's tests compare their flattened result with the merged composite, file by file [S]. Its regenerated output has the same content each time but is not identical byte for byte [S].
7. **Decide what may leave your machine.** Captures and exports are the app's own output. Keep them in the git-ignored folder unless you have decided that they can be published. See `pinned-corpus` for keeping samples out of git and out of published numbers [I].

## How the Sargento splits the work

- **Surface recruit (1).** Order: list what the app exposes from outside, using only its UI, its scripting interface and its exports: menu names, scripting commands, save and export formats, settings. Writes `reports/app-surface.md`. Hands back the counts of each kind of item and the gaps it could not fill.
- **Generator recruits (1 to 3, one per feature group).** Order: write the script that makes the inputs, one feature per file, and run it on a small subset first. Hands back the script path and the final tally of `ok`, `skip` and `FAIL`.
- **Observer recruit (1).** Order: run the app on the inputs, keep captures and exports in the git-ignored `captures/` folder, and write `reports/observations.md` with the app version, operating system and fonts, and one fact per observation in the ledger format. Hands back facts with counts, each naming its input file.
- **The Sargento** asks the user which questions matter and what may leave the machine, looks through the captures for anything that is not synthetic, merges the facts into `ledger/facts.md`, keeps unanswered questions in `ledger/unknowns.md`, and sends a recruit back when an observation lacks its input file name or the app version.

## How to prove it worked

What to count: inputs generated, the `ok`, `skip` and `FAIL` tally, captures taken, ledger questions answered by an observation, and the inputs on which your hypothesis or implementation agrees with the recorded output ("N of M inputs").

The method works when every observation fact names its input, the app version and a count, and when rerunning the generator gives the same content.

The source publishes counts about the set of files it made this way, but no before and after measurement of the observation method itself, so this recipe is `draft`. The numbers below show the scale, marked [S]:

- [S] The corpus README's file table lists 258 Photoshop files made by scripts. The same README says "256 small PSDs" in one place.
- [S] The test that compares those files with their merged composites sets a floor of 190 passing files and 258 files that survive an export and re-import. These are minimums the test enforces, not published results.

## Sources and credits

Method learned from the open-source work of the storytold team. All links are permalinks to a fixed commit.

- Word, AutoCAD and Pro Tools observed with synthetic documents and window screenshots. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/AGENTS.md#L27, https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L25 and https://github.com/storytold/soundcraft/blob/e82c1689b31ae4941472068ebcd37b12bd4cecf0/AGENTS.md#L22
- Screenshots by window id, kept in a git-ignored folder. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/AGENTS.md#L27, https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L25 and https://github.com/storytold/soundcraft/blob/e82c1689b31ae4941472068ebcd37b12bd4cecf0/AGENTS.md#L22
- Observing is allowed, copying resources is not, and the menu tree is kept by name. https://github.com/storytold/soundcraft/blob/e82c1689b31ae4941472068ebcd37b12bd4cecf0/AGENTS.md#L17 and https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L8
- Acrobat: synthetic fixtures, no personal data, behaviour from public specifications, documentation and black-box observation. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L94 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L92
- The corpus repository: files made by the app, rendered by the app. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L56-L57 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L208-L209
- The generator: scripting interface, one document at a time, preferences restored, everything made from scratch. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L227-L228, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L233-L234, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L235, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L236 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/tools/photoshop-oracles/generate.jsx#L11
- Small single-feature files named after their parameters. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L218, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L196-L197 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L194
- Skip instead of saving a file that does nothing, and the `ok`, `skip` and `FAIL` lines. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L220, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L286 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L287
- Names read from the app's own descriptor key strings, and the diagnostic script. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L248-L249, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L252, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/tools/photoshop-oracles/dump-text.jsx#L1 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/tools/photoshop-oracles/dump-text.jsx#L6
- Output not identical byte for byte, fonts, the application version in each batch commit. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L289, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L268-L269 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L177-L178
- Tests compare the flatten with the merged composite, and the file count. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L90, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L121 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L206
- Floors for the Photoshop set. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/io/tests/it/corpus.rs#L157 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/io/tests/it/corpus.rs#L159
- Notes: rules the source projects set for themselves. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/AGENTS.md#L28, https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L25, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L91, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L25, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L165, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L166 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L78-L79

## Notes

What the source projects set for themselves, as information about the source and not as rules of this skill:

- The wordcraft, cadcraft and soundcraft projects each keep the app they study installed on the dev machine and say it may be observed black-box with synthetic documents, drawings or sessions [S]. The pdfcraft project observes Acrobat only with synthetic fixtures [S].
- Those projects never read, disassemble or copy anything inside the vendor's app bundle, and allow file names and listings only [S]. The pdfcraft project also names one folder inside the bundle that is never opened [S]. This recipe does not use the bundle at all: it observes from outside.
- They capture the app's window by its id and store screenshots under a `plan/` folder. The wordcraft and pdfcraft projects say that folder is git-ignored, and the cadcraft project says screenshots are never committed [S]. For Acrobat, screenshots are private local notes and nothing else [S]. For Acrobat they also require synthetic fixtures and never capture personal data, account information or recent files [S].
- The wordcraft and cadcraft projects never commit files produced by Word or AutoCAD [S]. The photocraft-corpus repository does commit Photoshop files, but only ones that its own scripts generated from scratch, and it excludes hand-made, downloaded and found files [S].
- The photocraft Affinity reader is a different case: Affinity software was never downloaded, installed, run, scripted, screenshotted or disassembled for it [S]. See `licence-firewall`.
- The source's capture commands are for macOS (`screencapture`, AppleScript). On another system use that system's equivalent.
- Which apps you observe, and what you read, are your decisions. Write them in your own rules for the study.

## Example

An illustrative run, with made-up numbers. Question: does setting X change what the app stores as its own rendering? The generator makes 12 small documents, one per value of X. The run prints 11 `ok`, 1 `skip` (the app does not offer that value in grayscale) and 0 `FAIL`. The observer saves each document with the rendering stored and compares it with a baseline. The ledger gets: F-001 [S] Setting X changes the stored rendering in 11 of 11 inputs. Source: reports/observations.md (app version 1.2, illustrative).
