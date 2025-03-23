"""Tests for the government members scraping module."""

import pandas as pd
import pytest
from unittest.mock import MagicMock, patch, Mock
from bs4 import BeautifulSoup

from open_discourse.steps.politicians.scrape_mgs import (
    fetch_wikipedia_content,
    extract_birth_death_years,
    parse_government_position,
    extract_politician_data,
    main,
    DEFAULT_VALUE,
)


class TestScrapeMGs:
    """Tests for the scrape_mgs module functions."""

    def test_extract_birth_death_years_only_birth(self):
        """Test extracting only a birth year."""
        birth_date, death_date = extract_birth_death_years("(* 1970)")
        assert birth_date == 1970
        assert death_date == DEFAULT_VALUE

    def test_extract_birth_death_years_both(self):
        """Test extracting both birth and death years."""
        birth_date, death_date = extract_birth_death_years("(* 1960 † 2020)")
        assert birth_date == 1960
        assert death_date == 2020

    def test_extract_birth_death_years_invalid(self):
        """Test extracting with no years present."""
        birth_date, death_date = extract_birth_death_years("(no dates)")
        assert birth_date == DEFAULT_VALUE
        assert death_date == DEFAULT_VALUE

    def test_parse_government_position_simple(self):
        """Test parsing a simple government position."""
        position, from_year, until_year = parse_government_position("1990–1995 Minister for Finance")
        assert position == "Minister for Finance"
        assert from_year == 1990
        assert until_year == 1995

    def test_parse_government_position_seit(self):
        """Test parsing an ongoing government position with 'seit'."""
        position, from_year, until_year = parse_government_position("seit 2020 Minister for Environment")
        assert position == "Minister for Environment"
        assert from_year == 2020
        assert until_year == DEFAULT_VALUE

    def test_parse_government_position_single_year(self):
        """Test parsing a position with only one year."""
        position, from_year, until_year = parse_government_position("2018 Special Envoy")
        assert position == "Special Envoy"
        assert from_year == 2018
        assert until_year == 2018

    def test_parse_government_position_two_terms(self):
        """Test parsing a position with two separate terms."""
        result = parse_government_position("1995–2000, 2005–2010 Defense Minister")
        assert len(result) == 5
        position, from_year1, until_year1, from_year2, until_year2 = result
        assert position == "Defense Minister"
        assert from_year1 == 1995
        assert until_year1 == 2000
        assert from_year2 == 2005
        assert until_year2 == 2010

    def test_parse_government_position_invalid(self):
        """Test parsing an invalid position text raises ValueError."""
        with pytest.raises(ValueError):
            parse_government_position("Invalid position text")

    @patch("requests.get")
    def test_fetch_wikipedia_content_success(self, mock_get):
        """Test successful Wikipedia content fetching."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = """
        <html>
            <div id="mw-content-text">
                <div id="content-div">Content here</div>
            </div>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Just call the function with our mocked response
        result = fetch_wikipedia_content("https://example.com")
        
        # Check that the function called our mocked get
        mock_get.assert_called_once_with("https://example.com")
        assert result is not None

    @patch("requests.get")
    def test_fetch_wikipedia_content_no_content(self, mock_get):
        """Test Wikipedia fetching with no content section."""
        # Mock response without the right content div
        mock_response = Mock()
        mock_response.text = "<html><body>No content div</body></html>"
        mock_get.return_value = mock_response
        
        result = fetch_wikipedia_content("https://example.com")
        
        assert result is None

    @patch("requests.get")
    def test_fetch_wikipedia_content_request_error(self, mock_get):
        """Test handling of request error."""
        # Mock a request exception
        mock_get.side_effect = Exception("Connection error")
        
        result = fetch_wikipedia_content("https://example.com")
        
        assert result is None

    def test_extract_politician_data(self):
        """Test extracting politician data from HTML content."""
        # Create a simple HTML structure for testing
        html = """
        <div>
            <ul>
                <li>
                    <a href="#">John Doe</a> (* 1950)
                    <ul>
                        <li>1990–1995 Minister of Finance</li>
                        <li>2000–2005 Prime Minister</li>
                    </ul>
                </li>
                <li>
                    <a href="#">Jane Smith</a>
                    <a href="#">SPD</a> (* 1960)
                    <ul>
                        <li>1998–2002 Minister of Justice</li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        content_div = BeautifulSoup(html, "html.parser")
        
        # Call the function with our test HTML
        with patch('open_discourse.steps.politicians.scrape_mgs.logger'):
            result_df = extract_politician_data(content_div)
        
        # Check the result
        assert isinstance(result_df, pd.DataFrame)
        assert not result_df.empty
        assert "ui" in result_df.columns
        assert "first_name" in result_df.columns
        assert "last_name" in result_df.columns
        assert "position" in result_df.columns

    @patch('open_discourse.steps.politicians.scrape_mgs.fetch_wikipedia_content')
    @patch('open_discourse.steps.politicians.scrape_mgs.extract_politician_data')
    @patch('open_discourse.steps.politicians.scrape_mgs.save_pickle')
    def test_main_success(self, mock_save_pickle, mock_extract_data, mock_fetch_content):
        """Test successful execution of the main function."""
        # Setup mocks
        mock_content = MagicMock()
        mock_df = pd.DataFrame({"test": [1, 2, 3]})
        mock_fetch_content.return_value = mock_content
        mock_extract_data.return_value = mock_df
        mock_save_pickle.return_value = True
        
        # Call the main function
        result = main(None)
        
        # Verify the result and that all expected functions were called
        assert result is True
        mock_fetch_content.assert_called_once()
        mock_extract_data.assert_called_once_with(mock_content)
        mock_save_pickle.assert_called_once()

    @patch('open_discourse.steps.politicians.scrape_mgs.fetch_wikipedia_content')
    def test_main_fetch_content_failure(self, mock_fetch_content):
        """Test main function handling when fetch_wikipedia_content fails."""
        # Setup mock to return None (failure)
        mock_fetch_content.return_value = None
        
        # Call the main function
        result = main(None)
        
        # Verify the result
        assert result is False
        mock_fetch_content.assert_called_once()

    @patch('open_discourse.steps.politicians.scrape_mgs.fetch_wikipedia_content')
    @patch('open_discourse.steps.politicians.scrape_mgs.extract_politician_data')
    def test_main_extract_data_failure(self, mock_extract_data, mock_fetch_content):
        """Test main function handling when extract_politician_data fails."""
        # Setup mocks
        mock_content = MagicMock()
        mock_fetch_content.return_value = mock_content
        mock_extract_data.side_effect = Exception("Extraction error")
        
        # Call the main function
        result = main(None)
        
        # Verify the result
        assert result is False
        mock_fetch_content.assert_called_once()
        mock_extract_data.assert_called_once_with(mock_content)