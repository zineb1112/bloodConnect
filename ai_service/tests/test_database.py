import unittest
import pandas as pd
from unittest.mock import patch, MagicMock #H: to fake the db calls and magicmock is an anything always working object
from forecasting.database import load_city_data


#H: this is for testing the city data load

class TestDatabase(unittest.TestCase):
    @patch('forecasting.database.os.getenv')
    @patch('forecasting.database.psycopg2.connect')
    @patch('forecasting.database.pd.read_sql') #H:(mock_read_sql, mock_connect, mock_getenv)
    def test_load_city_data_with_env_vars(self, mock_read_sql, mock_connect, mock_getenv):
        #H: Mock environment variables needed for the load_city_data fct
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_HOST': 'localhost',
                'DB_PORT': '5432',
                'DB_NAME': 'test_db',
                'DB_USER': 'user',
                'DB_PASSWORD': 'pass'
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        #H: Mock connection and cursor
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Mock DataFrame
        mock_df = pd.DataFrame({
            'request_date': ['2023-01-01', '2023-02-01'],
            'blood_type': ['A+', 'B+'],
            'quantity_needed': [10, 20],
            'city': ['TestCity', 'TestCity'],
            'region': ['TestRegion', 'TestRegion']
        })
        mock_read_sql.return_value = mock_df

        result = load_city_data('TestCity', 'TestRegion')

        #H: verify if the db string is corretly formed from the vars
        mock_connect.assert_called_once_with('postgresql://user:pass@localhost:5432/test_db')
        mock_read_sql.assert_called_once() #H: the db is called
        args, kwargs = mock_read_sql.call_args
        # pd.read_sql(query, conn, params=(city, region))
        # params is passed as keyword argument
        self.assertEqual(kwargs['params'], ('TestCity', 'TestRegion'))
        pd.testing.assert_frame_equal(result, mock_df) #H: the data from db is the one used to forcast
        mock_conn.close.assert_called_once()

    @patch('forecasting.database.os.getenv')
    @patch('forecasting.database.psycopg2.connect')
    @patch('forecasting.database.pd.read_sql')
    def test_load_city_data_with_database_url(self, mock_read_sql, mock_connect, mock_getenv):
        mock_getenv.side_effect = lambda key: 'postgresql://user:pass@host:5432/db' if key == 'DATABASE_URL' else None

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        mock_df = pd.DataFrame()
        mock_read_sql.return_value = mock_df

        result = load_city_data('City', 'Region')

        mock_connect.assert_called_once_with('postgresql://user:pass@host:5432/db')
        pd.testing.assert_frame_equal(result, mock_df)


if __name__ == '__main__':
    unittest.main()