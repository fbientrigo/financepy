import datetime
import unittest

import pandas as pd
from unittest.mock import MagicMock, patch

from src.data import DataLoader


class TestDataLoaderResilience(unittest.TestCase):
    @patch('src.data.yf.download')
    def test_update_ticker_raises_when_close_missing(self, mock_download):
        target_date = datetime.date(2025, 1, 5)
        mock_frame = pd.DataFrame(
            {'Open': [100]}, index=pd.date_range('2025-01-01', periods=1)
        )
        mock_download.return_value = mock_frame

        store = MagicMock()
        store.get_last_date.return_value = None

        loader = DataLoader(store)

        with self.assertRaisesRegex(ValueError, 'Close'):
            loader._update_ticker('FAKE', target_date=target_date)

        store.save.assert_not_called()

    @patch('src.data.yf.download')
    def test_update_ticker_empty_download_path(self, mock_download):
        """Guard empty download path that currently references undefined end_date."""
        target_date = datetime.date(2025, 1, 5)
        mock_download.return_value = pd.DataFrame()

        store = MagicMock()
        store.get_last_date.return_value = None

        loader = DataLoader(store)

        loader._update_ticker('FAKE', target_date=target_date)

        store.save.assert_not_called()

    def test_load_combined_prices_ffill_before_start_date_filter(self):
        store = MagicMock()
        aaa_index = pd.date_range('2025-01-01', periods=3, freq='D')
        bbb_index = pd.to_datetime(['2025-01-01', '2025-01-03'])
        df_aaa = pd.DataFrame({'Close': [1, 2, 3]}, index=aaa_index)
        df_bbb = pd.DataFrame({'Close': [10, 30]}, index=bbb_index)
        data_map = {'AAA': df_aaa, 'BBB': df_bbb}
        store.load.side_effect = lambda ticker: data_map[ticker]

        loader = DataLoader(store)
        prices = loader.load_combined_prices(['AAA', 'BBB'], start_date=datetime.date(2025, 1, 2))

        self.assertEqual(prices.at[pd.Timestamp('2025-01-02'), 'BBB'], 10)

    @patch('src.data.DataLoader._update_ticker')
    def test_fetch_and_store_collects_errors_per_ticker(self, mock_update):
        target_date = datetime.date(2025, 1, 5)

        def side_effect(ticker, target_date):
            if ticker == 'BAD':
                raise RuntimeError('boom')

        mock_update.side_effect = side_effect

        store = MagicMock()
        loader = DataLoader(store)

        updated_count, errors = loader.fetch_and_store(['OK', 'BAD'], target_date=target_date)

        self.assertEqual(updated_count, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn('BAD', errors[0])
        self.assertIn('boom', errors[0])
