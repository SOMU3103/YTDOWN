from flask import Flask, render_template, request, send_file, jsonify
from pytubefix import YouTube
from io import BytesIO
import subprocess
import os
import tempfile
import re

app = Flask(__name__)


def sanitize_filename(filename):
    """Remove or replace invalid filename characters"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Replace multiple spaces/underscores with single space
    filename = re.sub(r'[_\s]+', ' ', filename)
    
    # Remove leading/trailing spaces and underscores
    filename = filename.strip(' _')
    
    # Limit filename length (leave room for extension)
    if len(filename) > 200:
        filename = filename[:200]
    
    # Final cleanup - remove trailing spaces/underscores again
    filename = filename.rstrip(' _')
    
    return filename


def merge_video_audio(video_path, audio_path, output_path):
    """Merge video and audio using ffmpeg"""
    try:
        subprocess.run([
            'ffmpeg', '-i', video_path, '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
            output_path, '-y', '-loglevel', 'error'
        ], check=True, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("FFmpeg not found. Please install ffmpeg.")
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("geturl")
        dtype = request.form.get("type")
        quality = request.form.get("quality", "720")
        
        if not url:
            return "No URL provided", 400
        
        # Use temporary directory that auto-cleans after request
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                yt = YouTube(url)
                clean_title = sanitize_filename(yt.title)
                
                if dtype == "audio":
                    # Get highest quality audio
                    stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                    
                    if not stream:
                        return "No audio stream available", 400
                    
                    # Stream directly to buffer (no server storage)
                    buffer = BytesIO()
                    stream.stream_to_buffer(buffer)
                    buffer.seek(0)
                    
                    filename = f"{clean_title}.mp3"
                    
                    return send_file(
                        buffer,
                        as_attachment=True,
                        download_name=filename,
                        mimetype="audio/mpeg"
                    )
                
                else:  # VIDEO
                    # For 720p and below, try progressive first (video+audio combined)
                    if quality in ["360", "480", "720"]:
                        stream = yt.streams.filter(res=f"{quality}p", progressive=True).first()
                        
                        if stream:
                            # Stream directly to buffer (no server storage)
                            buffer = BytesIO()
                            stream.stream_to_buffer(buffer)
                            buffer.seek(0)
                            filename = f"{clean_title}.mp4"
                            
                            return send_file(
                                buffer,
                                as_attachment=True,
                                download_name=filename,
                                mimetype="video/mp4"
                            )
                    
                    # For high quality, need to merge video+audio
                    video_stream = yt.streams.filter(
                        res=f"{quality}p", 
                        adaptive=True, 
                        file_extension='mp4'
                    ).first()
                    
                    if not video_stream:
                        # Try without resolution filter, get best available
                        video_stream = yt.streams.filter(
                            adaptive=True, 
                            file_extension='mp4'
                        ).order_by('resolution').desc().first()
                    
                    if not video_stream:
                        return f"{quality}p not available for this video", 400
                    
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                    
                    if not audio_stream:
                        return "No audio stream available", 400
                    
                    # Use temporary files that will be deleted after this request
                    video_path = os.path.join(tmpdir, "video.mp4")
                    audio_path = os.path.join(tmpdir, "audio.mp4")
                    output_path = os.path.join(tmpdir, "output.mp4")
                    
                    # Download streams to temp directory
                    print(f"Downloading video: {video_stream.resolution}")
                    video_stream.download(output_path=tmpdir, filename="video.mp4")
                    
                    print(f"Downloading audio: {audio_stream.abr}")
                    audio_stream.download(output_path=tmpdir, filename="audio.mp4")
                    
                    # Merge with ffmpeg
                    print("Merging video and audio...")
                    if not merge_video_audio(video_path, audio_path, output_path):
                        return "Failed to merge video and audio. Make sure ffmpeg is installed.", 500
                    
                    # Read merged file into buffer and send to browser
                    # File will be deleted when tmpdir context exits
                    with open(output_path, 'rb') as f:
                        buffer = BytesIO(f.read())
                    
                    buffer.seek(0)
                    filename = f"{clean_title}.mp4"
                    
                    return send_file(
                        buffer,
                        as_attachment=True,
                        download_name=filename,
                        mimetype="video/mp4"
                    )
                    # tmpdir and all files automatically deleted here
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                return f"Error: {str(e)}", 500
            # tmpdir automatically cleaned up here even if error occurs
    
    return render_template("index.html")


@app.route("/get_qualities", methods=["POST"])
def get_qualities():
    """API endpoint to fetch available qualities for a video"""
    try:
        data = request.get_json()
        url = data.get("url")
        
        if not url:
            return jsonify({"success": False, "error": "No URL provided"}), 400
        
        yt = YouTube(url)
        
        # Get video qualities
        video_streams = yt.streams.filter(type="video", file_extension='mp4')
        video_qualities = []
        seen_resolutions = set()
        
        for stream in video_streams:
            if stream.resolution:
                res_num = stream.resolution.replace('p', '')
                if res_num not in seen_resolutions:
                    quality_info = {
                        'resolution': res_num,
                        'label': stream.resolution,
                        'fps': getattr(stream, 'fps', 30)
                    }
                    video_qualities.append(quality_info)
                    seen_resolutions.add(res_num)
        
        # Sort by resolution (highest first)
        video_qualities.sort(key=lambda x: int(x['resolution']), reverse=True)
        
        # Get audio qualities
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        audio_qualities = []
        seen_audio = set()
        
        for stream in audio_streams:
            if stream.abr and stream.abr not in seen_audio:
                audio_qualities.append({
                    'bitrate': stream.abr,
                    'label': stream.abr
                })
                seen_audio.add(stream.abr)
        
        return jsonify({
            "success": True,
            "video_qualities": video_qualities,
            "audio_qualities": audio_qualities,
            "title": yt.title,
            "duration": yt.length
        })
        
    except Exception as e:
        print(f"Error fetching qualities: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)