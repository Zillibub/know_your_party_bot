import io
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List
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

    def analyse(self, artist_names: List[str]) -> AnalysisResult:

        scrapper = SoundCloudScrapper()

        for artist_name in artist_names:
            artist_url = scrapper.find_artist(artist_name)
            if not artist_url:
                self.unknown_artist_names.append(artist_name)
            else:
                self.artist_urls.append(artist_url)

        genres_counters = [
            SoundCloudScrapper().get_genre(artist_url)
            for artist_url in self.artist_urls
        ]

        genres_counters = [x for x in genres_counters if x]

        combined = sum(genres_counters, Counter())

        top_genres = dict(combined.most_common(5))

        # Plot a donut pie chart using seaborn
        plt.figure(figsize=(6, 6))
        ax = sns.color_palette("pastel").as_hex()
        plt.pie(top_genres.values(), labels=top_genres.keys(), colors=ax,
                autopct='%1.1f%%', pctdistance=0.85, startangle=90)
        my_circle = plt.Circle((0, 0), 0.7, color='white')
        p = plt.gcf()
        p.gca().add_artist(my_circle)
        plt.title('Top 5 genres in the lineup', fontsize=14)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        analysis_result = AnalysisResult(
            image_bytes=buffer.getvalue(),
            unknown_artist_names=self.unknown_artist_names
        )
        return analysis_result
