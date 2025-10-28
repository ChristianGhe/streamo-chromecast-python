import json
import os
import subprocess
import time
from queue import Queue
from run_cmd_line_command import run_command


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


def print_current_dir():
    print("Current dir: ", os.getcwd())


# stream video using ffmpeg as cmd line commands
def stream_video_for_chromecast(video_path, base_folder, video_stream_index=0, audio_stream_index=0, ffmpeg_path=None):
    current_dir = os.getcwd()
    os.makedirs(f'{current_dir}/hls/{base_folder}', exist_ok=True)
    input_code = [
        ffmpeg_path if ffmpeg_path else f'{current_dir}/ffmpeg/ffmpeg',
        '-loglevel', 'debug',
        '-i',
        video_path,
        '-map', f'0:v:{video_stream_index}', '-map', f'0:a:{audio_stream_index}',
        '-c:v', 'libx264',
        '-c:a', 'aac', '-ac', '2', '-ar', '44100',
        '-level', '4.1',
        '-maxrate', '10M',
        '-bufsize', '20M',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-hls_base_url', f'{base_folder}/',
        '-hls_segment_filename', f'{current_dir}/hls/{base_folder}/%03d.ts',
        f'{current_dir}/hls/{base_folder}.m3u8'
    ]
    print("input:", input_code)
    rc = run_command(input_code)
    print("rc stream video:", rc)
    # try:
    #     output = subprocess.check_output(input_code, stderr=subprocess.STDOUT)
    #     print("output:", output)
    # except subprocess.CalledProcessError as e:
    #     print('Command failed with exit status', e.returncode)
    #     print('Output:', e.output.decode())


def stream_subtitle_for_chromecast(video_path, filename, subtitle_stream_index, ffmpeg_path=None):
    current_dir = os.getcwd()
    input_code = [ffmpeg_path if ffmpeg_path else f'{current_dir}/ffmpeg/ffmpeg',
                  '-i', video_path,
                  '-map', f'0:s:{subtitle_stream_index}',
                  '-c:s', 'webvtt',
                  f'{current_dir}/tracks/{filename}.vtt'
                  ]
    print("subtitle input:", input_code)
    rc = run_command(input_code)
    print("rc stream subtitles:", rc)
    # try:
    #     output = subprocess.check_output(input_code, stderr=subprocess.STDOUT)
    #     print("output:", output)
    # except subprocess.CalledProcessError as e:
    #     print('Command failed with exit status', e.returncode)
    #     print('Output:', e.output.decode())


def convert_srt_to_vtt(srt_path, filename, ffmpeg_path=None):
    print("srt_path:", srt_path)
    current_dir = os.getcwd()
    input_code = [ffmpeg_path if ffmpeg_path else f'{current_dir}/ffmpeg/ffmpeg',
                  '-y',
                  '-i', srt_path,
                  '-c:s', 'webvtt',
                  f'{current_dir}/tracks/{filename}.vtt'
                  ]
    print("subtitle input:", input_code)
    rc = run_command(input_code)
    print("rc stream subtitles:", rc)


if __name__ == '__main__':
    __base_folder = "Arthur_Christmas_2011_720p_BluRay_DD_5_1_x264_playHD"
    # __base_folder = "testasdf"
    __video_path = "D:\\Movies\\Arthur.Christmas.2011.720p.BluRay.DD+5.1.x264-playHD\\Arthur.Christmas.2011.720p.BluRay.DD+5.1.x264-playHD.mkv"
    # get_video_info(video_path)
    # create folder if not exists
    # os.makedirs(f'./hls/{__base_folder}', exist_ok=True)
    # stream_video_for_chromecast(
    #     __video_path,
    #     __base_folder,
    #     0,
    #     1,
    # )
    print_current_dir()
    __srt_path = "D:/Movies/Three.Days.of.the.Condor.1975.720p.Blu-ray.DD5.1.x264-playHD/Three.Days.of.the.Condor.1975.720p.Blu-ray.DD5.1.x264-playHDen.srt"
    convert_srt_to_vtt(__srt_path, "Three.Days.of.the.Condor.1975.720p.Blu-ray.DD5.1.x264-playHDen")
    # stream_subtitle_for_chromecast(__video_path, __base_folder, 0)
    # time.sleep(10)
    # get_video_info("D:\Movies\Enemy 2013 1080p BluRay x264 EbP\Enemy 2013 1080p BluRay x264 EbP.mkv")
