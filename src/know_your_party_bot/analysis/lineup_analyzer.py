import seaborn as sns
import matplotlib.pyplot as plt
from typing import List
from collections import Counter
from know_your_party_bot.analysis.soundcloud_scrapper import SoundCloudScrapper


class LineupAnalyser:

    def __init__(
            self,
            artists: List[str]
    ):
        self.artists = artists

    def analyse(self):
        genres_counters = [
            SoundCloudScrapper().find_genre(artist)
            for artist in self.artists
        ]

        combined = sum(genres_counters, Counter())

        top_genres = dict(combined.most_common(5))

        # Plot a donut pie chart using seaborn
        plt.figure(figsize=(6, 6))
        ax = sns.color_palette("pastel").as_hex()
        plt.pie(top_genres.keys(), labels=top_genres.values(), colors=ax,
                autopct='%1.1f%%', pctdistance=0.85, startangle=90)
        my_circle = plt.Circle((0, 0), 0.7, color='white')
        p = plt.gcf()
        p.gca().add_artist(my_circle)
        plt.title('Top 5 genres in the lineup', fontsize=14)
        plt.show()
