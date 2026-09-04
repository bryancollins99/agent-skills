Mines your own notes folder for content ideas: mostly recent material, plus a few deliberately resurfaced older notes. Ideation only. It never drafts.

## Purpose

Most people point an AI at their notes and ask it to write something. That is the wrong job. The draft comes back sounding like an impression of you, and the actual value of a few thousand accumulated notes goes untouched.

The value is retrieval. You wrote something two years ago that answers the thing you are stuck on this week, and you have forgotten it exists. No amount of careful tagging fixes that, because the connection is semantic and you did not know to make it at the time. That is the one job an agent reading a whole folder at once is genuinely better at than you are.

So this skill finds and cites. You write.

The second thing it fixes is that ideation without memory degrades. Run any "give me ten ideas" prompt weekly with no record and you get the same six ideas every time, because the same notes are the most findable. This writes a dated ledger and reads the previous ones, so each run has to work harder than the last.

## When to use

- Weekly or fortnightly, when you need a queue of things to write rather than one thing to write now.
- When you have a folder of notes, work logs or journals you have stopped mining.
- After a stretch of building, when the lessons are still in the log and have not been written up.

Not for drafting. Not for research on a topic you have no notes about. If you already know what you want to write, this is the wrong tool.

## Steps

1. **Establish the folder and the window.** Ask once for the notes directory if it is not obvious, then work from there regardless of the current working directory. Default window is 90 days: `date -v-90d +%Y-%m-%d` on macOS, `date -d '90 days ago' +%Y-%m-%d` on Linux.

2. **Mine the recent window for most of the list.** Rank the sources by yield, not by tidiness:

   - **A work log or daily journal file is almost always the richest seam.** If entries are already shaped as "what I did, and what it taught me", the lesson clause is the idea, already written. Check whether entries are newest-first or oldest-first before you start walking, and check whether the date headers carry a year.
   - **Files modified in the window**, minus the noise: `find . -name '*.md' -not -path './.git/*' -mtime -90`. Exclude imported highlights, generated output, scripts and media directories.
   - **Anything already shaped as a brief or an idea file**, by whatever naming convention you use.

   Glob each pattern separately. In zsh, a single non-matching pattern in a multi-pattern `ls` aborts the whole command and returns nothing, so `ls Idea-*.md Draft-*.md` silently yields nothing at all when only the second has no matches.

3. **Deliberately resurface a few older notes.** Take the two or three dominant themes from step 2, then search outside the window for notes that speak to them and were never used. This is the part that justifies the whole exercise, so do not let it become a token gesture.

   An old note earns a slot only if you can name the **current thread it connects to**: "this note from two years ago is the missing frame for the thing you shipped last week". A note that is merely old and unused is not an idea. Cut it and take another from the recent window instead.

4. **Separate drafted from surfaced, and treat them completely differently.** Conflating these two states is what ruins the skill on its third run.

   - **Drafted** - a draft file for it already exists. May still appear, but only as a flagged re-cut, and a re-cut must target a different format than the one it was drafted for. Cap re-cuts at two of ten. Ten things you already wrote, re-badged, is the failure mode.
   - **Surfaced but unwritten** - it appeared in an earlier ledger and no draft exists. Fully eligible, unrestricted, and it does not count against the re-cut cap. Label it as carried over.

   Retiring surfaced-but-unwritten ideas feels like good hygiene and quietly destroys the output. After a month every strong candidate in the folder is "previously surfaced", and the list degrades to the bottom of the barrel by construction. An unwritten idea is pending, not spent.

5. **Output the list and stop.** For each idea: the format, the angle in one sentence, the one load-bearing specific it rests on, and the source file it came from.

   Two rules do most of the work here. **Every number is lifted from a file, never recalled** - if you cannot point at the line, drop the number or drop the idea. And **one hard specific per idea**: a concrete artefact, a count, a bill, a failure, leading to one generalisable lesson. An idea with a lesson and no artefact is a platitude with a source citation.

   Spread across themes. Ten variations on one insight is one idea, not ten.

6. **Write a dated ledger** to the same folder, at the top level rather than in a subfolder, recording every idea with its state tag. This is what the next run reads. Then close with one line telling the user what to run when they want something drafted, and stop. No summary, no offer to expand, no sample opening line.

## Failure modes

- **File modification time is not authorship time.** Any bulk operation stamps every file at once: a sync migration, a mass find-and-replace, an export and re-import, a `git clone`. Every note then appears to have been written on the same day and your 90-day window becomes meaningless. Date a note from a date line inside the file, or from `git log -1 --format=%ad -- <file>`. Never from `mtime` alone. Check this before the first run: if hundreds of files share one mtime, you have found it.

- **Private journals are theme signal only.** If the folder mixes work notes with a personal journal, read the journal to see what the person keeps circling back to, then source the actual idea from a work note. Never surface a personal entry as a content idea, and never write to that file.

- **The subfolder problem.** Output written to a nested directory is output the user never sees. They work from the top level. Write the ledger there, and if a previous run buried one, move it rather than leaving two conventions in play.

- **Drafting is not a bonus.** The pull to write "just the opening line" is strong and it is the single thing that makes this skill worthless. If an idea is good, its reward is a place on the list.

- **Do not let the agent tidy the folder mid-run.** Renaming, retagging and reorganising notes is a separate job with separate risk. Ask before touching a single file. It is worth confirming the folder is backed up or version controlled before any run that will write to it.
