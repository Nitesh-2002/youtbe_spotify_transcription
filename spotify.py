import os
import spotipy
import urllib.request
import soundfile as sf
import speech_recognition as sr
from transformers import pipeline
import tempfile

spotify_client_id = '67d84df62a7b44d1bbacfe8274c4792a'
spotify_client_secret = 'a8543c6dfaed457ebb7300be03bae439'

spotify_client_credentials_manager = spotipy.SpotifyClientCredentials(
    client_id=spotify_client_id, client_secret=spotify_client_secret
)
spotify_sp = spotipy.Spotify(client_credentials_manager=spotify_client_credentials_manager)

def get_track_info(track_url):
    try:
        track_info = spotify_sp.track(track_url)
        return track_info
    except Exception as e:
        print(f"Error retrieving track information for {track_url}: {str(e)}")
        return None

def summarize_audio_from_spotify(track_url, language):
    # Get track information
    track_info = spotify_sp.track(track_url)
    track_name = track_info['name']
    track_artist = track_info['artists'][0]['name']

    # Get preview URL
    preview_url = track_info['preview_url']
    print(f"Preview URL: {preview_url}")

    # Create a temporary directory to store the audio file and transcript
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download audio from Spotify if preview URL is available
        if preview_url is not None:
            audio_path = os.path.join(temp_dir, "audio.m4a")
            urllib.request.urlretrieve(preview_url, audio_path)
        else:
            print("No preview URL available for the track.")
            return

        # Convert audio to WAV format using soundfile
        data, samplerate = sf.read(audio_path)
        wav_path = os.path.join(temp_dir, "audio.wav")
        sf.write(wav_path, data, samplerate)

        # Initialize SpeechRecognition recognizer with PocketSphinx engine
        r = sr.Recognizer()
        r.energy_threshold = 4000

        # Load audio file
        audio_file = sr.AudioFile(wav_path)

        # Transcribe audio using PocketSphinx
        with audio_file as source:
            audio = r.record(source)

        # Generate transcript
        transcript = r.recognize_sphinx(audio)

        # Print track information and transcript
        print(f"Track: {track_name} by {track_artist}")
        print("Transcript:")
        print(transcript)

        # Initialize the summary pipeline
        summarizer = pipeline('summarization')

        # Summarize the text
        summarized_text = summarizer(transcript, max_length=200, min_length=50, do_sample=False)

        # Print the summary
        print("Summary:")
        print(summarized_text[0]['summary_text'])

        return transcript, summarized_text[0]['summary_text']