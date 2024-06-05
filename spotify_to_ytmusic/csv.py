import re


class CSV:
    def getCSVPlaylist(self, file_path):
        tracks = []

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    track = parse_track_line(line)
                    if track:
                        tracks.append(track)

        return {
            "tracks": tracks,
            "name": file_path,
            "description": "",
        }


def parse_track_line(line):
    match = re.match(r'^(.+?) - (.+?) - (\d{1,2}:\d{2})?$', line)
    if match:
        artist, name, duration = match.groups()
        duration_in_seconds = convert_duration_to_seconds(duration)
        return {
            'artist': artist.strip(),
            'name': name.strip(),
            'duration': duration_in_seconds,
        }
    else:
        return None

def convert_duration_to_seconds(duration):
    if not duration:
        return None
    minutes, seconds = map(int, duration.split(':'))
    return minutes * 60 + seconds
