Generates a large batch of business ideas against your own constraints, scores each on VRIO plus personal fit, and builds an interactive dashboard you can filter, sort and turn into build prompts.

## Purpose

Ask an AI for business ideas and you get a list anyone could have got: generic, unranked, and blind to what you already own. The list is not the useful part. The ranking is, and so is the bottom of the list, where the model tells you which of your pet ideas are a personal itch rather than a business.

This skill exists because of one run that produced 104 ideas from a prompt asking for 101, ranked them out of 100, and concluded that the two best ideas should ship as paid features on a site already running, not as new brands that would spend months waiting for traffic. That conclusion was worth more than any single idea on the list, and it only appeared because the prompt forced the model to weigh what the user already has.

## When to use

- Once a quarter, or whenever you feel the pull to start something new and want it checked against what you already run.
- When you have a pile of half-ideas in notes and no way to compare them.
- Before committing build time to a new project.

Not for validating one idea you have already decided on. Not for market sizing. The scores are a sort order, not a forecast.

## Steps

1. **Collect the constraints before writing the prompt.** Ask the user, one line each, and skip what memory or a profile file already answers:
   - Team size they will tolerate (default: solo or near-solo).
   - Market or geography they want to win in, and why.
   - Proprietary data, APIs or access they have that a competitor would not.
   - Existing sites, products or audiences the ideas may build on.
   - Traits and dislikes: what they will not do (sales calls, support, hardware, ads).

2. **Write the generation prompt.** Role: business strategist. Task: N online projects, products or SaaS businesses the user could build lean with AI coding. Hard criteria: the constraints above, plus "proven in another market" so every idea names a working comparable elsewhere. Scoring: VRIO for each idea.
   - **Valuable** - does the market want it, will it make money.
   - **Rare / realistic** - can this user actually build and run it.
   - **Inimitable** - can a competitor copy it in a weekend.
   - **Organised** - does the user have the skills, tools and time to execute.
   Tell the model explicitly not to limit itself to existing projects, and separately to say when an idea belongs on an existing asset instead.

3. **Ask for the output as an interactive dashboard**, single HTML file, with per idea: name, one-line summary, the comparable in another market, local competition (or "none found"), suggested price, the angle, category, VRIO sub-scores and a total out of 100. Filters by category and by "builds on something you own". Sort by score. A shortlist band at the top. A list of every external source link at the bottom.

4. **Run it once at high effort, then iterate in the same conversation.** Expect two or three rounds of correction. Feed back anything wrong about the user's situation rather than starting over; the model's grasp of the constraints is what improves between rounds.

5. **Read the bottom of the list before the top.** The low scorers with an explanation are where the model tells the user what not to build. Surface those reasons to the user in plain words.

6. **Turn the shortlist into build prompts.** For each shortlisted idea that builds on an existing project, write one investigator prompt: the ground rules (read the repo first, check what already exists, no build until a plan is agreed), then the idea-specific question. These go into a coding agent opened in that project's repo, and the first output is a requirements doc, not code.

## Failure modes

- **The count will be wrong.** Ask for 101 and you may get 104 or 96. Count the rows in the dashboard before quoting a number anywhere.
- **It is expensive.** A max-effort run with a few correction rounds used about half a week's allowance of the top model in the run this skill came from. Do it rarely and do it once properly; do not re-run from scratch to tweak wording.
- **Comparables and competitor claims can be invented.** "Proven in another market" is only useful if the comparable exists. Spot-check the shortlisted ideas' comparables and the source links before acting on any of them. "No local competition" means the model found none, not that there is none.
- **Personal fit needs real input.** Without memory or a written profile, the model scores fit against an imagined user. Give it the constraints in step 1 explicitly, especially the dislikes.
- **Scores are a sort order.** An 89 is not twice as good as a 45 and is not a prediction. Use the scores to choose what to investigate next, never as the decision.
- **Swap the localisation out.** The criteria are only as good as their fit to the user. A prompt written for one country, one data set and one person's traits will produce confident nonsense for someone else.
