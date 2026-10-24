# How scoring works

Each round is ranked by **final profit after costs**. Fees, futures unlocks,
auction payments and research spending all reduce that profit.

The number of teams is **not fixed**. For each round, let **N** be the number
of teams included in that round's results:

**Round points = N − your round rank + 1.**

| Round place | Points |
| --- | --- |
| 1st | N |
| 2nd | N − 1 |
| 3rd | N − 2 |
| Last (Nth) | 1 |

**Overall score = points added across all seven rounds.** Every round has the
same weight, including the final. If the same N teams play every round, the
maximum is **7 × N points**. A bigger profit does not add extra points beyond
that round's rank.

The roster is captured when the organizer starts each round. Registering
another team later does not recalculate points from completed rounds. No
recorded result for a round means zero points for that round. A registered
team's bot making no trades can still have a valid zero-profit result; it is
ranked normally, including above teams with losses.

## Ties

- **Within a round:** equal final profits, measured to the cent, share the same
  rank and points. Places after a tie skip the occupied positions. For example,
  places `1, 2, 2, 4` earn `N, N−1, N−1, N−3` points.
- **Overall:** equal point totals are broken by total final profit across the
  rounds. If those profits are also equal, teams share the overall place.
  Team names or IDs do not decide a competitive tie.

For the same roster, finishing first then third earns `N + (N−2)` points.
Two second-place finishes earn `(N−1) + (N−1)`, the same total. If teams remain
tied at the end, their total final profit determines the higher overall place.

Live profit and delayed rankings are provisional. Points are awarded at the
**official round close**. The dashboard then shows your round points and the
updated overall ranking. An organizer-aborted round does not count.
