
import os
from flask import Flask, request, jsonify
from spotify import summarize_audio_from_spotify
from youtube import summarize_video_from_youtube

import functions_framework

app = Flask(__name__)

@app.route('/summarize', methods=['POST'])
@functions_framework.http
def summarize(request):
    data = request.get_json()
    link = data.get('link')
    language = data.get('language')

    if not link or not language:
        return jsonify({'error': 'Invalid payload.'}), 400

    # Check if it's a YouTube video link or Spotify track link
    if "youtube.com/watch?v=" in link:
        transcript, summary = summarize_video_from_youtube(link, language)
    elif "youtu.be/" in link:
        transcript, summary = summarize_video_from_youtube(link, language)
    elif "open.spotify.com/track/" in link:
        transcript, summary = summarize_audio_from_spotify(link, language)
    else:
        return jsonify({'error': 'Invalid link format.'}), 400

    if not transcript or not summary:
        return jsonify({'error': 'Summarization failed.'}), 500

    # Print transcript and summary
    print("Transcript:", transcript)
    print("Summary:", summary)

    # Save transcript and summary to files
    

    return jsonify({
        'message': 'Summarization completed.',
        'transcript': transcript,
        'summary': summary
    })

if __name__ == '__main__':
    app.run(debug=True)
