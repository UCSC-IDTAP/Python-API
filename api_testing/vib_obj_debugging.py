#!/usr/bin/env python3

from idtap import SwaraClient, Piece

TRANSCRIPTION_ID = "6417585554a0bfbd8de2d3ff"

def main():
    # Authenticate with Google OAuth
    # login_google()
    
    # Create client
    client = SwaraClient()
    
    # Fetch all transcriptions first
    piece_data = client.get_piece(TRANSCRIPTION_ID)
    piece = Piece.from_json(piece_data)
    print(piece)

if __name__ == "__main__":
    main()
