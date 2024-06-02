#!/usr/bin/env python3

from typing import List

class SickdayPlaylistConfig:
    server: str = 'http://127.0.0.1:32400'
    # For the token, see: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
    token: str = 'abcdefghijklmnopqrst'
    library_name: str = 'TV Shows'
    playlist_name: str = 'SickdayQueue'
    show_list: List[str] = [
        'I Love Lucy',
        'The Addams Family',
        "Gilligan's Island",
        'The Monkees',
        'Batman',
        'Knight Rider',
        'Lost in Space'
    ]
