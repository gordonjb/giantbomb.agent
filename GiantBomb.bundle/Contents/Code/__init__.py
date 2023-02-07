"""
A Plex agent for Giant Bomb dot com.
"""
# ################### Imports ###################
from datetime import datetime
import re
from season_markers import SEASONS
from duders import DUDERS

# ################### Agent Constants ###################
AGENT_NAME = "Giant Bomb dot agent"
AGENT_LANGUAGES = [Locale.Language.English]
AGENT_PRIMARY_PROVIDER = True
AGENT_ACCEPTS_FROM = ['com.plexapp.agents.localmedia']

# ################### JSON keys ###################
RESULTS = 'results'
COUNT = 'number_of_total_results'
ID = 'id'
GUID = 'guid'
TITLE = 'title'
NAME = 'name'
IMAGE = 'image'
LOGO = 'logo'
DECK = 'deck'
HOSTS = 'hosts'
CREW = 'crew'
DATE = 'publish_date'
VIDEOS_LINK = 'api_videos_url'
ORIG_URL = 'original_url'
THUMB_URL = 'thumb_url'
SCREEN_URL = 'screen_large_url'

# ################### URLs ###################
REQUEST_SUFFIX = "api_key={api_key}&format=json"
GB_VIDEO_SHOWS = "https://www.giantbomb.com/api/video_shows/?" + REQUEST_SUFFIX
SHOW_ID_FILTER = "&filter=id:{show_id}"
SEARCH_FIELD_LIST = "&field_list=" + ID + "," + TITLE + "," + IMAGE
UPDATE_FIELD_LIST = "&field_list=" + ID + "," + TITLE + "," + IMAGE + "," + LOGO + "," + DECK + "," + VIDEOS_LINK
VIDEOS_FIELD_LIST = "&field_list=" + GUID + "," + NAME + "," + IMAGE + "," + DECK + "," + CREW + "," + HOSTS + "," + DATE
SHOW_VIDEOS = "{show_videos_url}&" + REQUEST_SUFFIX + "&sort=publish_date:asc" + VIDEOS_FIELD_LIST


# ################### Functions ###################
def natural_sort_key(sort):
    """
    Function to sort seasons correctly.
    Taken from: https://github.com/ZeroQI/YouTube-Agent.bundle/blob/7efbf4da0c06f98ca54a57e5412ea9b18d3b84b4/Contents/Code/__init__.py#L13
    "Avoid 1, 10, 2, 20... 
    Usage: list.sort(key=natural_sort_key), sorted(list, key=natural_sort_key)"
    """
    return [int(text) if text.isdigit() else text for text in re.split(re.compile('([0-9]+)'), str(sort).lower())]


def get_episode(show_videos, show_id, season, episode):
    """
    Given sorted list of all videos in a show `show_videos`,
    return the video that matches the requested `season` &
    `episode`.
    """
    # Iterate over the list, checking IDs against season-markers as we go.
    # If we encounter a marker, split to new season, reset ep count and start again
    # Keep going until we match the requested item
    season_markers = SEASONS.get(show_id)
    current_season = 0
    if season_markers is None:
        current_season = 1
    current_episode = 1

    for video in show_videos:
        if season_markers is not None:
            marker = season_markers[current_season] if current_season < len(season_markers) else None
            if marker is not None and marker.get('first_ep') == video[GUID]:
                Log.Debug("[" + AGENT_NAME + "] [get_episode] Matched marker " + marker.get('name'))
                current_season += 1
                current_episode = 1

        if current_season > 0:
            if current_season == int(season) and current_episode == int(episode):
                return video
            current_episode += 1

    return None


def set_role(username, role):
    """
    Given a Plex role object `role` to fill, and a `username` as
    returned by the API, look up the username in known people
    and fill out the role with their name and photo if it exists.
    Otherwise use the `username`.
    """
    duder = DUDERS.get(username)
    if duder is None:
        role.name = ' ' + username
    else:
        role.name = duder.get('name')
        role.role = ' ' + username
        role.photo = duder.get('pic')


def get_season_name(show_id, season):
    """
    Check the list of season markers, and return the name of the
    season of the specified show if one exists, or else None.
    """
    season = int(season)
    season_markers = SEASONS.get(show_id)

    if season_markers is not None and len(season_markers) >= season:
        return season_markers[season - 1].get('name')
    
    return None


# ################### Agent ###################
def Start():
    """
    On start
    """
    HTTP.CacheTime = CACHE_1DAY


class GiantBombDotAgent(Agent.TV_Shows):
    """
    Agent class to match Giant Bomb shows as TV Show library items.
    """
    name = AGENT_NAME
    languages = AGENT_LANGUAGES
    primary_provider = AGENT_PRIMARY_PROVIDER
    accepts_from = AGENT_ACCEPTS_FROM

    def search(self, results, media, lang, manual):
        """
        manual: true/false depending on if the search was invoked manually
        results: array that should be filled with MetadataSearchResult object representing candidates for selection
        media: the input to the search. known fields:
            'openSubtitlesHash': uhh i guess a file hash?
            'name': a media search name, as determined by the scanner.
            'year': a file year, as determined by the scanner.
            'filename': the full path of the file.
            'plexHash': some sort of hash for plex
            'duration': the length of the media
            'id': some id
        """
        shows = JSON.ObjectFromURL((GB_VIDEO_SHOWS + SEARCH_FIELD_LIST).format(api_key=Prefs['apiKey']))[RESULTS]
        exact_matches = [x for x in shows if x[TITLE] == media.show]
        for match in exact_matches:
            results.Append(MetadataSearchResult(
                id=str(match[ID]),
                name=str(match[TITLE]),
                score=100,
                lang=lang,
                thumb=str(match[IMAGE][ORIG_URL])
            ))


    def update(self, metadata, media, lang, force):
        """
        metadata: object to be updated with the required show metadata
        media: the object(s) being updated
        """
        # TODO: this method fails the following lint checks
        # R:155, 4: Too many branches (18/12) (too-many-branches)
        # R:155, 4: Too many statements (67/50) (too-many-statements)
        # R:155, 4: Too many local variables (25/15) (too-many-locals)
        Log.Info("[" + AGENT_NAME + "] [update] Updating video show with ID: " + metadata.id)

        # Get the (hopefully 1) show with the specified ID
        results = JSON.ObjectFromURL((GB_VIDEO_SHOWS + SHOW_ID_FILTER + UPDATE_FIELD_LIST).format(api_key=Prefs['apiKey'], show_id=metadata.id))
        if results[COUNT] > 1:
            raise Exception('Only one result should be returned from an update query')
        show_details = results[RESULTS][0]
        if int(show_details[ID]) != int(metadata.id):
            raise Exception('Somehow the returned show has a different ID')

        metadata.title = str(show_details[TITLE])
        metadata.summary = str(show_details[DECK])
        metadata.studio = 'Giant Bomb'

        show_artwork_url = show_details[IMAGE][ORIG_URL]
        show_artwork_thumb_url = show_details[IMAGE][THUMB_URL]
        valid_names = list()
        if show_artwork_url not in metadata.art:
            try:
                metadata.art[show_artwork_url] = Proxy.Preview(HTTP.Request(show_artwork_thumb_url).content)
                valid_names.append(show_artwork_url)
            except Exception as e:
                Log.Info("[" + AGENT_NAME + "] [update] Exception requesting show artwork: " + str(e))

        metadata.art.validate_keys(valid_names)

        if show_details[LOGO] is not None:
            logo_url = show_details[LOGO][ORIG_URL]
            logo_thumb_url = show_details[LOGO][THUMB_URL]
            valid_names = list()
            if logo_url not in metadata.posters:
                try:
                    metadata.posters[logo_url] = Proxy.Preview(HTTP.Request(logo_thumb_url).content)
                    valid_names.append(logo_url)
                except Exception as e:
                    Log.Info("[" + AGENT_NAME + "] [update] Exception requesting show logo: " + str(e))

                metadata.posters.validate_keys(valid_names)

        Log.Info("[" + AGENT_NAME + "] [update] Requesting show API page for: " + metadata.id)
        show_videos = JSON.ObjectFromURL(SHOW_VIDEOS.format(api_key=Prefs['apiKey'], show_videos_url=show_details[VIDEOS_LINK]))[RESULTS]

        # Fill show roles
        cast_set = set()
        metadata.roles.clear()
        for video in show_videos:
            if video[CREW] is not None:
                cast_set.update([x.strip() for x in video[CREW].split(',')])
            if video[HOSTS] is not None:
                cast_set.update([x.strip() for x in video[HOSTS].split(',')])

        Log.Info("[" + AGENT_NAME + "] [update] Found cast: " + ', '.join(cast_set))

        for cast in cast_set:
            role = metadata.roles.new()
            set_role(cast, role)

        for season in sorted(media.seasons, key=natural_sort_key):
            Log.Info("[" + AGENT_NAME + "] [update] Have season: " + season)

            # The following is code to look up the name of a season.
            # However, from my research (https://github.com/ZeroQI/Hama.bundle/issues/452),
            # Plex doesn't allow agents to update these fields. Perhaps we could do something
            # like this (https://gist.github.com/JonnyWong16/bafa266c7ce4a1dbd6d715132a502c03)
            # and have a script to bulk update all season names.
            season_name = get_season_name(show_id=metadata.id, season=season)
            if season_name is not None:
                metadata.seasons[season].title = season_name

            for episode in sorted(media.seasons[season].episodes, key=natural_sort_key):
                Log.Info("[" + AGENT_NAME + "] [update] Have episode: " + episode)
                episode_metadata = metadata.seasons[season].episodes[episode]
                video = get_episode(show_videos, metadata.id, season, episode)
                if video is None:
                    Log.Warn("[" + AGENT_NAME + "] [update] Could not find S" + season + " E" + episode + " in list of show videos")
                else:
                    episode_metadata.title = video[NAME]
                    episode_metadata.originally_available_at = datetime.strptime(video[DATE], "%Y-%m-%d %H:%M:%S").date()
                    episode_metadata.summary = video[DECK]
                    screen_url = video[IMAGE][SCREEN_URL]
                    # As far as I can tell, other agents call the low res thumb, and this pattern seems
                    # to work for show art, however when I do it here we just get low res thumbnails
                    # so I've just set screen_thumb_url to the high res copy
                    #screen_thumb_url = video[IMAGE][THUMB_URL]
                    screen_thumb_url = video[IMAGE][SCREEN_URL]
                    valid_names = list()
                    if screen_url is not None and screen_url not in episode_metadata.thumbs:
                        try:
                            episode_metadata.thumbs[screen_url] = Proxy.Preview(HTTP.Request(screen_thumb_url).content)
                            valid_names.append(screen_url)
                        except Exception as e:
                            Log.Info("[" + AGENT_NAME + "] [update] Exception requesting thumbnail: " + str(e))
                    episode_metadata.thumbs.validate_keys(valid_names)

        Log.Info("[" + AGENT_NAME + "] [update] Finished")
