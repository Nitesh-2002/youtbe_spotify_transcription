from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import time
from langdetect import detect
import vosk
import os
from pydub import AudioSegment

def extract_video_id(video_link):
    # Check if it's a short URL format (https://youtu.be/VIDEO_ID)
    if "youtu.be/" in video_link:
        video_id = video_link.split("/")[-1]
    elif "youtube.com/watch?v=" in video_link:
        video_id = video_link.split("=")[1]
    else:
        print("Invalid YouTube video link!")
        return None
    return video_id

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript for video {video_id}: {str(e)}")
        return []

def generate_captions_from_audio(audio_path):
    # Load the Vosk ASR model
    model = vosk.Model("vosk-model-small-en-us-0.15")

    # Read the audio file
    sound = AudioSegment.from_wav(audio_path)

    # Get the sample rate of the audio
    sample_rate = sound.frame_rate

    # Convert the audio to raw bytes
    raw_bytes = sound.raw_data

    # Perform ASR on the audio
    rec = vosk.KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    rec.AcceptWaveform(raw_bytes)
    result = rec.FinalResult()

    # Extract and combine the captions into a single string
    captions = ""
    for res in result:
        if 'result' in res:
            captions += res['result'] + ' '

    return captions.strip()

def summarize_video_from_youtube(video_link, language):
    video_id = extract_video_id(video_link)

    if not video_id:
        return

    # Get the transcript of the YouTube video
    transcript = get_transcript(video_id)

    if len(transcript) == 0:
        print("No captions available for the video.")

        # Download audio from YouTube if captions are not available
        audio_url = f"https://www.youtube.com/watch?v={video_id}"
        audio_path = "audio.wav"
        os.system(f"youtube-dl -x --audio-format wav -o {audio_path} {audio_url}")

        # Generate captions using Vosk ASR
        generated_captions = generate_captions_from_audio(audio_path)
        print("Generated Captions:")
        print(generated_captions)

        return

    # Combine the transcript into a single string
    result = ""
    for i in transcript:
        result += ' ' + i['text']

    # Detect the language of the transcript
    detected_language = detect(result)

    # Check if the detected language is English
    if detected_language != 'en':
        print("Our model currently accepts only English language videos.")
        return

    # Initialize the summary pipeline
    summarizer = pipeline('summarization')

    # Measure the inference time
    start_time = time.time()

    # Summarize the text
    num_iters = int(len(result) / 1000)
    summarized_text_list = []
    for i in range(num_iters + 1):
        start = i * 1000
        end = (i + 1) * 1000
        input_text = result[start:end]
        out = summarizer(input_text)
        out = out[0]
        out = out['summary_text']
        summarized_text_list.append(out)

    end_time = time.time()

    # Calculate the inference time
    inference_time = end_time - start_time

    # Print the summarized text, transcript, and inference time
    print("Transcript:")
    for i in transcript:
        print(i['text'])

    print("Summarized text:")
    for text in summarized_text_list:
        print(text)

    # Return the transcript and summary as a tuple
    return transcript, summarized_text_list