import json
import os

__data = {
    "categories": [
        {
            "name": "Movies",
            "hls": "http://{ip}:{port}/hls/",
            "dash": "https://commondatastorage.googleapis.com/gtv-videos-bucket/CastVideos/dash/",
            "mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/CastVideos/mp4/",
            "images": "https://commondatastorage.googleapis.com/gtv-videos-bucket/CastVideos/images/",
            "tracks": "http://{ip}:{port}/tracks/",
            "videos": []
        }
    ]
}


def init_video_list(filename, data, ip_address, port):
    print(f"Initializing video_list.json with ip address {ip_address} and port {port}")
    # Create video_list.json if it doesn't exist and create base structure
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            data_str = json.dumps(data)
            data_str = data_str.replace("{ip}", ip_address)
            data_str = data_str.replace("{port}", port)
            data = json.loads(data_str)
            json.dump(data, f, indent=4)


def set_ip_address_to_data(file_name, ip_address, port):
    print(f"Setting ip address {ip_address} to video_list.json")
    with open(file_name, 'r') as f:
        # load json file and replace ip of tracks and hls for "Movies" category
        data = json.load(f)
        data["categories"][0]["hls"] = f"http://{ip_address}:{port}/hls/"
        data["categories"][0]["tracks"] = f"http://{ip_address}:{port}/tracks/"
        # save json file
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)


def add_video_to_list(file_name, video_name, duration, subtitle_name, subtitle_language):
    print(f"Adding video {video_name} to video_list.json with duration {duration} and subtitle {subtitle_name} "
          f"and subtitle language {subtitle_language}")
    with open(file_name, 'r') as f:
        print("filename", f)
        # load json file and replace ip of tracks and hls for "Movies" category
        data = json.load(f)
        print(data["categories"])
        data["categories"][0]["videos"].append({
            "subtitle": "description",
            "sources": [
                {
                    "type": "hls",
                    "mime": "application/x-mpegurl",
                    "url": video_name + ".m3u8"
                }
            ],
            "thumb": "images/DesigningForGoogleCast-480x270.jpg",
            "image-480x270": "480x270/DesigningForGoogleCast2-480x270.jpg",
            "image-780x1200": "780x1200/DesigningForGoogleCast-887x1200.jpg",
            "title": video_name,
            "studio": "Twenty Century Fox",
            "duration": duration,
            "tracks": [
                {
                    "id": "1",
                    "type": "text",
                    "subtype": "captions",
                    "contentId": video_name + ".vtt",
                    "name": subtitle_name,
                    "language": subtitle_language
                }
            ]
        })
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)


def add_subtitle_to_list(file_name, video_name, duration, subtitle_name, subtitle_language):
    print(f"Adding subtitle {subtitle_name} to video {video_name} in video_list.json")
    with open(file_name, 'r') as f:
        # load json file and replace ip of tracks and hls for "Movies" category
        data = json.load(f)
        video_found = False
        for video in data["categories"][0]["videos"]:
            if video["title"] == video_name:
                # get tracks size and add new track with different id
                track_size = len(video["tracks"])
                video["tracks"].append({
                    "id": str(track_size + 1),
                    "type": "text",
                    "subtype": "captions",
                    "contentId": video_name + ".vtt",
                    "name": subtitle_name,
                    "language": subtitle_language
                })
                video_found = True
                break
        if not video_found:
            print(f"Video {video_name} not found in video_list.json")
            add_video_to_list(file_name, video_name, 0, subtitle_name, subtitle_language)

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    add_video_to_list('video_list.json', "apvral-scenes.from.a.marriage.720p[flt]", 10196, "English", "en")
