# IDTAP Query System Examples

This folder contains example scripts demonstrating how to use the IDTAP Python query system.

## Files

### `query_examples.py`
Comprehensive examples showing different query types and usage patterns:
- Basic trajectory queries
- Pitch-based queries  
- Vowel and consonant queries (for vocal transcriptions)
- Multiple query coordination (AND/OR logic)
- Trajectory sequence pattern matching
- Duration filtering
- Result serialization for cross-platform compatibility

### `explore_transcription.py`
Utility script to explore a transcription's structure and content:
- Analyzes available vowels, consonants, and trajectory types
- Shows frequency statistics for different musical elements
- Helps identify realistic query targets
- Tests common query patterns with actual data

## Usage

Run examples from this directory:

```bash
cd examples

# Run comprehensive query examples
python query_examples.py

# Explore a specific transcription
python explore_transcription.py
```

## Requirements

- Valid IDTAP account and authentication
- Access to transcription data (either through API or local files)
- Replace the example transcription ID with actual IDs from your account

## Notes

These examples use the test transcription ID `645ff354deeaf2d1e33b3c44` (a vocal recording suitable for consonant/vowel testing). You may need to:

1. Replace with transcription IDs from your own account
2. Adjust query parameters based on your transcription content
3. Handle authentication as needed

The examples demonstrate the full capability of the query system while maintaining exact compatibility with the TypeScript web application.