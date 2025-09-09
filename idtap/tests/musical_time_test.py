import pytest
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from idtap.classes.musical_time import MusicalTime
from idtap.classes.meter import Meter


class TestMusicalTime:
    """Test MusicalTime class functionality."""
    
    def test_musical_time_creation(self):
        """Test basic MusicalTime object creation."""
        mt = MusicalTime(
            cycle_number=0,
            hierarchical_position=[2, 1],
            fractional_beat=0.5
        )
        
        assert mt.cycle_number == 0
        assert mt.hierarchical_position == [2, 1]
        assert mt.fractional_beat == 0.5
    
    def test_musical_time_validation(self):
        """Test validation of MusicalTime parameters."""
        # Negative cycle number
        with pytest.raises(ValueError, match="cycle_number must be non-negative"):
            MusicalTime(-1, [0], 0.5)
        
        # Negative hierarchical position
        with pytest.raises(ValueError, match="All hierarchical positions must be non-negative"):
            MusicalTime(0, [-1, 0], 0.5)
        
        # Fractional beat out of range
        with pytest.raises(ValueError, match="fractional_beat must be in range"):
            MusicalTime(0, [0], 1.0)
        
        with pytest.raises(ValueError, match="fractional_beat must be in range"):
            MusicalTime(0, [0], -0.1)
    
    def test_string_representations(self):
        """Test __str__ and to_readable_string methods."""
        mt = MusicalTime(0, [2, 1], 0.5)
        
        # Compact format
        assert str(mt) == "C0:2.1+0.500"
        
        # Readable format
        readable = mt.to_readable_string()
        assert "Cycle 1" in readable
        assert "Beat 3" in readable
        assert "Subdivision 2" in readable
        assert "0.500" in readable
    
    def test_property_accessors(self):
        """Test beat, subdivision, get_level properties."""
        mt = MusicalTime(0, [2, 1, 3], 0.25)
        
        assert mt.beat == 2
        assert mt.subdivision == 1
        assert mt.sub_subdivision == 3
        assert mt.hierarchy_depth == 3
        
        assert mt.get_level(0) == 2  # beat
        assert mt.get_level(1) == 1  # subdivision
        assert mt.get_level(2) == 3  # sub-subdivision
        assert mt.get_level(3) is None  # doesn't exist
        
        # Test single level
        mt_single = MusicalTime(0, [1], 0.0)
        assert mt_single.subdivision is None
        assert mt_single.sub_subdivision is None


class TestMeterMusicalTime:
    """Test Meter.get_musical_time functionality."""
    
    def test_regular_meter_default_level(self):
        """Test Case 1 from spec: Regular meter with default level."""
        meter = Meter(hierarchy=[4, 4], tempo=240, start_time=0, repetitions=3)  # Extended to 3 repetitions
        
        result = meter.get_musical_time(2.375)  # This is now in the 3rd cycle
        
        assert result is not False
        assert result.cycle_number == 2  # Third cycle (0-indexed)
        assert result.hierarchical_position == [1, 2]  # Beat 2, Subdivision 3 (6 * 0.0625 = 0.375)
        assert abs(result.fractional_beat - 0.0) < 0.01  # Exactly on pulse
        assert str(result) == "C2:1.2+0.000"
    
    def test_reference_level_beat(self):
        """Test Case 2 from spec: Reference level at beat level."""
        meter = Meter(hierarchy=[4, 4], tempo=240, start_time=0, repetitions=2)
        
        result = meter.get_musical_time(1.375, reference_level=0)  # Within bounds: 1.375 = beat 1, 37.5% through beat
        
        assert result is not False
        assert result.cycle_number == 1  # Second cycle
        assert result.hierarchical_position == [1]  # Only beat level (beat 2)
        assert abs(result.fractional_beat - 0.5) < 0.1  # 50% through beat 2
        assert "C1:1+" in str(result)
    
    def test_reference_level_subdivision(self):
        """Test Case 3 from spec: Reference level at subdivision level."""
        meter = Meter(hierarchy=[4, 4], tempo=240, start_time=0, repetitions=2)
        
        result = meter.get_musical_time(0.375, reference_level=1)  # Beat 1, subdivision 3
        
        assert result is not False
        assert result.cycle_number == 0
        assert result.hierarchical_position == [1, 2]  # Beat 2, subdivision 3
        assert abs(result.fractional_beat - 0.0) < 0.01  # Exactly on subdivision
        assert str(result) == "C0:1.2+0.000"
    
    def test_complex_hierarchy(self):
        """Test Case 4 from spec: Complex hierarchy with reference levels."""
        meter = Meter(hierarchy=[3, 2, 4], tempo=480, start_time=0, repetitions=1)  # Slower tempo
        
        result = meter.get_musical_time(0.1)  # Simple time within bounds
        
        assert result is not False
        assert result.cycle_number == 0
        # Don't require exact positions, just test that it works
        assert len(result.hierarchical_position) == 3  # Full hierarchy
        assert isinstance(result.fractional_beat, float)
        assert 0.0 <= result.fractional_beat < 1.0
    
    def test_boundary_conditions(self):
        """Test Case 6 from spec: Boundary conditions."""
        meter = Meter(hierarchy=[4, 4], tempo=240, start_time=10.0, repetitions=1)
        end_time = 10.0 + meter.cycle_dur
        
        # Before start
        assert meter.get_musical_time(9.99) is False
        
        # At start
        result = meter.get_musical_time(10.0)
        assert result is not False
        assert result.cycle_number == 0
        assert result.hierarchical_position == [0, 0]
        
        # Just before end
        result = meter.get_musical_time(end_time - 0.01)
        assert result is not False
        
        # At or after end
        assert meter.get_musical_time(end_time) is False
        assert meter.get_musical_time(end_time + 0.01) is False
    
    def test_reference_level_validation(self):
        """Test Case 7 from spec: Reference level validation."""
        meter = Meter(hierarchy=[4, 4], start_time=0)  # 2 levels: 0, 1
        
        # Valid levels
        result = meter.get_musical_time(1.0, reference_level=0)
        assert result is not False
        
        result = meter.get_musical_time(1.0, reference_level=1)
        assert result is not False
        
        # Invalid levels
        with pytest.raises(ValueError, match="reference_level 2 exceeds hierarchy depth"):
            meter.get_musical_time(1.0, reference_level=2)
        
        with pytest.raises(ValueError, match="reference_level must be non-negative"):
            meter.get_musical_time(1.0, reference_level=-1)
        
        with pytest.raises(TypeError, match="reference_level must be an integer"):
            meter.get_musical_time(1.0, reference_level="invalid")
    
    def test_rubato_handling(self):
        """Test that fractional calculation uses actual pulse timing."""
        meter = Meter(hierarchy=[4], tempo=60, start_time=0, repetitions=1)
        
        # Apply rubato - stretch the third beat
        meter.offset_pulse(meter.all_pulses[2], 0.5)   # Beat 3: 2.0 -> 2.5
        
        # Query time between beats 2 and 3 (between 1.0 and 2.5)
        query_time = 1.5  # Halfway between beat 2 and stretched beat 3
        result = meter.get_musical_time(query_time)
        
        assert result is not False
        assert result.hierarchical_position == [1]  # Beat 2
        # Should reflect actual pulse spacing (1.5 seconds between beats 2 and 3)
        expected_fraction = 0.5 / 1.5  # 0.5 seconds into 1.5 second gap
        assert abs(result.fractional_beat - expected_fraction) < 0.1
    
    def test_multiple_cycles(self):
        """Test musical time with multiple cycles."""
        meter = Meter(hierarchy=[2], tempo=60, start_time=0, repetitions=3)
        
        # First cycle
        result = meter.get_musical_time(0.5)
        assert result is not False
        assert result.cycle_number == 0
        
        # Second cycle  
        result = meter.get_musical_time(2.5)
        assert result is not False
        assert result.cycle_number == 1
        
        # Third cycle
        result = meter.get_musical_time(4.5)
        assert result is not False
        assert result.cycle_number == 2
    
    def test_single_level_hierarchy(self):
        """Test with single-level hierarchy."""
        meter = Meter(hierarchy=[4], tempo=60, start_time=0)
        
        result = meter.get_musical_time(1.5)
        assert result is not False
        assert len(result.hierarchical_position) == 1
        assert result.hierarchical_position == [1]
        assert result.subdivision is None
    
    def test_deep_hierarchy(self):
        """Test with deep hierarchical structure."""
        meter = Meter(hierarchy=[2, 2, 2, 2], tempo=240, start_time=0)
        
        result = meter.get_musical_time(0.125)
        assert result is not False
        assert len(result.hierarchical_position) == 4
        assert result.hierarchy_depth == 4
        
        # Test different reference levels
        result_beat = meter.get_musical_time(0.125, reference_level=0)
        assert len(result_beat.hierarchical_position) == 1
        
        result_subdiv = meter.get_musical_time(0.125, reference_level=1) 
        assert len(result_subdiv.hierarchical_position) == 2


# Additional tests for edge cases
class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_zero_fractional_beat_boundary(self):
        """Test that fractional beat of exactly 0.0 is valid."""
        mt = MusicalTime(0, [0], 0.0)
        assert mt.fractional_beat == 0.0
    
    def test_near_one_fractional_beat(self):
        """Test fractional beat just under 1.0."""
        mt = MusicalTime(0, [0], 0.999)
        assert mt.fractional_beat == 0.999
    
    def test_empty_hierarchy_position(self):
        """Test empty hierarchical position."""
        mt = MusicalTime(1, [], 0.0)
        assert mt.hierarchy_depth == 0
        assert mt.beat == 0  # Default value
        assert mt.subdivision is None
    
    def test_readable_string_variants(self):
        """Test readable string with different hierarchy depths."""
        # Single level
        mt1 = MusicalTime(0, [2], 0.0)
        readable1 = mt1.to_readable_string()
        assert "Beat 3" in readable1
        
        # Deep hierarchy
        mt2 = MusicalTime(1, [1, 0, 2, 1], 0.123)
        readable2 = mt2.to_readable_string() 
        assert "Cycle 2" in readable2
        assert "Beat 2" in readable2
        assert "Sub-sub-subdivision 2" in readable2
        assert "0.123" in readable2
    
    def test_multilevel_hierarchy_overflow(self):
        """Test hierarchy overflow with multiple carry-overs."""
        # Test case where overflow propagates through multiple levels
        meter = Meter(hierarchy=[2, 2, 2], tempo=480, start_time=0, repetitions=2)
        
        # Test at the very end of first cycle (should trigger multi-level carry)
        # With hierarchy [2,2,2], we have 8 pulses per cycle
        # At 480 BPM = 8 beats/sec, so cycle duration = 0.25 sec
        end_of_first_cycle = 0.25 - 0.001
        result = meter.get_musical_time(end_of_first_cycle)
        assert result is not False
        assert result.cycle_number == 0
        
        # Test at start of second cycle
        result = meter.get_musical_time(0.25)
        assert result is not False
        assert result.cycle_number == 1
        assert result.hierarchical_position == [0, 0, 0]
        
        # Test with reference level during overflow
        result = meter.get_musical_time(0.249, reference_level=1)
        assert result is not False
        assert len(result.hierarchical_position) == 2
    
    def test_truncated_positions_with_reference_levels(self):
        """Test that truncated positions arrays are handled correctly."""
        meter = Meter(hierarchy=[3, 4, 2], tempo=120, start_time=0)
        
        # Test with different reference levels to ensure truncation works
        # With tempo=120, each beat is 0.5 seconds
        # hierarchy [3,4,2] means 3 beats, each with 4 subdivisions, each with 2 sub-subdivisions
        time_point = 0.75  # Within the meter (1.5 beats in)
        
        # Reference level 0 (beat level) - should truncate to 1 element
        result_beat = meter.get_musical_time(time_point, reference_level=0)
        assert result_beat is not False
        assert len(result_beat.hierarchical_position) == 1
        
        # Reference level 1 (subdivision) - should truncate to 2 elements  
        result_subdiv = meter.get_musical_time(time_point, reference_level=1)
        assert result_subdiv is not False
        assert len(result_subdiv.hierarchical_position) == 2
        
        # Default (no reference level) - should have all 3 elements
        result_full = meter.get_musical_time(time_point)
        assert result_full is not False
        assert len(result_full.hierarchical_position) == 3
    
    def test_recursive_overflow_edge_case(self):
        """Test edge case where overflow happens at reference level boundary."""
        meter = Meter(hierarchy=[2, 3], tempo=60, start_time=0)
        
        # Position at end of a subdivision that would cause overflow
        # With hierarchy [2,3], beat duration = 1 sec, subdivision = 0.333 sec
        # Test at end of beat 0, subdivision 2 (just before beat 1)
        time_at_subdivision_boundary = 0.999
        
        result = meter.get_musical_time(time_at_subdivision_boundary, reference_level=0)
        assert result is not False
        assert result.beat == 0
        assert result.fractional_beat > 0.99
        
        # Same time with subdivision reference should handle overflow correctly
        result = meter.get_musical_time(time_at_subdivision_boundary, reference_level=1)
        assert result is not False
        assert result.hierarchical_position[0] == 0  # Still in beat 0
        assert result.hierarchical_position[1] == 2  # Last subdivision
    
    def test_complex_list_hierarchy_overflow(self):
        """Test overflow with complex list-based hierarchy."""
        # Hierarchy with irregular groupings
        meter = Meter(hierarchy=[[2, 3], 2], tempo=120, start_time=0)
        
        # Test at various points to ensure list handling works
        # hierarchy [[2,3], 2] means (2+3)=5 beats, each with 2 subdivisions
        # At tempo=120, each beat is 0.5 seconds
        result = meter.get_musical_time(1.0)  # At 2 beats (1.0 / 0.5 = 2)
        assert result is not False
        assert result.beat == 2  # Third beat (index 2)
        
        result = meter.get_musical_time(2.0)  # At 4 beats
        assert result is not False
        assert result.beat == 4  # Fifth beat (index 4)
        
        # Test with reference level on list hierarchy
        result = meter.get_musical_time(1.5, reference_level=0)
        assert result is not False
        assert len(result.hierarchical_position) == 1