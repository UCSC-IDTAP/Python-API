# IDTAP Python Query System

This document describes the newly implemented Python query system that provides exact compatibility with the TypeScript query system from the IDTAP web application.

## Overview

The query system allows sophisticated analysis of musical transcriptions, enabling users to search for specific patterns, characteristics, and sequences within Hindustani music recordings. The Python implementation maintains 100% data structure compatibility with the TypeScript version, allowing queries created in one system to work seamlessly in the other.

## Key Features

### 🎵 **Musical Element Queries**
- **Trajectory IDs**: Find specific melodic gesture types
- **Pitches**: Search for specific pitches or pitch ranges
- **Vowels & Consonants**: Analyze vocal articulations (vocal transcriptions only)
- **Pitch Sequences**: Find melodic patterns (strict or loose matching)
- **Trajectory Sequences**: Locate gesture patterns

### 🏗️ **Structural Analysis**
- **Phrase-level**: Query individual musical phrases
- **Group-level**: Analyze phrase groupings  
- **Section-level**: Find Alap, Composition, Improvisation sections
- **Sequence-level**: Analyze trajectory sequences and connections

### 🎭 **Categorization Queries**
- **Performance Sections**: Alap, Jor, Jhala, Bandish, etc.
- **Phrase Types**: Asthai, Antara, Mohra, Mukra, etc.
- **Elaboration Types**: Vistar, Tan, Laykari, Tihai, etc.
- **Articulation Types**: Bol, Aakar, Sargam, etc.

### ⚙️ **Advanced Features**
- **Multiple Query Coordination**: Combine conditions with AND/OR logic
- **Duration Filtering**: Filter by time duration constraints
- **Cross-Platform Serialization**: Full JSON compatibility with TypeScript
- **Flexible Segmentation**: Phrase, group, or trajectory-level analysis

## Quick Start

```python
from idtap import SwaraClient, CategoryType, DesignatorType

# Initialize client
client = SwaraClient()

# Simple trajectory query
results = client.single_query(
    transcription_id="your_transcription_id",
    category=CategoryType.TRAJECTORY_ID,
    trajectory_id=1,
    designator=DesignatorType.INCLUDES
)

print(f"Found {len(results.trajectories)} matching phrases")
for answer in results.query_answers:
    print(f"- {answer.title}: {answer.duration:.2f}s")
```

## Query Types

### Single Queries

```python
# Find phrases containing specific pitch
from idtap import Pitch
pitch = Pitch({"numberedPitch": 60})  # Middle C
results = client.single_query(
    transcription_id="...",
    category=CategoryType.PITCH,
    pitch=pitch
)

# Find vowel patterns (vocal only)
results = client.single_query(
    transcription_id="...",
    category=CategoryType.VOWEL,
    vowel="a",
    designator=DesignatorType.INCLUDES
)

# Find trajectory sequences
results = client.single_query(
    transcription_id="...",
    category=CategoryType.TRAJ_SEQUENCE_STRICT,
    traj_id_sequence=[1, 2, 1],
    segmentation=SegmentationType.SEQUENCE_OF_TRAJECTORIES,
    sequence_length=3
)
```

### Multiple Queries

```python
# Combine multiple conditions
queries = [
    {
        "category": CategoryType.TRAJECTORY_ID,
        "trajectory_id": 1,
        "designator": DesignatorType.INCLUDES
    },
    {
        "category": CategoryType.VOWEL,
        "vowel": "a", 
        "designator": DesignatorType.INCLUDES
    }
]

# Find phrases matching ALL conditions (intersection)
trajectories, identifiers, answers = client.multiple_query(
    queries=queries,
    transcription_id="...",
    every=True  # AND logic
)

# Find phrases matching ANY condition (union)  
trajectories, identifiers, answers = client.multiple_query(
    queries=queries,
    transcription_id="...",
    every=False  # OR logic
)
```

## Data Structure Compatibility

The Python query system maintains exact JSON compatibility with TypeScript:

```python
# Serialize query results
answer = results.query_answers[0]
json_data = answer.to_json()

# This JSON can be used directly in the TypeScript web app
# or sent between Python and TypeScript systems

# Deserialize from JSON
from idtap.query_types import QueryAnswerType
restored = QueryAnswerType.from_json(json_data)
```

## Core Components

### Files Structure
```
idtap/
├── query.py              # Main Query class
├── query_types.py        # Type definitions & enums
├── sequence_utils.py     # Sequence matching utilities
├── client.py            # SwaraClient with query methods
└── tests/query_test.py  # Comprehensive test suite
```

### Key Classes

- **`Query`**: Main query execution engine
- **`CategoryType`**: Enum of query categories (pitch, trajectory, vowel, etc.)
- **`DesignatorType`**: Query designators (includes, excludes, startsWith, endsWith)
- **`SegmentationType`**: Analysis segmentation types (phrase, group, sequence)
- **`QueryAnswerType`**: Structured query results with timing and metadata

## Query Categories

| Category | Description | Example Use Case |
|----------|-------------|------------------|
| `trajectoryID` | Melodic gesture types | Find all gamaka (ornament) trajectories |
| `pitch` | Specific pitches | Locate all instances of Sa (tonic) |
| `vowel` | Vocal vowels | Analyze vowel distribution in vocal phrases |
| `startingConsonant` | Initial consonants | Find phrases beginning with 'ga' |
| `pitchSequenceStrict` | Exact pitch patterns | Locate specific melodic phrases |
| `pitchSequenceLoose` | Loose pitch patterns | Find melodic contours |
| `sectionTopLevel` | Performance sections | Separate Alap from Composition |
| `phraseType` | Phrase categories | Find all Asthai phrases |

## Designators

| Designator | Behavior | Example |
|------------|----------|---------|
| `includes` | Contains the element | Phrase contains pitch 60 |
| `excludes` | Does not contain | Phrase avoids pitch 60 |
| `startsWith` | Begins with element | Phrase starts with trajectory 1 |
| `endsWith` | Ends with element | Phrase ends with pitch 67 |

## Segmentation Types

| Type | Unit of Analysis | Use Case |
|------|------------------|----------|
| `phrase` | Individual phrases | Standard phrase-level analysis |
| `group` | Phrase groups | Multi-phrase structural analysis |
| `sequenceOfTrajectories` | Fixed-length trajectory sequences | Pattern recognition |
| `connectedSequenceOfTrajectories` | Variable-length connected sequences | Continuous gesture analysis |

## Advanced Usage

### Duration Filtering
```python
# Find short ornamental phrases (< 1 second)
results = client.single_query(
    transcription_id="...",
    category=CategoryType.TRAJECTORY_ID,
    trajectory_id=1,
    max_dur=1.0,  # Maximum 1 second
    min_dur=0.1   # Minimum 0.1 seconds
)
```

### Section Analysis
```python
# Find all Alap sections
results = client.single_query(
    transcription_id="...",
    category=CategoryType.SECTION_TOP_LEVEL,
    section_top_level="Alap",
    designator=DesignatorType.INCLUDES
)
```

### Sequence Pattern Matching
```python
# Find strict melodic patterns
results = client.single_query(
    transcription_id="...",
    category=CategoryType.PITCH_SEQUENCE_STRICT,
    pitch_sequence=[
        Pitch({"numberedPitch": 60}),  # Sa
        Pitch({"numberedPitch": 62}),  # Re  
        Pitch({"numberedPitch": 64})   # Ga
    ],
    designator=DesignatorType.INCLUDES
)

# Find loose melodic contours (pitches in order but not consecutive)
results = client.single_query(
    transcription_id="...",
    category=CategoryType.PITCH_SEQUENCE_LOOSE,
    pitch_sequence=[...],  # Same as above
    designator=DesignatorType.INCLUDES
)
```

## Testing

The query system includes comprehensive tests covering:

```bash
# Run all query tests
pytest idtap/tests/query_test.py

# Run specific test categories
pytest idtap/tests/query_test.py::TestSequenceUtils
pytest idtap/tests/query_test.py::TestQueryValidation  
pytest idtap/tests/query_test.py::TestQueryExecution
```

## Cross-Platform Compatibility

This Python implementation is designed for seamless integration with the TypeScript web application:

1. **Identical Data Structures**: All types match TypeScript definitions exactly
2. **JSON Serialization**: Results can be serialized/deserialized between systems
3. **Parameter Validation**: Same validation rules as TypeScript version
4. **Error Messages**: Consistent error handling and messaging
5. **Query Logic**: Identical filtering and matching algorithms

## Performance Considerations

- **Large Transcriptions**: Query system handles large datasets efficiently
- **Complex Queries**: Multiple query coordination optimized for performance  
- **Memory Usage**: Minimal memory overhead for result storage
- **Caching**: Results can be cached and reused across queries

## Migration from TypeScript

Existing TypeScript queries can be directly ported:

```typescript
// TypeScript
const query = await Query.single({
  transcriptionID: 'abc123',
  category: 'trajectoryID',
  trajectoryID: 1,
  designator: 'includes'
});
```

```python
# Python equivalent
query = client.single_query(
    transcription_id='abc123',
    category=CategoryType.TRAJECTORY_ID,
    trajectory_id=1,
    designator=DesignatorType.INCLUDES
)
```

## Future Extensions

The query system is designed to support future enhancements:

- Additional query categories and musical elements
- Performance optimization for very large datasets
- Real-time query execution
- Query result visualization
- Statistical analysis integration
- Machine learning pattern recognition

## Support

For questions about the query system:

1. Check the comprehensive test suite for usage examples
2. Review `query_examples.py` for practical demonstrations
3. Refer to TypeScript documentation for detailed feature descriptions
4. Examine the source code - it's extensively documented

The query system represents a complete port of sophisticated musical analysis capabilities, enabling researchers, educators, and enthusiasts to perform deep analysis of Hindustani music transcriptions programmatically.