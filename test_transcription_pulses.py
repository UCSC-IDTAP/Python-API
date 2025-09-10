#!/usr/bin/env python
"""Test script to examine pulse data in real transcription."""

from idtap import SwaraClient
from idtap.classes.meter import Meter
import json

# Initialize client
client = SwaraClient()

# Fetch the transcription
transcription_id = "68a3a79fffd9b2d478ee11e8"
print(f"Fetching transcription: {transcription_id}")

try:
    piece_data = client.get_piece(transcription_id)
    
    # Convert from JSON to Piece object
    from idtap.classes.piece import Piece
    piece = Piece.from_json(piece_data)
    
    print(f"✓ Successfully loaded: {piece.title}")
    print(f"  Instrumentation: {piece.instrumentation}")
    
    # Examine meters
    if piece.meters:
        print(f"\n  Meters found: {len(piece.meters)}")
        
        for i, meter in enumerate(piece.meters):
            print(f"\n  Meter {i}:")
            print(f"    Hierarchy: {meter.hierarchy}")
            print(f"    Tempo: {meter.tempo} BPM")
            print(f"    Start time: {meter.start_time}s")
            print(f"    Repetitions: {meter.repetitions}")
            print(f"    Cycle duration: {meter.cycle_dur}s")
            
            # Debug: Check pulse_structures
            print(f"\n    Pulse structures layers: {len(meter.pulse_structures)}")
            for layer_idx, layer in enumerate(meter.pulse_structures):
                print(f"      Layer {layer_idx}: {len(layer)} structures")
                for struct_idx, struct in enumerate(layer):
                    print(f"        Structure {layer_idx}.{struct_idx}: {len(struct.pulses)} pulses")
            
            # Calculate expected vs actual pulses
            expected_pulses_per_cycle = meter._pulses_per_cycle
            expected_total = expected_pulses_per_cycle * meter.repetitions
            actual_total = len(meter.all_pulses)
            
            # Check what all_pulses SHOULD be
            print(f"\n    What all_pulses returns: {len(meter.all_pulses)} pulses")
            print(f"    Should be all pulses from layer -1: {sum(len(ps.pulses) for ps in meter.pulse_structures[-1])} pulses")
            
            print(f"    Pulses per cycle (expected): {expected_pulses_per_cycle}")
            print(f"    Total pulses expected: {expected_total}")
            print(f"    Total pulses actual: {actual_total}")
            print(f"    Pulse density: {actual_total / expected_total * 100:.1f}%")
            
            # Check if this would be considered "sparse"
            is_sparse = actual_total < expected_total * 0.5
            print(f"    Would be considered sparse (<50%)?: {'YES ⚠️' if is_sparse else 'NO ✓'}")
            
            # Show first few pulse times if sparse
            if is_sparse or actual_total < expected_total:
                print(f"    First 10 pulse times: {[round(p.real_time, 3) for p in meter.all_pulses[:10]]}")
                
                # Check pulse spacing
                if len(meter.all_pulses) > 1:
                    spacings = []
                    for j in range(1, min(10, len(meter.all_pulses))):
                        spacing = meter.all_pulses[j].real_time - meter.all_pulses[j-1].real_time
                        spacings.append(round(spacing, 3))
                    print(f"    Pulse spacings: {spacings}")
                
                # Try to understand the pattern
                if actual_total > 0:
                    print(f"    Analyzing pulse pattern...")
                    # Check if pulses align with beats only
                    beat_duration = meter.cycle_dur / meter.hierarchy[0] if meter.hierarchy else 0
                    if beat_duration > 0:
                        for j, pulse in enumerate(meter.all_pulses[:10]):
                            relative_time = pulse.real_time - meter.start_time
                            beat_position = relative_time / beat_duration
                            print(f"      Pulse {j}: {pulse.real_time:.3f}s (beat position: {beat_position:.2f})")
            
            # Test get_musical_time with a few sample points
            print(f"\n    Testing get_musical_time():")
            test_times = [
                meter.start_time + 0.1,
                meter.start_time + meter.cycle_dur * 0.25,
                meter.start_time + meter.cycle_dur * 0.5,
                meter.start_time + meter.cycle_dur * 0.75
            ]
            
            for test_time in test_times:
                result = meter.get_musical_time(test_time)
                if result:
                    print(f"      Time {test_time:.3f}s → {result} (frac: {result.fractional_beat:.3f})")
                else:
                    print(f"      Time {test_time:.3f}s → False (out of bounds)")
    else:
        print("  No meters found in this transcription")
        
except Exception as e:
    print(f"✗ Error loading transcription: {e}")
    import traceback
    traceback.print_exc()