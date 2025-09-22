# Refactoring Guidelines and Best Practices

Based on code review feedback and refactoring of the factions module.

## Summary of Today's Refactoring

We successfully refactored the factions module to improve code quality, memory efficiency, and test coverage. Key improvements included:

1. **Simplified code complexity** by removing unnecessary helper functions and using built-in Python methods
2. **Optimized memory usage** by implementing in-place DataFrame modifications
3. **Fixed test architecture** to test actual functions instead of reimplementations  
4. **Added comprehensive I/O and integration tests** for complete pipeline coverage
5. **Improved code clarity** with better naming and type hints

## Guidelines for Better and More Efficient Code

### 1. Use Built-in Python Methods Effectively

**✅ DO:** Use `dict.get()` with default values for lookups
```python
# Good - Simple and clear
abbreviation = FACTION_ABBREVIATIONS.get(faction_name, faction_name)
```

**Why:** Python's built-in methods are optimized and reduce code complexity. No need to wrap simple operations in helper functions.

### 2. Optimize Memory Usage with In-Place Operations

**✅ DO:** Modify DataFrames in-place when the original data isn't needed
```python
def process_data(df: pd.DataFrame) -> None:
    """Modifies DataFrame in-place."""
    df["new_column"] = df["old_column"].apply(transform)
```

**Why:** Avoids unnecessary memory allocation for copies, especially important for large datasets in data pipelines.

### 3. Keep Exception Handling Simple and Pragmatic

**✅ DO:** Use general exception handling unless specific handling is needed
```python
try:
    process_data()
except Exception as e:
    logger.error(f"Error processing data: {e}")
    return False
```

**Why:** Multiple specific exception handlers without different handling logic add complexity without value.

### 4. Write Tests That Test Actual Code

**✅ DO:** Import and test the actual functions from your codebase
```python
from open_discourse.steps.factions.create import extract_unique_factions

def test_extract_unique_factions():
    result = extract_unique_factions(test_data)  # Test the real function
    assert expected == result
```

**Why:** Tests must validate the actual implementation to catch regressions. Reimplementing functions in tests defeats their purpose.

### 5. Test the Full Stack Including I/O Operations

**✅ DO:** Include tests for file operations and data persistence
```python
def test_pickle_roundtrip():
    """Test that data survives save/load operations."""
    save_pickle(test_df, tmp_path, logger)
    loaded_df = load_pickle(tmp_path, logger)
    pd.testing.assert_frame_equal(test_df, loaded_df)
```

**✅ DO:** Test main() orchestration functions with mocked paths
```python
def test_main_function():
    with patch('module.path') as mock_path:
        mock_path.INPUT_DIR = temp_dir / "input"
        result = main(None)
        assert result is True
```

**Why:** I/O operations are common failure points in data pipelines and need testing coverage.

### 6. Use Clear, Purpose-Driven Variable Names

**✅ DO:** Name variables by their content, not their type
```python
# Good
factions = df.loc[df["type"] == "Fraktion", "name"]

# Avoid
factions_series = df.loc[df["type"] == "Fraktion", "name"]
```

**Why:** Types are evident from context or IDE hints; names should describe the data's purpose.

### 7. Add Type Hints for Better Code Documentation

**✅ DO:** Include return type annotations for all functions
```python
def main(task) -> bool:
    """Main orchestration function."""
    return True
```

**Why:** Type hints improve code readability, enable better IDE support, and help catch type-related bugs early.

### 8. Log Errors for Debugging

**✅ DO:** Add error logging for unexpected failures
```python
if data is None:
    logger.error(f"Failed to load data from {file_path}")
    return False
```

**Why:** Clear error messages make debugging production issues much easier.

### 9. Use Pythonic Patterns

**✅ DO:** Use `enumerate()` for index-value iteration
```python
# Good
for idx, value in enumerate(items):
    process(idx, value)
```

**✅ DO:** Use sets for tracking unique items
```python
# Good
missing_items = set()  # Automatically handles duplicates
```

**Why:** Pythonic patterns are more readable, efficient, and less error-prone.

### 10. Structure Tests Comprehensively

**✅ DO:** Organize tests to cover:
- Unit tests for individual functions
- Integration tests for complete workflows  
- I/O tests for file operations
- Parametrized tests for multiple scenarios
- Error case handling (where appropriate)

**Why:** Comprehensive test coverage catches bugs early and provides confidence when refactoring.

## Key Takeaways

1. **Simplicity over complexity** - Don't create abstractions for simple operations
2. **Memory efficiency matters** - Use in-place operations for large data processing
3. **Test the real code** - Never reimplement functions in tests
4. **Test the full stack** - Include I/O and orchestration in test coverage
5. **Write self-documenting code** - Use clear names and type hints
6. **Be pragmatic** - Don't over-engineer error handling or abstractions

## Applied Refactoring Patterns

- **Remove Middle Man:** Eliminated unnecessary helper functions
- **Inline Method:** Replaced `_get_abbreviation()` with direct `dict.get()`
- **Replace Magic with Query:** Used explicit None checks instead of string comparisons
- **Consolidate Duplicate Conditional:** Simplified exception handling
- **Rename Variable:** Removed type suffixes from variable names
- **Add Parameter Type Hints:** Added return type annotations

These guidelines help create maintainable, efficient, and well-tested code that's easy for teams to work with and build upon.