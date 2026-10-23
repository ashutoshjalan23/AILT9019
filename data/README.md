# Data provenance

All data in this folder was created as synthetic demonstration fixtures on 23 October 2026. Building labels refer to HKU locations, but no claim is made that the listed demo venues, floors, hours, prices, diet tags, walking links or minutes describe real facilities. No external dataset was downloaded. Every synthetic venue is named with a Demo prefix.

`canteens.json` stores opening intervals, cheapest/most expensive illustrative prices, cuisine and menu tags. Each entry inherits the dataset-level `last_updated` date. Weekday means Monday-Friday; weekend means Saturday-Sunday. Empty interval lists mean closed. Closing is exclusive; intervals may span midnight.

`walks.json` stores undirected building links and minutes; the engine computes shortest routes. These links are intentionally illustrative and cannot be used as real directions. Same-building walking time is zero and excludes finding the floor. The planner reserves 10 minutes for eating plus a return walk when a break duration is given.

To replace fixtures, preserve IDs/schema, mark `synthetic` accurately, record source URLs and field-level verification notes, update the snapshot date and check all routes. Review the evaluation expectations against the new data rather than reusing synthetic venue assertions unchanged. No supplied data implies allergen safety or medical suitability.
