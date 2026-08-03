# TheSecretMindset — channel extraction

Full strategy extraction of the YouTube channel [@TheSecretMindset](https://www.youtube.com/@TheSecretMindset).

Fresh line of work. Nothing here touches the BTCUSDT 15m study or its holdout.

## What was done

1. Enumerated the channel: 267 videos, about 62 hours.
2. Pulled captions for 266 of them (one video, `H3x-7_TM-ak`, has none published).
3. Ran one extraction pass per video, producing a structured note: indicators and their exact
   stated settings, context filter, entry, stop, target, invalidation, any performance claim,
   and a vagueness log of every rule that is not mechanically computable as stated.
4. Ran a second, adversarial pass over every strategy the first pass called fully mechanical,
   to check that claim rather than trust it.

The governing rule throughout was that no agent may invent a parameter the speaker did not state.
A note saying "stop loss: NOT STATED" is the correct output. A note quietly filling in a plausible
default would corrupt every number computed downstream, so gaps are recorded as gaps.

## What was found

530 strategy blocks. None is backtestable exactly as taught. The strictest 33 reduce to 25 that
need 2 to 6 invented parameters each, and 8 that cannot be tested at all.

See [TRIAGE.md](TRIAGE.md) for the full breakdown, the ranked shortlist, and the instrument
mismatch between this channel (stocks, forex, futures) and the crypto data in this repository.

## Layout

| Path | Contents |
|---|---|
| `channel_index.tsv` | 267 videos: id, duration, classification, strategy count, title |
| `transcripts/` | Cleaned transcripts with 30-second timestamps, `<video_id>.txt` |
| `notes/` | Structured strategy note per video, `<video_id>.md` |
| `TRIAGE.md` | What can and cannot be tested, and what each candidate would cost in assumptions |
| `VERIFICATION_VERDICTS.md` | Per-candidate audit detail |
| `EXTRACTION_BRIEF.md` | Instructions the extraction agents ran under |
| `VERIFY_BRIEF.md` | Instructions the audit agents ran under |

Every rule in a note carries an `[MM:SS]` marker pointing back into the transcript, so any claim
here can be checked against the source without rewatching the video.

## Reproducing

Transcripts were fetched with `yt-dlp` (json3 captions, falling back to VTT), cleaned into
30-second paragraphs. YouTube rate-limits bulk caption fetching; the `tv` player client and
2 concurrent workers got through the full channel where 5 workers on the default client did not.

## Status

Extraction and triage are complete. No backtest has been run, and no assumption set has been
chosen. Choosing those assumptions is the next decision, and it determines the results, so it
belongs in a written spec before any code runs.
