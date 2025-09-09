# Musical Time Conversion Specification

## Overview

This specification defines the interface and behavior for converting real time (seconds) to musical time within a hierarchical meter system. This functionality enables precise positioning of events within complex rhythmic structures while accounting for expressive timing variations (rubato).

## Goals

1. Convert real time to hierarchical musical position within a meter
2. Handle arbitrary depth of rhythmic hierarchy
3. Account for non-periodic pulse spacing due to rubato/expression
4. Provide human-readable musical time representations
5. Maintain identical behavior across Python and TypeScript implementations

## Core Data Structures

### MusicalTime

Represents a position within musical time relative to a meter.

#### Properties
- `cycleNumber: number` - Zero-indexed cycle number
- `hierarchicalPosition: number[]` - Position at each hierarchical level [beat, subdivision, sub-subdivision, ...]
- `fractionalBeat: number` - Fractional position between current pulse and next pulse (0.0 to 1.0)

#### Methods
- `toString(): string` - Compact format: `"C{cycle}:{hierarchy}+{fraction}"`
- `toReadableString(): string` - Human-readable format with level names
- `getBeat(): number` - Get beat position (hierarchicalPosition[0])
- `getSubdivision(): number | null` - Get subdivision (hierarchicalPosition[1] or null)
- `getSubSubdivision(): number | null` - Get sub-subdivision (hierarchicalPosition[2] or null)
- `getLevel(level: number): number | null` - Get position at arbitrary level
- `getHierarchyDepth(): number` - Number of hierarchical levels

#### String Format Examples
```
Compact: "C0:2.1+0.500"  (Cycle 0, Beat 2, Subdivision 1, 0.5 to next)
Readable: "Cycle 1: Beat 3, Subdivision 2 + 0.500 to next pulse"
```

## Core Interface

### Meter.getMusicalTime()

**Signature:**
```
getMusicalTime(realTime: number, referenceLevel?: number): MusicalTime | false
```

**Parameters:**
- `realTime: number` - Time in seconds
- `referenceLevel: number` (optional) - Hierarchical level to use as fractional reference (0=beat, 1=subdivision, etc.). Defaults to finest level (hierarchy.length - 1)

**Returns:**
- `MusicalTime` - Musical position if time falls within meter boundaries
- `false` - If time is before start_time or after end_time

**Reference Level Behavior:**
- `fractionalBeat`: ALWAYS represents fractional position between pulses (finest level), regardless of referenceLevel
- `referenceLevel`: Only affects the truncation of `hierarchicalPosition`:
  - `referenceLevel=0`: hierarchicalPosition includes only beat level
  - `referenceLevel=1`: hierarchicalPosition includes beat and subdivision levels  
  - `referenceLevel=n`: hierarchicalPosition includes levels 0 through n
  - Default (None): hierarchicalPosition includes all levels

**Boundaries:**
- **Start**: `realTime >= meter.startTime`
- **End**: `realTime < meter.startTime + meter.repetitions * meter.cycleDur`

## Algorithm Specification

### Step 1: Boundary Validation
```
if realTime < meter.startTime:
    return false

endTime = meter.startTime + meter.repetitions * meter.cycleDur
if realTime >= endTime:
    return false
```

### Step 2: Cycle Calculation
```
relativeTime = realTime - meter.startTime
cycleNumber = floor(relativeTime / meter.cycleDur)
cycleOffset = relativeTime % meter.cycleDur
```

### Step 3: Hierarchical Position Calculation

For each level in the hierarchy, calculate the position within that level:

```
positions = []
remainingTime = cycleOffset

totalFinestSubdivisions = meter.getPulsesPerCycle()
currentGroupSize = totalFinestSubdivisions

for each level in hierarchy:
    levelSize = hierarchy[level] (or sum if array)
    currentGroupSize = currentGroupSize / levelSize
    subdivisionDuration = currentGroupSize * meter.getPulseDur()
    
    positionAtLevel = floor(remainingTime / subdivisionDuration)
    positions.append(positionAtLevel)
    
    remainingTime = remainingTime % subdivisionDuration
```

### Step 4: Fractional Beat Calculation (Always Pulse-Based)

The fractional beat ALWAYS represents the position between pulses (finest level), regardless of reference level:

```
currentPulseIndex = hierarchicalPositionToPulseIndex(positions, cycleNumber)

// Bounds checking
if currentPulseIndex < 0 or currentPulseIndex >= meter.allPulses.length:
    fractionalBeat = 0.0
else:
    currentPulseTime = meter.allPulses[currentPulseIndex].realTime
    
    // Handle next pulse (accounting for cycle boundaries)
    if currentPulseIndex + 1 < meter.allPulses.length:
        nextPulseTime = meter.allPulses[currentPulseIndex + 1].realTime
    else:
        // Last pulse - use next cycle start
        nextCycleStart = meter.startTime + (cycleNumber + 1) * meter.cycleDur
        nextPulseTime = nextCycleStart
    
    pulseDuration = nextPulseTime - currentPulseTime
    if pulseDuration <= 0:
        fractionalBeat = 0.0
    else:
        timeFromCurrentPulse = realTime - currentPulseTime
        fractionalBeat = timeFromCurrentPulse / pulseDuration

// Clamp to [0, 1] range
fractionalBeat = max(0.0, min(1.0, fractionalBeat))
```

### Step 5: Handle Reference Level Truncation

If a reference level is specified, truncate the hierarchical position (fractional_beat remains unchanged):

```
if referenceLevel is not None and referenceLevel < len(hierarchy):
    // Truncate positions to reference level for final result
    positions = positions[0:referenceLevel+1]
    
// Note: fractionalBeat is NOT recalculated - it always remains pulse-based
```

### Step 6: Result Construction
```
return MusicalTime {
    cycleNumber: cycleNumber,
    hierarchicalPosition: positions,
    fractionalBeat: fractionalBeat
}
```

## Helper Functions

### hierarchicalPositionToPulseIndex()

**Purpose:** Convert hierarchical position to pulse index within a cycle.

**Signature:**
```
hierarchicalPositionToPulseIndex(positions: number[], cycleNumber: number): number
```

**Algorithm:**
```
pulseIndex = 0
multiplier = 1

// Work from finest to coarsest level
for level = positions.length - 1 down to 0:
    position = positions[level]
    hierarchySize = hierarchy[level] (or sum if array)
    
    pulseIndex += position * multiplier
    multiplier *= hierarchySize

// Add offset for cycle
cycleOffset = cycleNumber * meter.getPulsesPerCycle()
return pulseIndex + cycleOffset
```

**Note:** The simplified implementation no longer requires the complex `calculateLevelStartTime()` and `calculateLevelDuration()` helper functions that were used in the previous reference-level-based fractional beat calculation.

## Edge Cases & Error Handling

### Time Boundaries
- **Before start**: Return `false`
- **At or after end**: Return `false`
- **Exactly at start**: Return valid MusicalTime
- **Exactly at cycle boundary**: Belongs to the starting cycle

### Pulse Spacing
- **Zero duration between pulses**: fractionalBeat = 0.0
- **Negative duration** (shouldn't happen): fractionalBeat = 0.0
- **Last pulse in meter**: Use next cycle start for duration calculation

### Hierarchy Validation
- **Empty hierarchy**: Should not occur (validated in Meter constructor)
- **Single level hierarchy**: hierarchicalPosition has length 1
- **Array notation** (`[[2,2]]`): Treat as sum for calculations

## Test Cases

### Test Case 1: Regular Meter - Default (Finest Level)
```
Meter: hierarchy=[4, 4], tempo=240, startTime=0, repetitions=2
Query: getMusicalTime(2.375)

Expected:
- cycleNumber: 0
- hierarchicalPosition: [2, 1] (Beat 3, Subdivision 2)  
- fractionalBeat: 0.5 (halfway to next pulse)
- toString(): "C0:2.1+0.500"
```

### Test Case 2: Reference Level - Beat Level (referenceLevel=0)
```
Meter: hierarchy=[4, 4], tempo=240, startTime=0, repetitions=2  
Query: getMusicalTime(2.375, referenceLevel=0)

Expected:
- cycleNumber: 0
- hierarchicalPosition: [2] (Beat 3 only, due to referenceLevel=0)
- fractionalBeat: 0.0 (exactly on pulse, fractionalBeat always pulse-based)
- toString(): "C0:2+0.000"
- Readable: "Cycle 1: Beat 3"
```

### Test Case 3: Reference Level - Subdivision Level (referenceLevel=1)
```
Meter: hierarchy=[4, 4], tempo=240, startTime=0, repetitions=2
Query: getMusicalTime(2.375, referenceLevel=1)

Expected:
- cycleNumber: 0
- hierarchicalPosition: [2, 1] (Beat 3, Subdivision 2)
- fractionalBeat: 0.0 (exactly on pulse, fractionalBeat always pulse-based)
- toString(): "C0:2.1+0.000"
- Readable: "Cycle 1: Beat 3, Subdivision 2"
```

### Test Case 4: Complex Hierarchy with Reference Levels
```
Meter: hierarchy=[3, 2, 4], tempo=960, startTime=0, repetitions=1
Query: getMusicalTime(0.15625, referenceLevel=1)

Expected:
- cycleNumber: 0
- hierarchicalPosition: [1, 0] (Beat 2, Subdivision 1)
- fractionalBeat: 0.25 (0.25 through finest-level pulse duration)
- toString(): "C0:1.0+0.250"
```

### Test Case 5: Rubato with Reference Level
```
Meter: hierarchy=[4, 2], tempo=120, startTime=0, repetitions=1
Pulses modified: beat 2 is stretched by 0.5 seconds

Query: getMusicalTime(1.75, referenceLevel=0) 
Expected: fractionalBeat calculated from actual beat boundaries (accounting for rubato)
```

### Test Case 6: Boundary Conditions
```
Meter: startTime=10.0, endTime=20.0

Query: realTime=9.99 → Expected: false
Query: realTime=10.0 → Expected: valid MusicalTime
Query: realTime=19.99 → Expected: valid MusicalTime  
Query: realTime=20.0 → Expected: false
```

### Test Case 7: Reference Level Validation
```
Meter: hierarchy=[4, 4] (2 levels: 0, 1)

Query: getMusicalTime(1.0, referenceLevel=0) → Valid
Query: getMusicalTime(1.0, referenceLevel=1) → Valid  
Query: getMusicalTime(1.0, referenceLevel=2) → Error (level doesn't exist)
Query: getMusicalTime(1.0, referenceLevel=-1) → Error (invalid level)
```

## Implementation Notes

### Precision Considerations
- Use appropriate floating-point comparison tolerances
- Handle potential precision errors in time calculations
- Ensure consistent behavior across platforms

### Performance Considerations  
- Cache calculated values where appropriate
- Avoid recalculating pulse indices for repeated queries
- Consider optimization for large numbers of pulses

### Type Safety
- Return type should be union/optional type (`MusicalTime | false`)
- All numeric parameters should be validated
- Handle null/undefined inputs gracefully

## Level Naming Convention

For string representations, use this naming pattern:
- Level 0: "Beat"
- Level 1: "Subdivision"  
- Level 2: "Sub-subdivision"
- Level 3: "Sub-sub-subdivision"
- Level N (N > 3): "Sub^{N-1}-subdivision"

## Version Requirements

This specification should be implemented identically in:
- Python: `idtap.classes.meter.Meter`
- TypeScript: `src/ts/model/meter/Meter`

Both implementations must pass identical test suites to ensure behavioral consistency across platforms.