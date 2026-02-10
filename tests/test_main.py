import pytest
from unittest.mock import MagicMock, patch
from src import main
import datetime

@pytest.fixture
def mock_dependencies():
    with patch("src.main.config.load_config") as mock_conf, \
         patch("src.main.downloader") as mock_dl, \
         patch("src.main.parser") as mock_parser, \
         patch("src.main.matcher") as mock_matcher, \
         patch("src.main.storage") as mock_storage:
        
        # Setup config mock return
        mock_config_obj = MagicMock()
        mock_config_obj.keywords = ["test"]
        mock_config_obj.sections = ["dou1"]
        mock_conf.return_value = mock_config_obj
        
        yield mock_conf, mock_dl, mock_parser, mock_matcher, mock_storage

def test_job_process_dou_flow(mock_dependencies):
    mock_conf, mock_dl, mock_parser, mock_matcher, mock_storage = mock_dependencies
    
    # Setup mocks
    mock_dl.fetch_article_urls.return_value = ["http://fake.url"]
    mock_dl.fetch_content.return_value = "<html>Title<p>test content</p></html>"
    
    mock_parser.extract_text.return_value = "test content"
    mock_parser.extract_title.return_value = "Title"
    
    mock_matcher.find_matches.return_value = ["match"]
    
    # Run
    main.job_process_dou()
    
    # Verify flow
    mock_dl.fetch_article_urls.assert_called()
    mock_dl.fetch_content.assert_called_with("http://fake.url")
    mock_parser.extract_text.assert_called()
    mock_matcher.find_matches.assert_called()
    mock_storage.save_match.assert_called()

def test_main_entry_setup():
    """Test that main initializes config and scheduler."""
    with patch("src.main.scheduler") as mock_sched, \
         patch("src.main.config") as mock_conf, \
         patch("src.main.time.sleep", side_effect=KeyboardInterrupt): 
        
        try:
            main.main()
        except KeyboardInterrupt:
            pass
        
        mock_sched.create_scheduler.assert_called()
        mock_sched.schedule_daily_job.assert_called()
        mock_sched.start_scheduler.assert_called()
