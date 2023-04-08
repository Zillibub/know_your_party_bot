import requests
from typing import Union
from collections import Counter
from bs4 import BeautifulSoup


class SoundCloudScrapper:

    base_url = "https://soundcloud.com"

    def find_genre(self, artist_name: str) -> Union[Counter, None]:
        """
        Given the name of an artist, returns a Counter object with the
        genres of their top tracks on SoundCloud.
        :param artist_name: str, the name of the artist to search for.
        :return:  Counter or None, a Counter object containing the genres found, or None if no artists are found.
        """
        url = f'{self.base_url}/search/people?q={artist_name}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        artists = soup.find_all('h2', {'class': 'soundTitle__title sc-link-dark'})
        if len(artists) == 0:
            return None
        link = artists[0].find('a')['href']   # using the most popular
        artist_url = f'{self.base_url}{link}'

        response = requests.get(artist_url)
        artist_soup = BeautifulSoup(response.content, 'html.parser')
        tracks = artist_soup.find_all('li', {'class': 'trackList__item'})

        genres = []
        for track in tracks:
            genres.append(track.find(itemprop="genre").attrs["content"])

        return Counter(genres)
