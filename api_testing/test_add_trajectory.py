from idtap_api.client import SwaraClient
from idtap_api.classes.piece import Piece
from idtap_api.classes.trajectory import Trajectory

def test_add_trajectory():
    """Test adding a trajectory to a piece at a specific time."""
    s = SwaraClient()
    
    # Use the same transcription ID as the update test
    transcription_id = '685c11ad80dc6827daaf017d'
    print(f"Getting transcription {transcription_id}...")
    
    # Get the piece data
    piece_data = s.get_piece(transcription_id)
    piece = Piece.from_json(piece_data)
    print(f"Retrieved transcription: {piece.title}")
    print(f"Duration: {piece.dur_tot:.2f} seconds" if piece.dur_tot else "Duration: Unknown")
    print(f"Number of phrases: {len(piece.phrases)}")
    
    # Print current state at second 45
    target_time = 45.0
    inst_track = 0  # Main track
    
    print(f"\nChecking state at {target_time} seconds on track {inst_track}:")
    
    # Find what's currently at that time
    current_traj = piece.traj_from_time(target_time, inst_track)
    if current_traj:
        print(f"  Current trajectory: ID {current_traj.id}, name: {current_traj.name}")
        print(f"  Duration: {current_traj.dur_tot:.2f}s")
        if current_traj.id == 12:
            print("  ✅ Silent trajectory found - good for replacement")
        else:
            print("  ⚠️  Not a silent trajectory - may not be replaceable")
    else:
        print("  No trajectory found at this time")
    
    # Create a simple trajectory with ID 4 (should be a "Bend: Sloped End" trajectory type)
    # Using swaras: 0=sa, 1=re, so this will be sa -> re -> sa
    # The raised/komal status will be determined by the piece's raga
    trajectory_data = {
        'id': 4,
        'dur_tot': 2.0,    # 2-second duration
        'pitches': [
            {'swara': 0, 'oct': 0},   # Sa
            {'swara': 1, 'oct': 0},   # Re (komal/shuddha determined by raga)
            {'swara': 0, 'oct': 0}    # Sa
        ]
    }
    
    print(f"\nAttempting to add trajectory ID {trajectory_data['id']} at {target_time} seconds...")
    
    # Try to add the trajectory
    try:
        success = piece.add_trajectory(trajectory_data, inst_track, target_time)
        
        if success:
            print("✅ Trajectory added successfully!")
            
            # Verify the trajectory was added
            print("\nVerifying trajectory was added:")
            new_traj = piece.traj_from_time(target_time, inst_track)
            if new_traj and new_traj.id == trajectory_data['id']:
                print(f"  ✅ Found new trajectory: ID {new_traj.id}, name: {new_traj.name}")
                print(f"  Duration: {new_traj.dur_tot:.2f}s")
                if hasattr(new_traj, 'pitches') and new_traj.pitches:
                    start_swara = new_traj.pitches[0].swara
                    end_swara = new_traj.pitches[-1].swara
                    sargam_names = ['sa', 're', 'ga', 'ma', 'pa', 'dha', 'ni']
                    print(f"  Swaras: {sargam_names[start_swara]} to {sargam_names[end_swara]}")
            else:
                print("  ❌ Could not verify trajectory was added correctly")
            
            # Optional: Save the modified piece back to the server
            save_choice = input("\nSave changes to server? (y/N): ").strip().lower()
            if save_choice == 'y':
                print("Saving modified piece to server...")
                result = s.save_piece(piece.to_json())
                print(f"Save result: {result}")
            else:
                print("Changes not saved to server.")
                
        else:
            print("❌ Failed to add trajectory")
            print("This could be due to:")
            print("- No silent trajectory (ID 12) at the target location")
            print("- Time is outside piece duration")
            print("- Invalid track number")
            print("- Target spans multiple phrases or trajectories")
            
    except Exception as e:
        print(f"❌ Error adding trajectory: {e}")

if __name__ == "__main__":
    test_add_trajectory()