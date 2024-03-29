import io
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Tuple
from collections import Counter
from dataclasses import dataclass
from know_your_party_bot.analysis.soundcloud_scrapper import SoundCloudScrapper


@dataclass
class AnalysisResult:
    image_bytes: bytes
    unknown_artist_names: List[str]


class LineupAnalyser:

    def __init__(
            self,
    ):
        self.artist_urls = []
        self.unknown_artist_names = []
        self.top_genres = None
        self.scrapper = SoundCloudScrapper()

    def analyse_raw(self, message: str) -> AnalysisResult:
        # TODO take command from some list, not hardcode
        message = message.replace("/analyse", "")  # remove bot command
        try:
            artist_names = self.scrapper.clean_names_with_openai(message)
        except Exception as e:
            print(e)  # TODO use logging library here
            artist_names = message.split('\n')[1:]

        return self.analyse(artist_names)

    def analyse(self, artist_names: List[str]) -> AnalysisResult:

        for artist_name in artist_names:
            artist_url = self.scrapper.find_artist(artist_name)
            if not artist_url:
                self.unknown_artist_names.append(artist_name)
            else:
                self.artist_urls.append(artist_url)

        self.top_genres = self._get_top_genres()

        image_bytes = self.create_image()

        analysis_result = AnalysisResult(
            image_bytes=image_bytes,
            unknown_artist_names=self.unknown_artist_names
        )
        return analysis_result

    def _get_top_genres(self, amount: int = 5):
        genres_counters = [
            SoundCloudScrapper().get_genre(artist_url)
            for artist_url in self.artist_urls
        ]

        genres_counters = [x for x in genres_counters if x]

        combined = sum(genres_counters, Counter())

        return dict(combined.most_common(amount))

    def _get_most_popular(self, amount: int = 5) -> List[Tuple[str, int]]:
        """
        Returns a list of the most popular SoundCloud artists among the artist URLs in this object,
        sorted by the number of subscribers. Each item in the list is a tuple with the artist URL
        and the number of subscribers.

        :param amount: int, the maximum number of artists to return. Default is 5.
        :return: list of tuples, the most popular SoundCloud artists among the artist URLs in this object.
        """
        sub_amount = [
            SoundCloudScrapper().get_subscriber_count(artist_url)
            for artist_url in self.artist_urls
        ]

        amount = min(amount, len(sub_amount))
        most_popular = [(s, x) for x, s in sorted(zip(sub_amount, self.artist_urls))][-amount:]

        return most_popular

    def create_image(self) -> bytes:

        if self.top_genres is None:
            raise ValueError("top_genres field not set")

        # Plot a donut pie chart using seaborn
        plt.figure(figsize=(6, 6))
        ax = sns.color_palette("pastel").as_hex()
        plt.pie(self.top_genres.values(), labels=self.top_genres.keys(), colors=ax,
                autopct='%1.1f%%', pctdistance=0.85, startangle=90)
        my_circle = plt.Circle((0, 0), 0.7, color='white')
        p = plt.gcf()
        p.gca().add_artist(my_circle)
        plt.title('Top 5 genres in the lineup', fontsize=14)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        return buffer.getvalue()
