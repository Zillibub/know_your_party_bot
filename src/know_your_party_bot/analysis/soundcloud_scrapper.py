import openai
import requests
import json
from typing import List
from typing import Union
from collections import Counter
from bs4 import BeautifulSoup
from know_your_party_bot.core.settings import settings

openai.api_key = settings.openai_token


class SoundCloudScrapper:
    base_url = "https://soundcloud.com"

    @staticmethod
    def clean_names_with_openai(content) -> List[str]:
        """
        turns this:
            DAMES BROWN [LIVE PA]
            Melvo Baptiste
            Natasha Diggs
            Simon Dunmore [Last Ever DJ Set]
        into this:
            ['DAMES BROWN', 'Melvo Baptiste', 'Natasha Diggs', 'Simon Dunmore']
        basically it removes all useless information
        since it uses language model, use it with caution
        :param content:
        :return:
        """
        prompt_content = "Reply only with text that can be parsed with a python json library, result must be a list" \
                         f"extract only artist and group names from this data : {content}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt_content},
            ]
        )
        completion = response.choices[0].message.content

        result = json.loads(completion)

        if not isinstance(result, list):
            raise ValueError("Parsing failed")

        return result

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

    @staticmethod
    def get_subscriber_count(artist_url: str) -> int:
        """
        Given the url of an artist's SoundCloud page, returns the number of subscribers.
        :param artist_url: str, the url of the artist's SoundCloud page.
        :return:  int or None, the number of subscribers, or None if no count is found.
        """
        response = requests.get(artist_url)
        artist_soup = BeautifulSoup(response.content, 'html.parser')

        count_soup = artist_soup.find(class_="infoStats__value", string=lambda text: "Followers" in text)
        count_str = count_soup.string.strip()
        # Remove commas and convert to integer
        count = int(count_str.replace(",", ""))
        return count
