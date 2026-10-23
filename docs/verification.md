# Verification record · 23 October 2026

## Actual checks

- Python regression suite: 13 test methods pass, including all 20 proposal fixtures as subcases. Covers hours/boundaries/weekends/overnight, impossible budget, invalid model fields, valid simulated model parsing/ranking, rejection of invented venue IDs, API failure, deliberate offline mode, call cap, context reset, isolated sessions and HTTP input/origin validation. Tests force offline HTTP mode even if a local key exists.
- Fixed offline evaluation: 20/20 pass, including normal 11/11, refusal 3/3, edge 3/3 and multi-turn 3/3. Actual outputs are in `evaluation/results.csv`. These are synthetic automated fixtures, not live LLM or human acceptance results.
- JavaScript syntax check passes. Design skill preflight script reports zero hard violations and zero warnings.
- Automated Microsoft Edge browser checks on 1280px desktop and 390px mobile: proactive location question, recommendations, vegetarian refinement, refusal clears prior results, reset, no horizontal mobile overflow and no JavaScript page errors. Light and dark screenshots visually inspected. Browser-check tooling is optional and not needed to run the app.
- No paid model calls performed. Actual provider/model compatibility, live parsing quality, and credit consumption have not been verified.

## UI review

Design read: an Operate-mode campus tool for students, using familiar system typography and restrained green controls. Dials: variance 3, motion 1, density 5. No decorative motion is needed for this task. Dual light/dark themes follow system preference.

| Before | After | Why |
| --- | --- | --- |
| Intentional offline mode displayed an API failure notice | Disabled model bypasses the API stage cleanly | Makes the demo state accurate |
| Internal preference names and boolean values appeared in results | Readable prices, break duration and preference labels | Helps students understand their active filters |
| Generic singular/plural result wording | Count-aware wording | Reads correctly when only one venue qualifies |
| Message error lacked an input association | Message field references the error region | Supports assistive technology |
| Fluid heading typography | Fixed desktop/mobile sizes | Keeps app controls and hierarchy predictable |

## Design preflight

| Universal core check | Result |
| --- | --- |
| Mode, brief, intensity and system | Checked above |
| Redesign audit | N/A: new interface |
| No em dash in interface | Checked by preflight script |
| Single accent, coherent themes, radius | Checked in both screenshot themes |
| Contrast | Checked dark ink/light surfaces and reciprocal dark theme; native focus/inputs remain visible |
| Typography and button wrapping | Checked desktop and 390px mobile |
| Visible copy | Re-read, clarified raw preference names and count wording |
| Motion/reduced motion | N/A: no animation |
| Dark mode | Both themes rendered and inspected |
| Responsive layout | Single column at mobile; no horizontal overflow |
| Interaction/fetch states | Native controls, focus ring, disabled/loading button, inline error, empty/results states |
| Layout restraint | Dividers between recommendation rows, no card grids |
| Fake visuals | N/A: no illustrations |
| Numbers | Explicit synthetic-data notice; actual result counts derived from response |
| Generic visual patterns | System font, restrained controls, no gradients or decorative panels |
| Performance | Tiny static assets, no external resources or production JS framework; formal Web Vitals not measured |

| Operate check | Result |
| --- | --- |
| Familiar task interface | Building/time controls, labelled request, short result list |
| Typography | One system font family, fixed heading sizes, short reading columns |
| Restrained color/state vocabulary | Accent actions/focus, separate error text, tinted chat messages |
| Components and structural responsiveness | Native form elements, two columns become one; overlays N/A |
| Purposeful motion | N/A: no animation |
| No decorative component invention | Checked; no custom scrollbars, dialogs or ornament |
| Familiar conventions | Native select, date-time input and form submission |
| Interactive state cycle | Text loading/disabled state, inline failure and useful empty state; skeletons N/A: short text results |
| Form labels/errors | Labels above fields; message error below form with ARIA association |
| Z-index restraint | N/A: no layers |

Keyboard focus styling is present; a comprehensive screen-reader audit and independent student usability review remain pending.
