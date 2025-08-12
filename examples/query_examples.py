#!/usr/bin/env python3
"""
Example usage of the IDTAP Query System

This file demonstrates how to use the newly implemented query system
to search and analyze musical transcriptions.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from idtap import (
    SwaraClient, Query, Pitch,
    CategoryType, DesignatorType, SegmentationType
)


def basic_trajectory_query_example():
    """Example: Find phrases containing a specific trajectory ID."""
    
    print("=== Basic Trajectory Query Example ===")
    
    # Initialize client
    client = SwaraClient()
    
    # Example transcription ID (replace with actual ID)
    transcription_id = "63445d13dc8b9023a09747a6"
    
    try:
        # Perform a simple trajectory query
        query_result = client.single_query(
            transcription_id=transcription_id,
            category=CategoryType.TRAJECTORY_ID,
            trajectory_id=1,
            designator=DesignatorType.INCLUDES,
            segmentation=SegmentationType.PHRASE
        )
        
        print(f"Found {len(query_result.trajectories)} results")
        
        # Print details about each result
        for i, answer in enumerate(query_result.query_answers):
            print(f"\nResult {i+1}:")
            print(f"  Title: {answer.title}")
            print(f"  Start time: {answer.start_time:.3f}s")
            print(f"  Duration: {answer.duration:.3f}s")
            print(f"  Trajectories: {len(answer.trajectories)}")
            
    except Exception as e:
        print(f"Error: {e}")


def pitch_query_example():
    """Example: Find phrases containing a specific pitch."""
    
    print("\n=== Pitch Query Example ===")
    
    client = SwaraClient()
    transcription_id = "63445d13dc8b9023a09747a6"
    
    try:
        # Create a pitch object (middle C = 60)
        target_pitch = Pitch({"numberedPitch": 60})
        
        # Query for phrases containing this pitch
        query_result = client.single_query(
            transcription_id=transcription_id,
            category=CategoryType.PITCH,
            pitch=target_pitch,
            designator=DesignatorType.INCLUDES
        )
        
        print(f"Found {len(query_result.trajectories)} phrases containing pitch 60")
        
        # Show first few results
        for answer in query_result.query_answers[:3]:
            print(f"  - {answer.title}: {answer.duration:.2f}s")
            
    except Exception as e:
        print(f"Error: {e}")


def vowel_query_example():
    """Example: Find phrases containing specific vowels (vocal transcriptions only)."""
    
    print("\n=== Vowel Query Example ===")
    
    client = SwaraClient()
    transcription_id = "63445d13dc8b9023a09747a6"  # Should be a vocal transcription
    
    try:
        # Query for phrases containing the vowel "a"
        query_result = client.single_query(
            transcription_id=transcription_id,
            category=CategoryType.VOWEL,
            vowel="a",
            designator=DesignatorType.INCLUDES,
            instrument_idx=0  # First instrument track
        )
        
        print(f"Found {len(query_result.trajectories)} phrases containing vowel 'a'")
        
        for answer in query_result.query_answers[:3]:
            print(f"  - {answer.title}")
            
    except Exception as e:
        print(f"Error: {e}")
        if "vocal instruments" in str(e):
            print("  Note: This transcription may not contain vocal parts")


def multiple_query_example():
    """Example: Combine multiple query conditions."""
    
    print("\n=== Multiple Query Example ===")
    
    client = SwaraClient()
    transcription_id = "63445d13dc8b9023a09747a6"
    
    try:
        # Define multiple query conditions
        queries = [
            {
                "category": CategoryType.TRAJECTORY_ID,
                "trajectory_id": 1,
                "designator": DesignatorType.INCLUDES,
                "instrument_idx": 0
            },
            {
                "category": CategoryType.TRAJECTORY_ID, 
                "trajectory_id": 2,
                "designator": DesignatorType.INCLUDES,
                "instrument_idx": 0
            }
        ]
        
        # Find phrases that contain EITHER trajectory ID 1 OR 2
        trajectories, identifiers, answers = client.multiple_query(
            queries=queries,
            transcription_id=transcription_id,
            every=False,  # Union (any query matches)
            segmentation=SegmentationType.PHRASE
        )
        
        print(f"Found {len(trajectories)} phrases containing trajectory ID 1 OR 2")
        
        for answer in answers[:3]:
            print(f"  - {answer.title}: {answer.duration:.2f}s")
        
        # Now find phrases that contain BOTH trajectory ID 1 AND 2
        trajectories, identifiers, answers = client.multiple_query(
            queries=queries,
            transcription_id=transcription_id,
            every=True,  # Intersection (all queries must match)
            segmentation=SegmentationType.PHRASE
        )
        
        print(f"Found {len(trajectories)} phrases containing BOTH trajectory ID 1 AND 2")
        
    except Exception as e:
        print(f"Error: {e}")


def sequence_query_example():
    """Example: Find trajectory sequences."""
    
    print("\n=== Trajectory Sequence Query Example ===")
    
    client = SwaraClient()
    transcription_id = "63445d13dc8b9023a09747a6"
    
    try:
        # Find sequences of 3 consecutive trajectories containing specific IDs
        query_result = client.single_query(
            transcription_id=transcription_id,
            category=CategoryType.TRAJ_SEQUENCE_STRICT,
            traj_id_sequence=[1, 2, 1],  # Look for pattern: traj 1, then 2, then 1
            designator=DesignatorType.INCLUDES,
            segmentation=SegmentationType.SEQUENCE_OF_TRAJECTORIES,
            sequence_length=3
        )
        
        print(f"Found {len(query_result.trajectories)} trajectory sequences with pattern [1, 2, 1]")
        
        for answer in query_result.query_answers[:3]:
            print(f"  - {answer.title}: {answer.duration:.2f}s")
            print(f"    Contains {len(answer.trajectories)} trajectories")
            
    except Exception as e:
        print(f"Error: {e}")


def duration_filtering_example():
    """Example: Filter results by duration."""
    
    print("\n=== Duration Filtering Example ===")
    
    client = SwaraClient()
    transcription_id = "63445d13dc8b9023a09747a6"
    
    try:
        # Find phrases containing trajectory ID 1, but only short ones (< 2 seconds)
        query_result = client.single_query(
            transcription_id=transcription_id,
            category=CategoryType.TRAJECTORY_ID,
            trajectory_id=1,
            designator=DesignatorType.INCLUDES,
            max_dur=2.0,  # Maximum 2 seconds
            min_dur=0.5   # Minimum 0.5 seconds
        )
        
        print(f"Found {len(query_result.trajectories)} phrases with trajectory ID 1")
        print("Duration range: 0.5 - 2.0 seconds")
        
        for answer in query_result.query_answers[:3]:
            print(f"  - {answer.title}: {answer.duration:.2f}s")
            
    except Exception as e:
        print(f"Error: {e}")


def serialization_example():
    """Example: Serialize and deserialize query results."""
    
    print("\n=== Serialization Example ===")
    
    client = SwaraClient()
    transcription_id = "63445d13dc8b9023a09747a6"
    
    try:
        # Perform a query
        query_result = client.single_query(
            transcription_id=transcription_id,
            category=CategoryType.TRAJECTORY_ID,
            trajectory_id=1,
            designator=DesignatorType.INCLUDES
        )
        
        if query_result.query_answers:
            # Serialize the first result to JSON
            answer = query_result.query_answers[0]
            json_data = answer.to_json()
            
            print("Serialized query result:")
            print(f"  Keys: {list(json_data.keys())}")
            print(f"  Title: {json_data.get('title')}")
            print(f"  Duration: {json_data.get('duration')}")
            
            # Deserialize back
            from idtap.query_types import QueryAnswerType
            restored_answer = QueryAnswerType.from_json(json_data)
            
            print("\nDeserialized successfully:")
            print(f"  Title: {restored_answer.title}")
            print(f"  Duration: {restored_answer.duration}")
            print("  -> This demonstrates cross-platform compatibility!")
            
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples."""
    print("IDTAP Query System Examples")
    print("===========================")
    print("Note: These examples require a valid transcription ID and authentication.")
    print("Replace the transcription_id with an actual ID from your account.\n")
    
    # Run examples (you may want to comment out some during testing)
    basic_trajectory_query_example()
    pitch_query_example()
    vowel_query_example()
    multiple_query_example()
    sequence_query_example()
    duration_filtering_example()
    serialization_example()
    
    print("\n=== Examples Complete ===")
    print("The query system supports many more features:")
    print("- Section categorization queries (Alap, Composition, etc.)")
    print("- Phrase type queries (Asthai, Antara, etc.)")
    print("- Pitch sequence matching (strict and loose)")
    print("- Consonant and articulation queries")
    print("- Connected trajectory sequences")
    print("- Complex multi-query combinations")
    print("\nRefer to the TypeScript documentation for full feature details.")


if __name__ == "__main__":
    main()