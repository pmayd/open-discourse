# Wikidata Integration Analysis Plan

This document outlines a strategy for analyzing parliamentary speeches by geographic origin using Wikidata IDs and geographic data.

## Problem Statement

Given:
- Parliament members with Wikidata IDs
- Speech data (who said what when)
- Birth city information (e.g., "Regensburg")

Goal: Enable queries like "All representatives from Bavaria who spoke in the Bundestag this year"

## Overall Strategy

### 1. Data Enrichment Pipeline
- **Wikidata ID Mapping**: Create a mapping table linking politician UIDs to Wikidata IDs
- **Geographic Resolution**: Use Wikidata's geographic hierarchy to resolve cities to states
  - "Regensburg" → Bavaria via Wikidata property chains
  - Handle historical boundaries (some cities changed states)
  - Cache the city→state mappings for performance

### 2. Three-Layer Architecture

**Layer 1: Base Data** (existing)
- Speech content with politician_id, date, session
- Politicians table with names and basic info

**Layer 2: Wikidata Bridge** (new)
- politician_id ↔ Wikidata ID mapping
- Cached geographic hierarchies (city → district → state)
- Additional properties from Wikidata (party affiliations, education, etc.)

**Layer 3: Analysis Layer** (query interface)
- Filter by geographic origin (state, region, city)
- Filter by time period
- Combine with existing gender, faction filters

### 3. Geographic Challenge Solutions

**Problem**: Only having city names like "Regensburg"

**Solution**:
- Query Wikidata for each city's administrative hierarchy
- Build lookup table: City → Federal State
- Handle ambiguous city names (multiple cities with same name)
- Consider historical changes (cities that moved between states)

### 4. Query Workflow

For "All Bavarian representatives who spoke in 2024":
1. Identify all cities in Bavaria via Wikidata
2. Match politicians born in those cities
3. Filter speeches by those politician IDs + year 2024
4. Aggregate results (count speeches, analyze topics, etc.)

### 5. Implementation Approach

**Option A: Extend Current Pipeline**
- Add Wikidata fetching step after politicians data
- Store enriched data in new tables
- Modify analysis modules to use geographic filters

**Option B: Separate Analysis Service**
- Keep main pipeline unchanged
- Build standalone service that queries Wikidata on-demand
- Join with existing data at analysis time

### 6. Key Considerations

**Performance**:
- Cache Wikidata queries (cities rarely change states)
- Batch API calls to Wikidata
- Pre-compute common geographic groupings

**Data Quality**:
- Handle missing Wikidata IDs
- Validate geographic matches
- Account for politicians born abroad
- Consider constituency vs. birthplace

**Flexibility**:
- Make geographic hierarchy configurable (city/district/state/country)
- Allow multiple geographic filters (born in X, represents Y)
- Time-based filters (speeches in specific periods)

## Example Use Cases

This approach would enable complex queries like:

- "Show all speeches by East German-born politicians after reunification"
- "Compare speaking time between urban vs. rural representatives"
- "Track migration patterns of politicians (birthplace vs. constituency)"
- "Analyze regional dialect usage in parliamentary speeches"
- "Find correlation between university education location and policy positions"

## Implementation Details

### Wikidata ID Mapping Strategy

#### Automatic Matching Approaches
- **Name-based matching**: Query Wikidata for politicians with matching first/last names + birth dates
- **Fuzzy matching**: Handle name variations (nicknames, umlauts, hyphenated names)
- **Contextual matching**: Use additional data points (party affiliation, electoral terms, positions held)
- **Manual verification**: Flag uncertain matches for human review

#### Data Sources for Mapping
- **Abgeordnetenwatch.de**: Often has Wikidata IDs already
- **Wikipedia politician lists**: Cross-reference with existing politician data
- **Bundestag official records**: Match against known biographical data
- **Semi-automatic tools**: Use OpenRefine or similar for bulk matching

### Geographic Resolution Deep Dive

#### Wikidata Property Chain Strategy
For "Regensburg" → Bavaria:

**Step 1: City Identification**
- Query: `SELECT ?city WHERE { ?city rdfs:label "Regensburg"@de }`
- Handle multiple results (different Regensburgs exist)
- Use additional context (population size, administrative level)

**Step 2: Administrative Hierarchy Traversal**
```sparql
# Simplified SPARQL concept
SELECT ?state WHERE {
  ?city rdfs:label "Regensburg"@de .
  ?city wdt:P131+ ?state .  # "located in administrative territorial entity" (transitive)
  ?state wdt:P31 wd:Q1221156 .  # "instance of" "state of Germany"
}
```

**Step 3: Historical Boundary Handling**
- Use `wdt:P580` (start time) and `wdt:P582` (end time) properties
- Query historical administrative divisions
- Consider politician's birth year vs. city's administrative history

#### Caching Architecture

**Level 1: Static Mappings**
- Pre-built table: City Name → Wikidata ID → Current State
- Updated quarterly or when administrative changes occur
- Handle common variations and alternate spellings

**Level 2: Dynamic Resolution**
- Real-time Wikidata queries for unknown cities
- Cache results locally for future use
- Confidence scoring for ambiguous matches

**Level 3: Manual Override**
- Admin interface for correcting automatic matches
- Historical edge cases requiring human judgment
- Documentation of special cases

### Implementation Workflow

#### Phase 1: Baseline Mapping
1. **Export current politician data** (names, birth cities, dates)
2. **Bulk query Wikidata** for potential matches
3. **Score matches** based on multiple criteria:
   - Exact name match: +3 points
   - Birth date match: +3 points
   - Birth city match: +2 points
   - Party affiliation match: +1 point
4. **Flag uncertain matches** (score < 6) for manual review

#### Phase 2: Geographic Resolution
1. **Extract unique city names** from politician birth places
2. **Build city→state lookup table** via Wikidata SPARQL
3. **Handle ambiguities**:
   - Multiple cities with same name → use population/importance ranking
   - Historical changes → create time-based mappings
   - Missing data → flag for manual research

#### Phase 3: Integration
1. **Create bridge tables** in existing database
2. **Add geographic filters** to analysis modules
3. **Validate results** with known test cases

### Technical Challenges & Solutions

#### Challenge: Name Variations
- **Problem**: "München" vs "Munich", "Josef" vs "Joseph"
- **Solution**:
  - Query multiple language labels in Wikidata
  - Build synonym tables for common variations
  - Use fuzzy string matching (Levenshtein distance)

#### Challenge: Historical Administrative Changes
- **Problem**: Cities changing states, East/West Germany reunification
- **Solution**:
  - Time-aware queries using `wdt:P580`/`wdt:P582`
  - Separate mappings for different time periods
  - Document edge cases in metadata

#### Challenge: Data Quality
- **Problem**: Incomplete or incorrect Wikidata information
- **Solution**:
  - Confidence scoring for all matches
  - Manual verification workflow
  - Fallback to alternative data sources
  - Community contribution system for corrections

#### Challenge: Performance
- **Problem**: Real-time Wikidata queries are slow
- **Solution**:
  - Aggressive caching at multiple levels
  - Batch processing for bulk operations
  - Pre-computed common queries
  - Local Wikidata mirror for frequent access

### Quality Assurance Strategy

#### Validation Methods
- **Known test cases**: Politicians with verified Wikidata IDs
- **Cross-reference verification**: Compare against multiple sources
- **Statistical analysis**: Detect outliers and suspicious patterns
- **Community feedback**: Allow corrections from domain experts

#### Error Handling
- **Graceful degradation**: Analysis works even with partial data
- **Confidence indicators**: Show reliability of each match
- **Audit trails**: Track all automatic and manual changes
- **Rollback capability**: Undo problematic batch updates

## Implementation Notes

The key is building that Wikidata bridge layer that enriches existing data without disrupting the current pipeline. This maintains the non-intrusive design principle while adding powerful geographic analysis capabilities.

### Data Flow
```
Existing Pipeline → Wikidata Enrichment → Geographic Analysis
     ↓                      ↓                    ↓
Speech Content     +    City→State Maps    =   Regional Insights
Politicians Data        Wikidata IDs           Filtered Results
```

### Technical Requirements
- Wikidata SPARQL query capability
- Caching layer for geographic mappings
- Robust error handling for missing/ambiguous data
- Integration with existing analysis modules
- Confidence scoring system for data quality
- Manual override interface for edge cases