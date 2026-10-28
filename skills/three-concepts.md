Redesigns a multi-step flow (sign up, onboarding, checkout, upgrade) by asking the agent for three concepts per step, each grounded in a real product's design, and delivers them as one local HTML file you can visually QA before any code changes.

## Purpose

Ask an agent to "improve the sign up flow" and you get one design that looks like every other AI design, and you go down that rabbit hole until it is too late to compare it with anything.

This skill exists because of one run on a three-stage funnel (land from search, give an email, upgrade to paid). Forcing three concepts per stage, each copied from a named real product through a design reference library, made the bad ideas visible before they were built: a chatbox layout borrowed from a copywriting tool clearly did not suit a site about public tenders, and a newspaper-style paywall looked wrong at a glance. The winners were picked by eye in minutes, then simplified, then shipped.

## When to use

- Any flow with two or more steps where conversion matters: sign up, lead capture, onboarding, paywall, upgrade.
- When earlier AI design output for the project looked generic.
- Before touching the production templates, not after.

Not for single components with an obvious design, and not for flows you cannot see (backend-only changes).

## Steps

1. **Map the flow as stages.** One line per stage: who arrives, what they see, the one action you want. Confirm the stage list with the user before designing anything.

2. **Load the evidence.**
   - Traffic: export the last three months of search queries and landing pages (Search Console or your analytics) and hand the agent the file. It should name which pages feed the flow and where visitors drop.
   - Design references: connect a design reference library (Mobbin and similar tools ship an MCP) so the agent can cite real screens. If none is available, ask the user for 3-5 product URLs per stage instead. Do not let the agent design from memory alone; that is the generic output this skill exists to avoid.

3. **Ask for three concepts per stage.** Each concept names the real product it is based on, links the reference screen, and states in one line why that pattern fits this audience. The three must differ in approach, not just colour (for example: blurred content behind a social sign in, a conversational prompt, a metered paywall).

4. **Deliver one HTML file for visual QA.** All stages, all concepts, side by side, with the reference links clickable. Open it locally. No changes to the real site at this point.

5. **The user picks per stage, then simplify.** Collect one pick per stage (mixing is fine: A, A, B). Expect the first drafts to be busy. Feed back cuts in plain words, by voice if that is faster: remove boxes that do not drive the action, shorten preambles, keep the stages visually consistent with each other.

6. **Regenerate the simplified file, re-check, then implement.** Only once the user signs off on the simplified file does the agent edit the real templates. Ship to one page first, check it live, then roll out to the other pages from step 2.

## Failure modes

- **Concepts converge.** Three versions of the same layout is one concept. Reject and ask for three different patterns from three different products.
- **References are invented.** If the agent cannot link the real screen, the concept is not grounded. Spot-check every link before picking.
- **Borrowing the wrong audience.** A pattern that works for a consumer chat app may confuse a B2B buyer. Judge each concept against who actually lands on the page, not against how polished the reference looks.
- **Busy first drafts.** The agent adds stats boxes, preambles and extra tabs. Plan for at least one simplification round.
- **Inconsistent stages.** Each stage picked in isolation can look like a different site. Check the chosen concepts together before implementing.
- **Skipping the HTML step.** Iterating on a visual flow in a terminal is slow and blind. The local file is the whole point.
