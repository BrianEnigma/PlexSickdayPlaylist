#!/usr/bin/env python3

import argparse
import random
from typing import List

import plexapi
import plexapi.library
import plexapi.playlist
import plexapi.server
import plexapi.video

from config import SickdayPlaylistConfig


class PlaylistGenerator:
    def __init__(self):
        self._count = 20
        self._erase_first = False
        self._parser = argparse.ArgumentParser(prog="Sickday Playlist Generator",
                                               description="Generate a Plex playlist for sickdays.",
                                               epilog="See the README for more detailed information.")
        self._plex = None

    def _parse_arguments(self):
        self._parser.add_argument('-c', '--count',
                                  type=int,
                                  action='store',
                                  required=False,
                                  default=20,
                                  help='Number of items to add to the sickday playlist')
        self._parser.add_argument('-e', '--erase',
                                  action='store_true',
                                  required=False,
                                  default=False,
                                  help='Whether to erase the existing playlist before adding')
        args = self._parser.parse_args()
        self._count = args.count
        self._erase_first = args.erase
        if self._count < 1 or self._count > 100:
            self._parser.error('Count should be between 1 and 100, inclusive.')
        if SickdayPlaylistConfig.playlist_name is None or len(SickdayPlaylistConfig.playlist_name) < 1:
            self._parser.error('Config should contain a valid playlist name')
        if len(SickdayPlaylistConfig.show_list) < 2:
            self._parser.error('Config should contain two or more television show names')
        # print(self._count)
        # print(self._erase_first)

    def _open_server(self):
        try:
            self._plex = plexapi.server.PlexServer(SickdayPlaylistConfig.server, SickdayPlaylistConfig.token)
        except Exception as e:
            self._parser.error('Unable to open server: ' + repr(e))

    def _generate_show_list(self) -> List[plexapi.video.Video]:
        result = []
        section = None
        previous_show_title = ''
        try:
            section = self._plex.library.section(title=SickdayPlaylistConfig.library_name)
        except Exception as e:
            self._parser.error('Unable to find library: ' + repr(e))
        for counter in range(self._count):
            # Find a random TV show, disallowing the same one twice in a row.
            while True:
                show_title = random.choice(SickdayPlaylistConfig.show_list)
                if show_title != previous_show_title:
                    break
            previous_show_title = show_title
            show = section.get(title=show_title)
            if type(show) is not plexapi.video.Show:
                self._parser.error('The title ' + show_title + ' does not match a TV show.')
            episode = random.choice(show.episodes())
            if type(episode) is not plexapi.video.Episode:
                self._parser.error(
                    'The title ' + show_title + ' did not return an episode. Does it contain more than video?')
            description = "{0:<30} {1}: {2}".format(show_title, episode.seasonEpisode, episode.title)
            print(description)
            result.append(episode)
        return result

    def _make_playlist(self, items: List[plexapi.video.Video]):
        matched_playlist = None
        # Find a matching playlist (if it exists)
        for p in self._plex.playlists(title=SickdayPlaylistConfig.playlist_name):
            if p.title == SickdayPlaylistConfig.playlist_name:
                matched_playlist = p
                break
        # If it exists and we need to erase it, erase it.
        if matched_playlist is not None and self._erase_first:
            matched_playlist.delete()
            matched_playlist = None
        # If it doesn't exist, create it, otherwise add to it.
        if matched_playlist is None:
            matched_playlist = self._plex.createPlaylist(title=SickdayPlaylistConfig.playlist_name, items=items)
        else:
            matched_playlist.addItems(items)
        print('Added ' + str(len(items)) + ' items to ' + matched_playlist.title)

    def process(self):
        self._parse_arguments()
        self._open_server()
        items = self._generate_show_list()
        self._make_playlist(items)


playlist_generator = PlaylistGenerator()
playlist_generator.process()
