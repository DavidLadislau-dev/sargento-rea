---
id: perf-before-after
title: Performance before and after
summary: Measure frame rate and frame time on the same machine and scene before and after a change, find the real bottleneck from a profile instead of guessing, and report the numbers together with what they do not show.
mission: build
needs: [a build of the program before the change and one after, a repeatable scene, a way to capture frame times, a way to see where the time goes]
tools: [a frame-time capture with percentiles, a sampling profiler or phase timers, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: boykopovar/AnyPS5
    url: https://github.com/boykopovar/AnyPS5
status: proven-upstream
---

# Performance before and after

A speed-up is a claim, and a claim needs two measurements taken the same way. This recipe fixes the scene and the machine, names the bottleneck from a profile before touching the code, runs the old and the new build alternately, and reports the before and after numbers in the change that makes the claim.

## When to use

- You are speeding up a program that draws frames or does repeated work, and you want to show that the change helps.
- A change claims to be faster and you are asked to review the claim.
- You have a slowdown to track down and need a measurement to start from.

## What you need

- The program built twice: the baseline and the change, each identified by a commit.
- One machine for both builds, and one scene that you can reach again.
- A capture that records frames: presents per window, frame time at p50, p90 and p99, and busy time of the main workers. AnyPS5 has one built in (step 3). Anything that gives percentiles works [I].
- A profile of the baseline: a sampling profiler or the phase timers of the capture.

## Steps

1. **Fix the scene.** Measure in gameplay, not in cinematics, menus or loading screens [S]. Use the default settings, and say so [S]. Measure the same spot every time: load a save, wait for the scene to settle, then measure a fixed window with no input [S].
2. **Fix the machine.** Compare builds on the same machine [S]. On a laptop, run on AC power, because a run on battery can make a neutral change look like a regression [S]. Copy the GPU name from the log line, since the program can pick a software renderer without an error [S]. Check the memory budgets, which can change the frame rate several times over between machines [S]. Say whether the caches were empty or warm, and warm them before you measure, because first and later runs differ [S].
3. **Capture a window, not an impression.** The AnyPS5 switches record a window of presents by frame number or by elapsed seconds [S], or write one summary line every 10 seconds without slowing the title [S]. A digest tool turns a capture into a table and another compares two captures [S]. Captures can affect timing [S], so say so when you report.
4. **Alternate the builds.** Run the baseline and the change as A, B, A, B, at least two runs each, and throw away a run that was disturbed (another program, a sleeping display), saying so [S]. One run is an observation, not a reproduction [S]. AnyPS5 can also alternate two settings within one run and print the mean of each phase [S].
5. **Record the same fields every time.** For each window: presents in the window, frame p50 and p99, GPU busy time per present, and how busy the main worker is [S]. Add the commit of each build and the machine [I].
6. **Find the real bottleneck first.** Read the baseline's profile and name what dominates before you change anything. Two examples from the source:
   - A pull request on host buffer reuse starts from a sampled profile. Freeing, allocating and mapping the large buffers took about 12 %, 10 % and 18 % of the draw thread's samples, and the large tier hit 373 to 385 times per 10 s and missed 606 to 835 times [S]. The cause it names: snapshot sizes change by a few bytes almost every time, so with exact sizes the tier fills its budget with buffers that later requests never match [S].
   - A pull request on depth layers names the cause as re-uploading the same zero-filled layer on every refresh [S]. The baseline's summary line lists `Driver.Packet.memory_wait` at 9770.538 ms per frame next to `Driver.Packet` at 11462.277 ms per frame, and the change's line lists 756.552 and 928.616 [S]. The source does not tie these phases to the cause in so many words, so treat the link as a lead and confirm it by the change [I].
7. **Change one thing and watch the mechanism, not only the frame rate.** After the buffer change the same counters read 1,160 to 1,230 hits, 0 misses and 0 to 5 evictions per 10 s, and the draw committer cost per draw fell from 28.5 to 30.9 us to 20.8 to 21.7 us [S]. If the frame rate moved and the mechanism did not, you have not found the cause [I].
8. **Report before and after.** Give both builds' numbers in one table, with the scene, the settings and the machine (see the table in "How to prove it worked"). AnyPS5 asks for the summary lines of both builds, from the same machine and scene, in the pull request [S].
9. **Say what the numbers do not show.** Name the scene and what you did not test. Report variability, a small gain as small, and trace gaps. The examples in "How to prove it worked" show how.
10. **Keep the tool from changing the result.** The draw-profiling switch finishes every draw on the worker, so it cannot measure a switch that moves draw work off the worker [S]. Keep analysis written by an AI separate from measured data, and say which is which [S].

## How the Sargento splits the work

- **Capture recruit (1).** Order: with the machine and the scene the user names, run the baseline and the change as A, B, A, B, at least twice each, and save every capture and log. Hands back the summary lines of each run, the table of step 5, the list of discarded runs with the reason, and the machine description. It needs the user's machine and a title or scene the user supplies.
- **Profile recruit (1).** Order: from the baseline captures only, list the three biggest costs with their numbers and the evidence for each, and name the one to attack. Hands back `reports/profile.md`. Writes no code.
- **Change recruit (1).** Order: make one change aimed at the named cost, and add a test for it. Hands back the change, the test result and the counter that should move.
- **The Sargento** refuses a speed claim that lacks the same machine and scene, at least two runs per build, or the mechanism counter. It records the numbers in `ledger/facts.md` (see `evidence-ledger`), and keeps in `ledger/unknowns.md` anything the numbers do not show [I].

## How to prove it worked

What to count: for each build, presents in the window and frame p50 and p99; the mechanism counter before and after; the number of runs per build and the discarded ones; the scene and the machine.

The method works when the claimed gain shows in the same-scene numbers of both builds, the mechanism counter moves with it, and the report says what the numbers do not cover.

The source's pull requests are the proof, and each is its author's report of a run. I read the pull requests and did not re-run them [I]. All of them are merged:

| Pull request | Scene as the source states it | Before | After | The source's own limit |
|---|---|---|---|---|
| [#8888](https://github.com/boykopovar/AnyPS5/pull/8888) | A war-room menu of a game, one GPU, two alternated runs each | [S] 34 to 38 presents per 10 s; frame p50 269 to 299 ms. In a 30 s trace window: 108 presents, p50 279.3 ms, p99 340.8 ms, committer busy 92.7 ms (33 %) | [S] 40 to 43 presents per 10 s; frame p50 229 to 257 ms. In the window: 128 presents, p50 230.2 ms, p99 299.8 ms, committer busy 41.9 ms (18 %) | GPU busy per present was 75.2 ms before and 72.4 ms after [S] |
| [#6946](https://github.com/boykopovar/AnyPS5/pull/6946) | The hub of a game, player standing still, caches warm, a 10 s window | [S] 706 presents per 10 s; frame p50 14.0 ms; p99 18.7 ms; queue worker busy 98% | [S] 886 presents per 10 s; p50 11.2 ms; p99 13.7 ms; worker busy 96%. The source: "+25% frame rate." | Both builds carry another pull request; the source says why [S] |
| [#10500](https://github.com/boykopovar/AnyPS5/pull/10500) | An idle character creator at 3840x2160, 20 s windows, caches warm | [S] 14 presents in 20158.338 ms = 0.695 FPS; median frame 1446.853 ms | [S] 171 presents in 20005.180 ms = 8.548 FPS; median frame 115.551 ms | [S] "12.31x FPS in this short paired scene comparison", and not a broad claim. The after capture dropped trace events, and the source says what stays valid |

Three further pull requests show the numbers reported honestly when the result is weak or absent:

- [S] A texture-array pull request ran three pairs: gains of 5.60 %, 56.02 % and 63.63 %. The source states that a repeatable 20 % gain is not established, that baseline variability is unexplained, and that the larger gains must not be presented alone.
- [S] A pull request that cut heap allocations in the draw path reduced the sampled cost of `operator new` from 5.56 to 4.77 samples per frame. The FPS shown by the title went from 8.28 to 8.45 (median of six readings), and frame p50 went from 131.150 to 127.308 ms.
- [S] A pull request on pending-write snapshots makes no game FPS claim, because its scene is limited by the 60 Hz present and shows no regression and no speed-up.

## Sources and credits

The method is documented in the public AnyPS5 project, a compatibility layer for PS5 executables, and demonstrated in its pull requests. File links are permalinks to a fixed commit. Each pull request link is followed by its merge commit. Pull request bodies are the authors' own reports, and the quotes are short.

- Measuring performance, the capture switches and the rules. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L87, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L88, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L89, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L90, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L91, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L118 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L121
- Caches, power, GPU selection and memory budgets. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L51, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L52, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L56, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L57 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L58
- Traces slow the title. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/GAME_TESTING.md#L83 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/TRACING.md#L3
- Capture switches and the in-run comparison. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/TRACING.md#L67, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/TRACING.md#L68 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/TRACING.md#L72
- The rule for speed claims. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/CONTRIBUTING.md#L69 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/AGENTS.md#L14
- The pull requests, with their merge commits: https://github.com/boykopovar/AnyPS5/pull/8888 (merge commit https://github.com/boykopovar/AnyPS5/commit/b05b685642ff32d68fb7c7f88e8b5e9f1837e0f2), https://github.com/boykopovar/AnyPS5/pull/6946 (merge commit https://github.com/boykopovar/AnyPS5/commit/16319642a4c84e861188b75583ce853dfbe0a101), https://github.com/boykopovar/AnyPS5/pull/10500 (merge commit https://github.com/boykopovar/AnyPS5/commit/8864d0e3230ccac2603366474a43f880523a1d4b), https://github.com/boykopovar/AnyPS5/pull/6718 (merge commit https://github.com/boykopovar/AnyPS5/commit/584c5a80fda9e2259b9211ef22810559c1a103ba), https://github.com/boykopovar/AnyPS5/pull/6312 (merge commit https://github.com/boykopovar/AnyPS5/commit/72b0ab3e8e2f3be64a6bfbc40478a456f3ea25c6) and https://github.com/boykopovar/AnyPS5/pull/4889 (merge commit https://github.com/boykopovar/AnyPS5/commit/42e3b32defd8b19cfc7774a5354fca06143121ac)

## Notes

What AnyPS5 sets for itself, as information about the source and not as rules of this skill:

- A pull request that claims a change in speed shows the summary lines of the main branch and of the change, from the same machine and scene [S]. A pull request titled as a performance change is labelled `perf`, and `perf numbers missing` until it holds two valid summary lines with different commits [S].
- The source's guide asks for measurements in gameplay, not in menus [S], while the buffer-reuse pull request measured a menu [S]. The recipe leaves that choice to you and asks you to name the scene [I].
- The measured programs in the pull requests are commercial games that the authors run from their own dumps. The method does not need games; any program that draws repeated frames or does repeated work will do [I].
- These pull requests were found with a search for "perf" in titles of merged pull requests; the six cited are a selection, not a count of all perf work [I].

## Example

An illustrative case with made-up numbers. A profile of the baseline in a fixed scene shows 30 % of the main thread in one allocation call. You change the code to reuse the buffer, and run A, B, A, B on the same machine, two runs each, warm caches, default settings, no input. The counter for allocation calls falls from about 900 to 5 per window. Presents in a 10 s window go from 620 to 700 and frame p99 from 21 ms to 17 ms. You report both tables, the commits and the machine, and say that you tested one scene, so you make no claim for other scenes.
