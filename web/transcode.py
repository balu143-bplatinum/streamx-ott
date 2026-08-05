import subprocess
import os

def generate_hls_stream(input_mp4_path, output_dir):
    """Transcodes a raw video into a multi-resolution HLS playlist."""
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        'ffmpeg', '-i', input_mp4_path,
        '-filter_complex',
        '[0:v]split=3[v1,v2,v3]; '
        '[v1]scale=w=1920:h=1080[v1out]; '
        '[v2]scale=w=1280:h=720[v2out]; '
        '[v3]scale=w=854:h=480[v3out]',
        
        # 1080p Stream
        '-map', '[v1out]', '-map', '0:a', '-b:v:0', '5000k', '-maxrate:v:0', '5350k',
        # 720p Stream
        '-map', '[v2out]', '-map', '0:a', '-b:v:1', '2800k', '-maxrate:v:1', '3000k',
        # 480p Stream
        '-map', '[v3out]', '-map', '0:a', '-b:v:2', '1400k', '-maxrate:v:2', '1500k',
        
        '-f', 'hls',
        '-hls_time', '6',  # 6-second segment chunks
        '-hls_playlist_type', 'vod',
        '-master_pl_name', 'master.m3u8',
        '-var_stream_map', 'v:0,a:0 v:1,a:1 v:2,a:2',
        f'{output_dir}/stream_%v.m3u8'
    ]
    
    subprocess.run(cmd, check=True)
    return f"{output_dir}/master.m3u8"