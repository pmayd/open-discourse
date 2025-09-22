# Wikidata Geographic Queries for Political Analysis

This document provides practical SPARQL queries for determining if politicians were born in specific German states (like Bavaria) using Wikidata.

## High-Level Pattern

Totally doable at a high level—here's the pattern you want, no code needed.

### Goal
From a list of your politicians' **Wikidata QIDs**, flag who was **born in Bavaria** (and optionally who was born in **Germany**).

### The Wikidata facts you'll rely on
* Person → **place of birth** = property **P19**
* Place → **is in administrative unit** = property **P131** (follow recursively "up" the map)
* Place → **country** = property **P17**
* Bavaria = item **Q980**; Germany = item **Q183**
* "Federal state of Germany" class = **Q1221156** (handy if you want any German state)

### Query logic (conceptual)
1. **Input**: your QIDs (the politicians). Feed them to Wikidata in a single query using a list parameter (you'll chunk if the list is very large).
2. **Fetch birthplace**: for each person, read **P19 → birthplace** (a place QID).
3. **Climb the hierarchy**: from that birthplace, repeatedly follow **P131** upward (city → district → state → …).
4. **Test Bavaria**: if **any ancestor via P131** equals **Q980 (Bavaria)**, mark the person "born in Bavaria = true".
5. **Test Germany (optional)**:
   * EITHER check the birthplace's **P17** is **Q183 (Germany)**,
   * OR (more robust) allow **P17** on any ancestor you reach while following **P131**.
6. **Return**: person QID, person label, birthplace label, matched **state** (e.g., Bavaria) and **country**, plus boolean flags: `born_in_bavaria`, `born_in_germany`.

### Practical notes
* **Ambiguities**: Some birthplaces share names with districts (e.g., "Regensburg" the city vs. the district). The hierarchy step fixes this—only the city rolls up to Bavaria as a **state**; record which **state** item you matched.
* **Edge cases**:
  * **City-states** (Berlin, Hamburg, Bremen) will resolve directly to their own state items (not Bavaria).
  * **Historical borders**: Decide policy—use **present-day** administrative chains (simplest) unless you need time-of-birth borders.
  * **Missing P19**: leave as unknown; don't infer "from Germany" via citizenship unless you explicitly want that as a separate flag.
* **Scale/performance**: Send IDs in batches (thousands per call is fine), cache results. Place hierarchies change rarely—refresh monthly/quarterly.
* **Quality control**: Randomly spot-check a few outputs: birthplace → state should equal Bavaria, and country should equal Germany for Bavarian cases.

### If sometimes you only have a city string (e.g., "Regensburg")
Resolve the string to a **place QID** first (prefer items that are **instance of** city/municipality), then run the same hierarchy test. Keep a confidence score if multiple candidates exist.

**Summary**: "P19 to get the place, P131* to see if it rolls up to Q980 (Bavaria), P17 to confirm Germany if needed," done at scale over your list of QIDs.

## Assumption
You already have Wikidata IDs for your politicians and need to determine their geographic origins.

## SPARQL Implementation

Following the conceptual approach above, here are the practical SPARQL queries:

### Complete Analysis Query (Recommended)
```sparql
SELECT ?politician ?politicianLabel ?birthplace ?birthplaceLabel ?state ?stateLabel ?country ?countryLabel
       (IF(?state = wd:Q980, true, false) AS ?born_in_bavaria)
       (IF(?country = wd:Q183, true, false) AS ?born_in_germany) WHERE {

  # Your politicians (replace with actual Wikidata IDs)
  VALUES ?politician { wd:Q123456 wd:Q789012 wd:Q345678 }

  # Get birthplace (P19)
  ?politician wdt:P19 ?birthplace .

  # Climb hierarchy to find state (P131* = recursive administrative units)
  ?birthplace wdt:P131* ?state .
  ?state wdt:P31 wd:Q1221156 .  # Instance of "German federal state"

  # Get country (P17 or via hierarchy)
  OPTIONAL {
    { ?birthplace wdt:P17 ?country . }
    UNION
    { ?state wdt:P17 ?country . }
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" . }
}
```

### Bavaria-Only Filter (Faster)
```sparql
SELECT ?politician ?politicianLabel ?birthplace ?birthplaceLabel WHERE {
  VALUES ?politician { wd:Q123456 wd:Q789012 wd:Q345678 }

  # Use property path: birthplace via P19, then walk up P131+ to find Bavaria
  ?politician wdt:P19/wdt:P131* wd:Q980 .  # P19 → P131+ → Q980 (Bavaria)
  ?politician wdt:P19 ?birthplace .  # Also get the actual birthplace for display

  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" . }
}
```

### Two-Step Approach for Large Datasets

**Step 1: Get All Birthplaces and States**
```sparql
SELECT ?politician ?birthplace ?birthplaceLabel ?state ?stateLabel WHERE {
  VALUES ?politician { wd:Q123456 wd:Q789012 wd:Q345678 }
  ?politician wdt:P19 ?birthplace .
  ?birthplace wdt:P131* ?state .
  ?state wdt:P31 wd:Q1221156 .  # German federal state
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" . }
}
```

**Step 2: Filter Results in Your Application**
- Check if `?state` equals `wd:Q980` (Bavaria) → `born_in_bavaria = true`
- Batch this for better performance with large politician lists

## Key Wikidata Properties

- **P19**: Place of birth
- **P131**: Located in administrative territorial entity
- **P131***: Transitive property (goes up the hierarchy)
- **Q980**: Bavaria (Wikidata ID)
- **Q1221156**: German federal state

## Practical Implementation Steps

Following the conceptual pattern outlined above:

### Recommended Workflow
1. **Collect politician Wikidata QIDs** from your database
2. **Batch query Wikidata** using VALUES clause (chunk large lists)
3. **For each politician**: P19 → birthplace → P131* → state → check if Q980 (Bavaria)
4. **Return boolean flags**: `born_in_bavaria`, `born_in_germany`
5. **Cache results** locally (place hierarchies rarely change)

### Alternative: Build Geographic Cache
1. **Extract unique birthplace QIDs** from your politician data
2. **Query all states** for these birthplaces in one batch
3. **Create lookup table**: Birthplace QID → State QID
4. **Apply Bavaria filter** (State QID = Q980) to your politician data

## Handling Edge Cases

### Historical Boundaries
```sparql
# Time-aware query for historical Bavaria
SELECT ?politician ?birthplace WHERE {
  ?politician wdt:P19 ?birthplace .
  ?politician wdt:P569 ?birthDate .  # Birth date

  # Check administrative entity at birth time
  ?birthplace p:P131 ?statement .
  ?statement ps:P131 wd:Q980 .  # Was in Bavaria
  OPTIONAL { ?statement pq:P580 ?startTime . }  # Start time
  OPTIONAL { ?statement pq:P582 ?endTime . }    # End time

  # Ensure the period overlaps with birth date
  FILTER(!BOUND(?startTime) || ?startTime <= ?birthDate)
  FILTER(!BOUND(?endTime) || ?endTime >= ?birthDate)
}
```

### Multiple Administrative Levels
```sparql
# More specific: born in Bavaria vs. representing Bavaria
SELECT ?politician ?birthplace ?constituency WHERE {
  ?politician wdt:P19 ?birthplace .        # Birthplace
  ?politician wdt:P768 ?constituency .     # Electoral district

  # Both in Bavaria
  ?birthplace wdt:P131* wd:Q980 .
  ?constituency wdt:P131* wd:Q980 .
}
```

## Python Implementation Strategy

### The Clean Approach

**Run one SPARQL query from Python** against the Wikidata Query Service (WDQS). You can do this with:

* **SPARQLWrapper** (lightweight client; easiest)
* or plain **requests** (POST the query URL)
* (Optional) **qwikidata** if you prefer its helpers, but it's not required.

### What the Query Does (Conceptually)

* **Input**: your list of politician QIDs (VALUES block).
* **Fetch birthplace**: `P19`.
* **Walk up the admin tree**: from birthplace, follow `P131+` (one-or-more hops: city → district → state → …).
* **Check Bavaria**: return a flag when one of those ancestors **is Bavaria (Q980)**.
* **Optionally check Germany**: either birthplace or any ancestor has **country (P17) = Germany (Q183)**.
* **Labels**: ask WDQS to return German/English labels so you can display "Regensburg," "Bayern," etc.

### Python Workflow (No Code)

1. **Chunk your QIDs** (e.g., 200–500 per batch) to stay polite to WDQS.
2. **POST the SPARQL**; include a descriptive User-Agent.
3. **Parse the JSON** into a dataframe with columns like:
   * `person_qid`, `person_label`, `birthplace_qid`, `birthplace_label`,
   * `birth_state_qid`, `birth_state_label`,
   * booleans: `born_in_bavaria`, `born_in_germany`.
4. **Cache results** so you don't re-query WDQS each run.
5. **Join with your speeches** on `person_qid` and filter by date (e.g., 2025).

### When You Only Have a City String (like "Regensburg")

Before the main query, **resolve strings to place QIDs** using the Wikidata entity search API (`wbsearchentities`) constrained to German places. Prefer items whose **instance of (P31)** is city/municipality. Save the mapping in a reference table so you only resolve once.

### Practical Tips

* Use the property path **`P19 / P131+`** to test Bavaria (Q980).
* If you need provenance, also pull the **statement ID** for P19 (so you can audit later).
* Rate limits: pause between batches; WDQS is shared infrastructure.
* Decide upfront whether you use **present-day borders** (most common) or borders at time of birth.

## Complete Implementation Workflow

### End-to-End Process
1. **Input**: List of politician Wikidata QIDs from your database
2. **Batch Processing**: Chunk QIDs into groups of 200-500
3. **SPARQL Query**: Use the "Complete Analysis Query" above with VALUES clause
4. **Parse Results**: Extract boolean flags `born_in_bavaria` and `born_in_germany`
5. **Cache Data**: Store results locally to avoid re-querying
6. **Analysis**: Filter speeches by Bavarian politicians using these flags

### Performance Optimization
- **Batch queries** in chunks of 200-500 QIDs per SPARQL call
- **Cache results** locally (place hierarchies change rarely)
- **Rate limiting**: Pause between batches to respect WDQS
- **Refresh** cached data monthly/quarterly
- **Monitor timeouts** for very large datasets

### Quality Control
- **Spot check** random results: birthplace → state should be consistent
- **Validate** that Bavarian politicians show country = Germany
- **Handle missing data** gracefully (some politicians may lack P19)
- **Log ambiguities** for manual review if needed

## Common German State Wikidata IDs

- **Q980**: Bavaria (Bayern)
- **Q1198**: Baden-Württemberg
- **Q1208**: Berlin
- **Q1204**: Brandenburg
- **Q1205**: Bremen
- **Q1202**: Hamburg
- **Q1199**: Hesse (Hessen)
- **Q1196**: Lower Saxony (Niedersachsen)
- **Q1207**: Mecklenburg-Western Pomerania
- **Q1206**: North Rhine-Westphalia
- **Q1200**: Rhineland-Palatinate
- **Q1201**: Saarland
- **Q1202**: Saxony (Sachsen)
- **Q1203**: Saxony-Anhalt
- **Q1204**: Schleswig-Holstein
- **Q1205**: Thuringia (Thüringen)

## Example Result
This approach gives you a clean Boolean result: "Is this politician born in Bavaria?" that you can then use to filter your speech analysis data for queries like "All speeches by Bavarian politicians in 2024".