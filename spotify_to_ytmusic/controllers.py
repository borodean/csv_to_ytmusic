import time
from datetime import datetime

from spotify_to_ytmusic.setup import setup as setup_func
from spotify_to_ytmusic.csv import CSV
from spotify_to_ytmusic.ytmusic import YTMusicTransfer


def _get_csv_playlist(csv, playlist):
    try:
        return csv.getCSVPlaylist(playlist)
    except Exception as ex:
        print(
            "Could not get CSV playlist. Please check the playlist file.\n Error: " + repr(ex)
        )
        return


def _print_success(name, playlistId):
    print(
        f"Success: created playlist '{name}' at\n"
        f"https://music.youtube.com/playlist?list={playlistId}"
    )


def _init():
    return CSV(), YTMusicTransfer()


def _create_ytmusic(args, playlist, ytmusic):
    date = ""
    if args.date:
        date = " " + datetime.today().strftime("%m/%d/%Y")
    name = args.name + date if args.name else playlist["name"] + date
    info = playlist["description"] if (args.info is None) else args.info
    videoIds = ytmusic.search_songs(playlist["tracks"])

    playlistId = ytmusic.create_playlist(
        name, info, "PUBLIC" if args.public else "PRIVATE", videoIds
    )
    _print_success(name, playlistId)


def create(args):
    csv, ytmusic = _init()
    playlist = _get_csv_playlist(csv, args.playlist)
    _create_ytmusic(args, playlist, ytmusic)


def update(args):
    csv, ytmusic = _init()
    playlist = _get_csv_playlist(csv, args.playlist)
    playlistId = ytmusic.get_playlist_id(args.name)
    videoIds = ytmusic.search_songs(playlist["tracks"])
    if not args.append:
        ytmusic.remove_songs(playlistId)
    time.sleep(2)
    ytmusic.add_playlist_items(playlistId, videoIds)


def remove(args):
    ytmusic = YTMusicTransfer()
    ytmusic.remove_playlists(args.pattern)


def setup(args):
    setup_func(args.file)
