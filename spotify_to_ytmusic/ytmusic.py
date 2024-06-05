import os
import re
from collections import OrderedDict

from ytmusicapi import YTMusic

from spotify_to_ytmusic.cache import Cache
from spotify_to_ytmusic.utils.match import get_best_fit_song_id
from spotify_to_ytmusic.settings import Settings

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


class YTMusicTransfer:
    def __init__(self):
        settings = Settings()
        headers = settings["youtube"]["headers"]
        assert headers.startswith("{"), "ytmusicapi headers not set or invalid"
        self.api = YTMusic(headers, settings["youtube"]["user_id"])

    def create_playlist(self, name, info, privacy="PRIVATE", tracks=None):
        return self.api.create_playlist(name, info, privacy, video_ids=tracks)

    def search_songs(self, tracks):
        videoIds = []
        songs = list(tracks)
        notFound = list()
        cache = Cache()
        try:
            for i, song in enumerate(songs):
                if not i % 10:
                    print(f"YouTube tracks: {i}/{len(songs)}")
                name = re.sub(r" \(feat.*\..+\)", "", song["name"])
                query = song["artist"] + " " + name
                query = query.replace(" &", "")
                if query in cache:
                    targetSong = cache[query]
                else:
                    result = self.api.search(query)
                    if not len(result) or not (targetSong := get_best_fit_song_id(result, song)):
                        notFound.append(query)
                        continue

                    cache[query] = targetSong

                videoIds.append(targetSong)

        finally:
            cache.save()

        with open(path + "noresults_youtube.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(notFound))
            f.write("\n")
            f.close()

        return videoIds

    def add_playlist_items(self, playlistId, videoIds):
        videoIds = OrderedDict.fromkeys(videoIds)
        self.api.add_playlist_items(playlistId, videoIds)

    def get_playlist_id(self, name):
        pl = self.api.get_library_playlists(10000)
        try:
            playlist = next(x for x in pl if x["title"].find(name) != -1)["playlistId"]
            return playlist
        except:
            raise Exception("Playlist title not found in playlists")

    def remove_songs(self, playlistId):
        items = self.api.get_playlist(playlistId, 10000)
        if "tracks" in items:
            self.api.remove_playlist_items(playlistId, items["tracks"])

    def remove_playlists(self, pattern):
        playlists = self.api.get_library_playlists(10000)
        p = re.compile("{0}".format(pattern))
        matches = [pl for pl in playlists if p.match(pl["title"])]
        print("The following playlists will be removed:")
        print("\n".join([pl["title"] for pl in matches]))
        print("Please confirm (y/n):")

        choice = input().lower()
        if choice[:1] == "y":
            [self.api.delete_playlist(pl["playlistId"]) for pl in matches]
            print(str(len(matches)) + " playlists deleted.")
        else:
            print("Aborted. No playlists were deleted.")
