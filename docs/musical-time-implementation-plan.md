# Musical Time Implementation Plan - Python

## Overview

This document outlines the implementation plan for adding musical time conversion functionality to the Python IDTAP library, based on the specification in `musical-time-spec.md`.

## Implementation Phases

### Phase 1: Core Data Structures
**Goal**: Implement the MusicalTime class and basic infrastructure
**Duration**: 1-2 days
**Dependencies**: None

#### 1.1 MusicalTime Class (`idtap/classes/musical_time.py`)
```python
from dataclasses import dataclass
from typing import Optional, List
import math

@dataclass
class MusicalTime:
    """Represents a musical time position within a meter."""
    cycle_number: int
    hierarchical_position: List[int]
    fractional_beat: float
    
    def __post_init__(self):
        # Validation
        if self.cycle_number < 0:
            raise ValueError("cycle_number must be non-negative")
        if not all(pos >= 0 for pos in self.hierarchical_position):
            raise ValueError("All hierarchical positions must be non-negative")
        if not (0.0 <= self.fractional_beat < 1.0):
            raise ValueError("fractional_beat must be in range [0.0, 1.0)")
    
    # Core properties and methods from spec
```

#### 1.2 Update Package Exports (`idtap/__init__.py`)
```python
from .classes.musical_time import MusicalTime
# Add to __all__ list
```

### Phase 2: Helper Functions
**Goal**: Implement utility functions for hierarchical calculations
**Duration**: 1-2 days  
**Dependencies**: Phase 1

#### 2.1 Helper Functions in Meter Class
```python
# In idtap/classes/meter.py

def _hierarchical_position_to_pulse_index(
    self, 
    positions: List[int], 
    cycle_number: int
) -> int:
    """Convert hierarchical position to pulse index."""
    
def _calculate_level_start_time(
    self, 
    positions: List[int], 
    cycle_number: int, 
    reference_level: int
) -> float:
    """Calculate start time of hierarchical unit at reference level."""
    
def _calculate_level_duration(
    self, 
    positions: List[int], 
    cycle_number: int, 
    reference_level: int
) -> float:
    """Calculate actual duration of hierarchical unit."""
```

#### 2.2 Validation Utilities
```python
def _validate_reference_level(self, reference_level: Optional[int]) -> int:
    """Validate and normalize reference level parameter."""
    if reference_level is None:
        return len(self.hierarchy) - 1
    
    if not isinstance(reference_level, int):
        raise TypeError(f"reference_level must be an integer, got {type(reference_level)}")
    
    if reference_level < 0:
        raise ValueError(f"reference_level must be non-negative, got {reference_level}")
    
    if reference_level >= len(self.hierarchy):
        raise ValueError(f"reference_level {reference_level} exceeds hierarchy depth {len(self.hierarchy)}")
    
    return reference_level
```

### Phase 3: Core Algorithm Implementation
**Goal**: Implement the main get_musical_time method
**Duration**: 2-3 days
**Dependencies**: Phase 1, 2

#### 3.1 Main Method Implementation
```python
# In idtap/classes/meter.py

from typing import Union, Literal, Optional
from ..classes.musical_time import MusicalTime

def get_musical_time(
    self, 
    real_time: float, 
    reference_level: Optional[int] = None
) -> Union[MusicalTime, Literal[False]]:
    """
    Convert real time to musical time within this meter.
    
    Args:
        real_time: Time in seconds
        reference_level: Hierarchical level for fractional calculation 
                        (0=beat, 1=subdivision, etc.). Defaults to finest level.
        
    Returns:
        MusicalTime object if time falls within meter boundaries, False otherwise
    """
```

#### 3.2 Algorithm Steps Implementation
- Boundary validation
- Cycle calculation  
- Hierarchical position calculation
- Reference level-based fractional calculation
- Result construction

### Phase 4: Comprehensive Testing
**Goal**: Implement thorough test coverage
**Duration**: 2-3 days
**Dependencies**: Phase 1-3

#### 4.1 Unit Tests (`idtap/tests/musical_time_test.py`)
```python
import pytest
from idtap.classes.musical_time import MusicalTime
from idtap.classes.meter import Meter

class TestMusicalTime:
    """Test MusicalTime class functionality."""
    
    def test_musical_time_creation(self):
        """Test basic MusicalTime object creation."""
        
    def test_musical_time_validation(self):
        """Test validation of MusicalTime parameters."""
        
    def test_string_representations(self):
        """Test __str__ and to_readable_string methods."""
        
    def test_property_accessors(self):
        """Test beat, subdivision, get_level properties."""

class TestMeterMusicalTime:
    """Test Meter.get_musical_time functionality."""
    
    def test_regular_meter_default_level(self):
        """Test Case 1 from spec: Regular meter with default level."""
        
    def test_reference_level_beat(self):
        """Test Case 2 from spec: Reference level at beat level."""
        
    def test_reference_level_subdivision(self):
        """Test Case 3 from spec: Reference level at subdivision level."""
        
    def test_complex_hierarchy(self):
        """Test Case 4 from spec: Complex hierarchy with reference levels."""
        
    def test_rubato_handling(self):
        """Test Case 5 from spec: Rubato with reference level."""
        
    def test_boundary_conditions(self):
        """Test Case 6 from spec: Boundary conditions."""
        
    def test_reference_level_validation(self):
        """Test Case 7 from spec: Reference level validation."""
```

#### 4.2 Integration Tests
```python
class TestMusicalTimeIntegration:
    """Integration tests with existing meter functionality."""
    
    def test_with_tempo_changes(self):
        """Test musical time after tempo modifications."""
        
    def test_with_pulse_offsets(self):
        """Test musical time with offset_pulse modifications."""
        
    def test_with_grown_cycles(self):
        """Test musical time after grow_cycle operations."""
        
    def test_with_added_time_points(self):
        """Test musical time with manually added time points."""
```

#### 4.3 Performance Tests
```python
class TestMusicalTimePerformance:
    """Performance tests for musical time calculations."""
    
    def test_large_hierarchy_performance(self):
        """Test performance with deep hierarchies."""
        
    def test_many_pulses_performance(self):
        """Test performance with many repetitions."""
        
    def test_repeated_queries_performance(self):
        """Test performance of repeated time queries."""
```

### Phase 5: Documentation and Examples
**Goal**: Complete documentation and usage examples
**Duration**: 1-2 days
**Dependencies**: Phase 1-4

#### 5.1 Docstring Documentation
- Complete docstrings for all methods following Google style
- Type hints for all parameters and return values
- Usage examples in docstrings

#### 5.2 Usage Examples (`examples/musical_time_examples.py`)
```python
"""
Examples demonstrating musical time conversion functionality.
"""

def basic_usage_example():
    """Demonstrate basic musical time conversion."""
    
def reference_level_examples():
    """Demonstrate different reference levels."""
    
def rubato_analysis_example():
    """Demonstrate analysis of expressive timing."""
    
def complex_hierarchy_example():
    """Demonstrate complex hierarchical meters."""
```

#### 5.3 README Updates
Update main README.md with musical time functionality examples.

## Implementation Details

### Code Organization
```
idtap/
├── classes/
│   ├── musical_time.py          # New MusicalTime class
│   └── meter.py                 # Enhanced with get_musical_time
├── tests/
│   ├── musical_time_test.py     # New test file
│   └── meter_test.py            # Enhanced with musical time tests
└── examples/
    └── musical_time_examples.py # New examples
```

### Type Annotations Strategy
```python
from typing import Union, Literal, Optional, List, Tuple
from typing_extensions import TypedDict

# Use consistent typing throughout
TimeConversionResult = Union[MusicalTime, Literal[False]]
HierarchicalPosition = List[int]
```

### Error Handling Strategy
1. **Parameter Validation**: Use comprehensive validation with helpful error messages
2. **Boundary Conditions**: Return `False` for out-of-bounds times (per spec)
3. **Edge Cases**: Handle edge cases gracefully (e.g., zero pulse duration)
4. **Type Safety**: Use type hints and runtime validation

### Performance Considerations
1. **Caching**: Consider caching calculated values for repeated queries
2. **Lazy Evaluation**: Only calculate what's needed for each query
3. **Index Optimization**: Optimize pulse index calculations
4. **Memory Efficiency**: Avoid creating unnecessary intermediate objects

## Testing Strategy

### Test Coverage Goals
- **Unit Tests**: 100% coverage of MusicalTime class
- **Integration Tests**: 100% coverage of get_musical_time method
- **Edge Cases**: All boundary conditions and error cases
- **Spec Compliance**: All test cases from specification must pass

### Test Data Strategy
```python
# Test fixtures for common meter configurations
@pytest.fixture
def simple_meter():
    return Meter(hierarchy=[4, 4], tempo=240, start_time=0)

@pytest.fixture  
def complex_meter():
    return Meter(hierarchy=[3, 2, 4], tempo=960, start_time=5.0)

@pytest.fixture
def rubato_meter():
    meter = Meter(hierarchy=[4], tempo=60, start_time=0)
    meter.offset_pulse(meter.all_pulses[2], 0.5)  # Add rubato
    return meter
```

### Continuous Integration
- All tests must pass before merging
- Performance regression tests
- Type checking with mypy
- Code style compliance with black/isort

## Deployment Plan

### Version Increment
- This is a new feature addition (minor version bump)
- Update version in `pyproject.toml` and `idtap/__init__.py`

### Documentation Updates
- Update API reference documentation
- Add musical time section to main documentation
- Include usage examples in user guide

### Release Notes Template
```markdown
## Musical Time Conversion Feature

### New Functionality
- `Meter.get_musical_time(real_time, reference_level?)` - Convert real time to musical position
- `MusicalTime` class - Represents hierarchical musical time positions  
- Support for arbitrary hierarchical depth and reference levels
- Pulse-based fractional calculation handles rubato and irregular timing

### Usage Examples
[Include key examples from documentation]

### Breaking Changes
None - fully backward compatible
```

## Risk Assessment & Mitigation

### Technical Risks
1. **Floating Point Precision**: Use appropriate tolerances, comprehensive testing
2. **Complex Hierarchies**: Extensive testing with various hierarchy configurations  
3. **Rubato Edge Cases**: Thorough testing with extreme pulse modifications
4. **Performance Impact**: Performance testing and optimization

### Implementation Risks
1. **Spec Interpretation**: Cross-reference with TypeScript implementation
2. **Test Coverage**: Comprehensive test suite before release
3. **API Design**: Review API design with stakeholders before implementation
4. **Documentation**: Clear documentation with examples

## Success Criteria

### Functional Requirements
- [ ] All test cases from specification pass
- [ ] Handles arbitrary hierarchical depth
- [ ] Supports reference level functionality  
- [ ] Correctly handles rubato and irregular timing
- [ ] Returns appropriate types (MusicalTime | False)

### Quality Requirements  
- [ ] 100% test coverage
- [ ] All type annotations complete
- [ ] Performance meets requirements
- [ ] Documentation complete
- [ ] Code style compliant

### Integration Requirements
- [ ] No breaking changes to existing functionality
- [ ] Proper package exports
- [ ] Compatible with existing Meter functionality
- [ ] Ready for TypeScript implementation sync

## Timeline Estimate

**Total Duration**: 7-10 days

- Phase 1: 1-2 days
- Phase 2: 1-2 days  
- Phase 3: 2-3 days
- Phase 4: 2-3 days
- Phase 5: 1-2 days

**Deliverables per Phase**:
- Working code with tests
- Documentation updates  
- Performance validation
- Integration verification

This implementation plan provides a structured approach to adding musical time conversion functionality while maintaining code quality, comprehensive testing, and clear documentation.