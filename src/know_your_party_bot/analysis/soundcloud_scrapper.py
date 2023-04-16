import requests
from typing import Union
from collections import Counter
from bs4 import BeautifulSoup


class SoundCloudScrapper:
    base_url = "https://soundcloud.com"

    def find_artist(self, artist_name: str) -> Union[str, None]:
        """
        Given the name of an artist, returns the url of the artist's SoundCloud page.
        :param artist_name: str, the name of the artist to search for.
        :return:  str or None, the url of the artist's SoundCloud page, or None if no artists are found.
        """
        url = f'{self.base_url}/search/people?q={artist_name}'
        response = requests.get(url)
        search_soup = BeautifulSoup(response.content, 'html.parser')
        search_soup.findAll("h2")
        hrefs = []
        for search_result in search_soup.findAll("h2"):
            hrefs.append(search_result.a.attrs["href"])
        if len(hrefs) == 0:
            return None
        link = [x for x in hrefs if x.count("/") == 1][0]
        return f'{self.base_url}{link}'

    @staticmethod
    def get_genre(artist_url: str) -> Counter:
        """
        Given the url of an artist's SoundCloud page, returns a Counter object with the
        genres of their top tracks.
        :param artist_url: str, the url of the artist's SoundCloud page.
        :return:  Counter or None, a Counter object containing the genres found, or None if no genres are found.
        """
        response = requests.get(artist_url)
        artist_soup = BeautifulSoup(response.content, 'html.parser')

        genres = []
        for track in artist_soup.find_all(itemprop="track"):
            genre_soup = track.find(itemprop="genre")
            if genre_soup:
                genres.append(genre_soup.attrs["content"])

        return Counter(genres)
