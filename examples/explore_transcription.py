#!/usr/bin/env python3
"""
Explore the test transcription to understand available consonants, vowels, and patterns.
This helps us create better targeted tests.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from idtap import SwaraClient
from collections import Counter

# Test transcription ID
TRANSCRIPTION_ID = "645ff354deeaf2d1e33b3c44"

def explore_transcription_data():
    """Explore the transcription to see what data is available."""
    
    client = SwaraClient()
    
    print("=== TRANSCRIPTION EXPLORATION ===")
    print(f"Transcription ID: {TRANSCRIPTION_ID}")
    
    try:
        # Load the transcription
        piece_data = client.get_piece(TRANSCRIPTION_ID)
        from idtap.classes.piece import Piece
        piece = Piece.from_json(piece_data)
        
        print(f"\nInstrumentation: {piece.instrumentation}")
        print(f"Total phrases: {len(piece.phrases) if piece.phrases else 0}")
        
        if not piece.phrase_grid or not piece.phrase_grid[0]:
            print("No phrase grid data available")
            return
            
        phrases = piece.phrase_grid[0]  # First (and likely only) track
        print(f"Phrases in track 0: {len(phrases)}")
        
        # Collect all vowels and consonants
        vowels = []
        start_consonants = []
        end_consonants = []
        trajectory_ids = []
        
        total_trajectories = 0
        
        for phrase_idx, phrase in enumerate(phrases):
            print(f"\nPhrase {phrase_idx + 1}: {len(phrase.trajectories)} trajectories")
            
            for traj_idx, traj in enumerate(phrase.trajectories):
                total_trajectories += 1
                
                # Collect data
                if hasattr(traj, 'vowel') and traj.vowel is not None:
                    vowels.append(traj.vowel)
                if hasattr(traj, 'start_consonant') and traj.start_consonant is not None:
                    start_consonants.append(traj.start_consonant)
                if hasattr(traj, 'end_consonant') and traj.end_consonant is not None:
                    end_consonants.append(traj.end_consonant)
                if hasattr(traj, 'id') and traj.id is not None:
                    trajectory_ids.append(traj.id)
                
                # Show first few trajectories in detail
                if phrase_idx < 3 and traj_idx < 3:
                    vowel = getattr(traj, 'vowel', None)
                    start_cons = getattr(traj, 'start_consonant', None) 
                    end_cons = getattr(traj, 'end_consonant', None)
                    traj_id = getattr(traj, 'id', None)
                    print(f"  Traj {traj_idx}: ID={traj_id}, vowel='{vowel}', "
                          f"start='{start_cons}', end='{end_cons}'")
        
        print(f"\n=== SUMMARY STATISTICS ===")
        print(f"Total trajectories: {total_trajectories}")
        
        # Vowel analysis
        vowel_counts = Counter(vowels)
        print(f"\nVowels found ({len(vowels)} total):")
        for vowel, count in vowel_counts.most_common():
            print(f"  '{vowel}': {count} occurrences")
        
        # Consonant analysis
        start_cons_counts = Counter(start_consonants)
        print(f"\nStart consonants found ({len(start_consonants)} total):")
        for cons, count in start_cons_counts.most_common():
            print(f"  '{cons}': {count} occurrences")
            
        end_cons_counts = Counter(end_consonants)
        print(f"\nEnd consonants found ({len(end_consonants)} total):")
        for cons, count in end_cons_counts.most_common():
            print(f"  '{cons}': {count} occurrences")
        
        # Trajectory ID analysis
        traj_id_counts = Counter(trajectory_ids)
        print(f"\nTrajectory IDs found ({len(trajectory_ids)} total):")
        for traj_id, count in traj_id_counts.most_common():
            print(f"  ID {traj_id}: {count} occurrences")
            
        return {
            'vowels': vowel_counts,
            'start_consonants': start_cons_counts,
            'end_consonants': end_cons_counts,
            'trajectory_ids': traj_id_counts,
            'piece': piece
        }
        
    except Exception as e:
        print(f"Error exploring transcription: {e}")
        return None


def test_found_patterns(data):
    """Test queries using the patterns we actually found in the data."""
    
    if not data:
        print("No data to test with")
        return
        
    client = SwaraClient()
    
    print(f"\n=== TESTING ACTUAL PATTERNS ===")
    
    # Test most common vowel
    if data['vowels']:
        most_common_vowel = data['vowels'].most_common(1)[0][0]
        print(f"\nTesting most common vowel: '{most_common_vowel}'")
        
        try:
            result = client.single_query(
                transcription_id=TRANSCRIPTION_ID,
                category="vowel",
                vowel=most_common_vowel,
                designator="includes"
            )
            print(f"Found {len(result.trajectories)} phrases containing vowel '{most_common_vowel}'")
            
        except Exception as e:
            print(f"Vowel query failed: {e}")
    
    # Test most common start consonant
    if data['start_consonants']:
        most_common_start_cons = data['start_consonants'].most_common(1)[0][0]
        print(f"\nTesting most common start consonant: '{most_common_start_cons}'")
        
        try:
            result = client.single_query(
                transcription_id=TRANSCRIPTION_ID,
                category="startingConsonant",
                consonant=most_common_start_cons,
                designator="includes"
            )
            print(f"Found {len(result.trajectories)} phrases containing start consonant '{most_common_start_cons}'")
            
        except Exception as e:
            print(f"Start consonant query failed: {e}")
    
    # Test trajectory sequence with common IDs
    if len(data['trajectory_ids']) >= 2:
        common_ids = [tid for tid, count in data['trajectory_ids'].most_common(3)]
        if len(common_ids) >= 2:
            sequence = common_ids[:2]
            print(f"\nTesting trajectory sequence: {sequence}")
            
            try:
                result = client.single_query(
                    transcription_id=TRANSCRIPTION_ID,
                    category="trajSequenceStrict",
                    traj_id_sequence=sequence,
                    designator="includes",
                    segmentation="sequenceOfTrajectories",
                    sequence_length=2
                )
                print(f"Found {len(result.trajectories)} sequences matching pattern {sequence}")
                
            except Exception as e:
                print(f"Trajectory sequence query failed: {e}")


def test_specific_combinations(data):
    """Test specific combinations that might be interesting."""
    
    if not data:
        return
        
    client = SwaraClient()
    print(f"\n=== TESTING SPECIFIC COMBINATIONS ===")
    
    # Try to find phrases that have both a common vowel AND a common consonant
    if data['vowels'] and data['start_consonants']:
        vowel = data['vowels'].most_common(1)[0][0]
        consonant = data['start_consonants'].most_common(1)[0][0]
        
        print(f"\nTesting combination: vowel '{vowel}' AND start consonant '{consonant}'")
        
        try:
            queries = [
                {
                    "category": "vowel",
                    "vowel": vowel,
                    "designator": "includes",
                    "instrument_idx": 0
                },
                {
                    "category": "startingConsonant", 
                    "consonant": consonant,
                    "designator": "includes",
                    "instrument_idx": 0
                }
            ]
            
            trajectories, identifiers, answers = client.multiple_query(
                queries=queries,
                transcription_id=TRANSCRIPTION_ID,
                every=True  # Both conditions must be met
            )
            
            print(f"Found {len(trajectories)} phrases with BOTH vowel '{vowel}' AND consonant '{consonant}'")
            
            for answer in answers[:3]:
                print(f"  - {answer.title}: {answer.duration:.2f}s")
                
        except Exception as e:
            print(f"Combination query failed: {e}")


if __name__ == "__main__":
    print("Exploring test transcription data...")
    
    # Explore the transcription
    data = explore_transcription_data()
    
    # Test with found patterns
    test_found_patterns(data)
    
    # Test combinations
    test_specific_combinations(data)
    
    print(f"\n=== EXPLORATION COMPLETE ===")
    print("This data can help create more targeted and effective tests!")