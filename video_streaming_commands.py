import json
import subprocess
import time
from queue import Queue


def parse_stream(stream):
    language = stream['tags']['language'] if 'tags' in stream and 'language' in stream['tags'] else None
    if language is None:
        language = stream['tags']['LANGUAGE'] if 'tags' in stream and 'LANGUAGE' in stream[
            'tags'] else 'l'

    title = stream['tags']['title'] if 'tags' in stream and 'title' in stream['tags'] else 't'
    codec = stream['codec_name'] if 'codec_name' in stream else 'no codec'
    return language + ' - ' + title + ' - ' + codec


def duration_to_seconds(duration):
    return int(float(duration))


def get_video_info(video_path, queue: Queue = None, ffmpeg_path=None, ffprobe_path=None):
    output = subprocess.check_output(
        [ffprobe_path if ffprobe_path else 'ffmpeg/ffprobe',
         '-v', 'error',
         '-show_entries', 'stream=codec_name,codec_type:format=duration,size:stream_tags=language,title',
         '-of', 'json',
         video_path
         ],
        stderr=subprocess.STDOUT).decode()
    print("output:", output)
    metadata = json.loads(output)
    audio_streams = []
    video_streams = []
    subtitle_streams = []
    for stream in metadata['streams']:
        if stream['codec_type'] == 'audio':
            audio_streams.append(parse_stream(stream))
        elif stream['codec_type'] == 'video':
            video_streams.append(parse_stream(stream))
        elif stream['codec_type'] == 'subtitle':
            subtitle_streams.append(parse_stream(stream))
    if queue is not None:
        queue.put((video_streams, audio_streams, subtitle_streams, duration_to_seconds(metadata['format']['duration'])))


# stream video using ffmpeg as cmd line commands
def stream_video_for_chromecast(video_path, base_folder, video_stream_index=0, audio_stream_index=0, ffmpeg_path=None):
    input_code = [
        ffmpeg_path if ffmpeg_path else './ffmpeg/ffmpeg',
        '-loglevel', 'verbose',
        '-i',
        video_path,
        '-map', f'0:v:{video_stream_index}', '-map', f'0:a:{audio_stream_index}',
        '-c:v', 'libx264', '-c:a', 'aac', '-ac', '2', '-ar', '44100',
        '-level', '4.1', '-maxrate', '10M',
        '-bufsize', '20M', '-hls_time', '10', '-hls_list_size', '0', '-hls_base_url', f'./hls/{base_folder}/',
        '-hls_segment_filename',
        f'./hls/{base_folder}/%03d.ts',
        f'./hls/{base_folder}/{base_folder}.m3u8'
    ]
    print("input:", input_code)
    try:
        output = subprocess.check_output(input_code, stderr=subprocess.STDOUT)
        print("output:", output)
    except subprocess.CalledProcessError as e:
        print('Command failed with exit status', e.returncode)
        print('Output:', e.output.decode())


def stream_subtitle_for_chromecast(video_path, base_folder, ffmpeg_path=None):
    output = subprocess.check_output(
        [ffmpeg_path if ffmpeg_path else '/ffmpeg/ffmpeg',
         '-i', video_path,
         '-map 0:s:0',
         '-c:s webvtt',
         f'/tracks/{base_folder}/%03d.vtt'
         ],
        stderr=subprocess.STDOUT).decode().split('\n')
    print("output:", output)


if __name__ == '__main__':
    __base_folder = "Arthur_Christmas_2011_720p_BluRay_DD_5_1_x264-playHD"
    __video_path = "D:\\Movies\\Arthur.Christmas.2011.720p.BluRay.DD+5.1.x264-playHD\\Arthur.Christmas.2011.720p.BluRay.DD+5.1.x264-playHD.mkv"
    # get_video_info(video_path)
    # create folder if not exists
    # os.makedirs(f'/hls/{base_folder}', exist_ok=True)
    stream_video_for_chromecast(
        __video_path,
        __base_folder,
        0,
        1,
    )
    time.sleep(10)
    # get_video_info("D:\Movies\Enemy 2013 1080p BluRay x264 EbP\Enemy 2013 1080p BluRay x264 EbP.mkv")
