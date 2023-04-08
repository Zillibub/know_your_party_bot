import requests
from typing import Union
from collections import Counter
from bs4 import BeautifulSoup


class SoundCloudScrapper:

    base_url = "https://soundcloud.com"

    def find_genere(self, artist_name: str) ->Union[str, None]:
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
        tracks = soup.find_all('li', {'class': 'trackList__item'})

        genres = []
        for track in tracks:
            genres.append(track.find(itemprop="genre").attrs["content"])

        return Counter(genres)



