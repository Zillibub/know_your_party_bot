import pytest
from collections import Counter
from unittest.mock import MagicMock, patch
from know_your_party_bot.analysis.soundcloud_scrapper import SoundCloudScrapper


def test_find_genre_none():
    scraper = SoundCloudScrapper()
    with patch('requests.get') as mock_requests:
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = []
        mock_requests.return_value.content = mock_soup
        result = scraper.find_genre("InvalidArtistName")
        assert result is None


def test_find_genre_counter():
    scraper = SoundCloudScrapper()
    with patch('requests.get') as mock_requests:
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = [MagicMock(find=lambda x: MagicMock(attrs={'href': '/valid-artist'}))]
        mock_requests.return_value.content = mock_soup
        with patch('my_module.BeautifulSoup') as mock_bs:
            mock_bs.return_value.find_all.return_value = [
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Rock'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Electronic'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Rock'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Pop'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Pop'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Rock'}),
            ]
            result = scraper.find_genre("ValidArtistName")
            assert isinstance(result, Counter)


def test_find_genre_website_down():
    scraper = SoundCloudScrapper()
    scraper.base_url = "https://invalid-url.com"
    result = scraper.find_genre("ValidArtistName")
    assert result is None


def test_find_genre_multiple_tracks():
    scraper = SoundCloudScrapper()
    with patch('requests.get') as mock_requests:
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = [MagicMock(find=lambda x: MagicMock(attrs={'href': '/valid-artist'}))]
        mock_requests.return_value.content = mock_soup
        with patch('my_module.BeautifulSoup') as mock_bs:
            mock_bs.return_value.find_all.return_value = [
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Rock'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Electronic'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Rock'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Pop'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Pop'}),
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Rock'}),
            ]
            result = scraper.find_genre("ValidArtistWithMultipleTracks")
            expected_result = Counter({"Rock": 3, "Pop": 2, "Electronic": 1})
            assert result == expected_result


def test_find_genre_single_track():
    scraper = SoundCloudScrapper()
    with patch('requests.get') as mock_requests:
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = [MagicMock(find=lambda x: MagicMock(attrs={'href': '/valid-artist'}))]
        mock_requests.return_value.content = mock_soup
        with patch('my_module.BeautifulSoup') as mock_bs:
            mock_bs.return_value.find_all.return_value = [
                MagicMock(attrs={'itemprop': 'genre', 'content': 'Pop'}),
            ]
            result = scraper.find_genre("ValidArtistWithSingleTrack")
            expected_result = Counter({"Pop": 1})
            assert result == expected_result


def test_find_genre_invalid_artist():
    scraper = SoundCloudScrapper()
    with patch('requests.get') as mock_requests:
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = []
        mock_requests.return_value.content = mock_soup
        with pytest.raises(Exception):
            scraper.find_genre("$$$ Invalid Artist Name $$$")
