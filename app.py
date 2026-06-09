import os
import time
import threading
from glob import glob
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = 'downloads'

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def cleanup_old_files():
    """Background task to delete files older than 1 hour."""
    while True:
        try:
            now = time.time()
            for f in glob(os.path.join(DOWNLOAD_DIR, '*')):
                if os.path.isfile(f):
                    # Check if file is older than 3600 seconds (1 hour)
                    if os.stat(f).st_mtime < now - 3600:
                        os.remove(f)
                        print(f"Cleaned up {f}")
        except Exception as e:
            print(f"Cleanup error: {e}")
        time.sleep(1800)  # Run every 30 minutes

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    # Try to use cookies from browser to bypass 403 errors
    for browser in ('chrome', 'edge', 'firefox'):
        try:
            import yt_dlp
            test_opts = dict(ydl_opts)
            test_opts['cookiesfrombrowser'] = (browser,)
            with yt_dlp.YoutubeDL(test_opts) as ydl_test:
                ydl_test.cookiejar  # force cookie load
            ydl_opts['cookiesfrombrowser'] = (browser,)
            break
        except Exception:
            pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Format duration
            duration_s = info.get('duration', 0)
            mins, secs = divmod(duration_s, 60)
            hrs, mins = divmod(mins, 60)
            duration_str = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"

            formats = []
            
            # Filter and categorize formats (simplified for frontend selection)
            # We look for common specific resolutions we promised: 1080p, 720p, 480p and Audio
            
            # Video + Audio mixed formats (progressive) or just best combinations
            # To simplify the UX, we'll try to get video formats that have audio or we'll fetch them separately
            available_formats = info.get('formats', [])
            
            has_1080 = False
            has_720 = False
            has_480 = False
            
            for f in available_formats:
                height = f.get('height')
                vcodec = f.get('vcodec')
                acodec = f.get('acodec')
                format_id = f.get('format_id')
                ext = f.get('ext')
                filesize = f.get('filesize') or f.get('filesize_approx')
                
                # Try to find mp4 with both video and audio first
                # Or at least formats we can easily mux if needed. yt-dlp usually handles this with 'bestvideo+bestaudio'
                
                # To keep it simple and fast, we'll define some predefined options
                # The actual download logic will use bestvideo[height=X]+bestaudio/best
            
            options_to_offer = [
                {'id': '1080p', 'label': '1080p MP4', 'type': 'video', 'format_str': 'bestvideo[vcodec^=avc1][height<=1080]+bestaudio[ext=m4a]/bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best'},
                {'id': '720p', 'label': '720p MP4', 'type': 'video', 'format_str': 'bestvideo[vcodec^=avc1][height<=720]+bestaudio[ext=m4a]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best'},
                {'id': '480p', 'label': '480p MP4', 'type': 'video', 'format_str': 'bestvideo[vcodec^=avc1][height<=480]+bestaudio[ext=m4a]/bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best'},
                {'id': 'audio', 'label': 'Audio MP3', 'type': 'audio', 'format_str': 'bestaudio/best'},
            ]

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': duration_str,
                'formats': options_to_offer
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format_type = data.get('format')
    
    if not url or not format_type:
        return jsonify({'error': 'URL and format are required'}), 400

    # Determine format string based on user selection
    format_str = 'best'
    postprocessors = []
    
    FFMPEG_PATH = r'C:\Users\ARC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin'

    if format_type == '1080p':
        format_str = 'bestvideo[vcodec^=avc1][height<=1080]+bestaudio[ext=m4a]/bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best'
        merge_output_format = 'mp4'
    elif format_type == '720p':
        format_str = 'bestvideo[vcodec^=avc1][height<=720]+bestaudio[ext=m4a]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best'
        merge_output_format = 'mp4'
    elif format_type == '480p':
        format_str = 'bestvideo[vcodec^=avc1][height<=480]+bestaudio[ext=m4a]/bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best'
        merge_output_format = 'mp4'
    elif format_type == 'audio':
        format_str = 'bestaudio/best'
        merge_output_format = None
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    # Unique output filename to avoid collisions
    timestamp = int(time.time())
    output_template = os.path.join(DOWNLOAD_DIR, f'%(title)s_{format_type}_{timestamp}.%(ext)s')

    ydl_opts = {
        'format': format_str,
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': postprocessors,
        'ffmpeg_location': FFMPEG_PATH,
        'merge_output_format': merge_output_format if merge_output_format else None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    # Try to use cookies from browser to bypass 403 errors
    for browser in ('chrome', 'edge', 'firefox'):
        try:
            test_opts = {'cookiesfrombrowser': (browser,), 'quiet': True}
            with yt_dlp.YoutubeDL(test_opts) as ydl_test:
                ydl_test.cookiejar  # force cookie load
            ydl_opts['cookiesfrombrowser'] = (browser,)
            break
        except Exception:
            pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Find the downloaded file path
            # the requested format might change the extension (e.g., m4a/webm to mp3/mp4)
            # We can use ydl.prepare_filename to get the base name
            filename = ydl.prepare_filename(info)
            base, ext = os.path.splitext(filename)

            if format_type == 'audio':
                final_filename = base + '.mp3'
            elif merge_output_format:
                final_filename = base + '.' + merge_output_format
            else:
                final_filename = filename

            # Sometime yt-dlp prepends random things or changes names if file already exists
            # We'll glob to be safe if exact file doesn't exist
            if not os.path.exists(final_filename):
                possible_files = glob(base + '.*')
                if possible_files:
                    final_filename = possible_files[0]
                else:
                    return jsonify({'error': 'Downloaded file not found'}), 500
                    
            # Return just the filename mapped to a stream url
            return jsonify({
                'success': True,
                'download_url': f'/api/stream?file={os.path.basename(final_filename)}&title={info.get("title")}'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/stream', methods=['GET'])
def stream_file():
    filename = request.args.get('file')
    title = request.args.get('title', 'video')
    
    if not filename:
        return "No file specified", 400
        
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        return "File not found or expired", 404
        
    # Get extension
    _, ext = os.path.splitext(filename)
    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    download_name = f"{safe_title}{ext}"
    
    try:
        # We use send_file. After sending, we don't immediately delete here because send_file is async
        # The background cleanup_thread will handle deletion later
        return send_file(
            filepath,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
