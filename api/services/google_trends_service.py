import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError, TooManyRequestsError
import pandas as pd

logger = logging.getLogger(__name__)

class GoogleTrendsService:
    """
    Service for fetching Google Trends data with intelligent caching to avoid rate limiting
    """
    
    # Rate limiting configuration
    RATE_LIMIT_DELAY = 15  # seconds between requests (increased from 5 to 15 for better rate limiting)
    MAX_RETRIES = 3
    CACHE_EXPIRY_HOURS = 6  # Cache data for 6 hours (increased from 1 to reduce API calls)
    
    # Supported diseases
    SUPPORTED_DISEASES = ['Diabetes', 'Malaria', 'Meningitis', 'Cholera']
    
    # Data types
    DATA_TYPES = [
        'interest_over_time',
        'related_queries', 
        'related_topics',
        'interest_by_region'
    ]
    
    def __init__(self):
        self.pytrends = None
        self.last_request_time = 0
        self.request_count = 0
        self._initialize_pytrends()
    
    def _initialize_pytrends(self):
        """Initialize pytrends with proper configuration"""
        try:
            self.pytrends = TrendReq(
                hl='en-US',
                tz=0,  # UTC
                timeout=(10, 25),  # (connect timeout, read timeout)
                retries=2,
                backoff_factor=0.1
            )
            logger.info("Google Trends service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Trends service: {e}")
            self.pytrends = None 

    def _generate_cache_key(self, disease_name: str, data_type: str, time_range: str, geo: str = '') -> str:
        """Generate a unique cache key for the request"""
        key_data = f"{disease_name}:{data_type}:{time_range}:{geo}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _should_fetch_from_google(self, cache_obj: Any) -> bool:
        """Determine if we should fetch fresh data from Google"""
        if not cache_obj:
            return True
        
        # Check if cache is expired
        if cache_obj.is_expired:
            return True
        
        # Check if cache is stale and we haven't exceeded retry limit
        if cache_obj.is_stale and cache_obj.fetch_count < self.MAX_RETRIES:
            return True
        
        # Check if we have rate limit issues
        if cache_obj.last_error and 'rate limit' in cache_obj.last_error.lower():
            return False
        
        return False
    
    def _respect_rate_limit(self):
        """Respect Google's rate limits by sleeping between requests"""
        logger.info(f"Rate limiting: sleeping for {self.RATE_LIMIT_DELAY} seconds")
        time.sleep(self.RATE_LIMIT_DELAY)
        logger.info("Rate limit delay completed, proceeding with request")
    
    def _handle_rate_limit_error(self, attempt: int):
        """Handle rate limit errors with exponential backoff"""
        base_delay = self.RATE_LIMIT_DELAY
        exponential_delay = base_delay * (2 ** attempt)  # Exponential backoff
        max_delay = 60  # Cap at 60 seconds
        delay = min(exponential_delay, max_delay)
        
        logger.warning(f"Rate limit hit (attempt {attempt + 1}), sleeping for {delay} seconds")
        time.sleep(delay)
        logger.info(f"Exponential backoff delay completed, retrying...")
    
    def _log_request(self, disease_name: str, data_type: str, time_range: str, 
                     geo: str, status: str, response_time: float = None, 
                     error_message: str = None, cache_hit: bool = False):
        """Log the request for monitoring"""
        try:
            from disease_monitor.models import GoogleTrendsRequestLog
            GoogleTrendsRequestLog.objects.create(
                timestamp=timezone.now(),
                disease_name=disease_name,
                data_type=data_type,
                timeframe=time_range,
                geo=geo,
                status=status,
                response_time=response_time,
                error_message=error_message,
                cache_hit=cache_hit
            )
        except Exception as e:
            logger.error(f"Failed to log request: {e}")

    def _fetch_from_google_single(self, disease_name: str, data_type: str, time_range: str = None, geo: str = None) -> Tuple[bool, Any, str]:
        """
        Fetch a single data type from Google Trends API (without rate limiting)
        
        Args:
            disease_name: Name of the disease
            data_type: Type of data to fetch
            time_range: Timeframe for the data (optional, for logging)
            geo: Geographic location (optional, for logging)
            
        Returns:
            Tuple of (success, data, error_message)
        """
        if not self.pytrends:
            return False, None, "Google Trends service not initialized"
        
        start_time = time.time()
        
        try:
            logger.info(f"=== DEBUG: Fetching {data_type} for {disease_name} ===")
            
            # Fetch data based on type with error handling for empty responses
            if data_type == 'interest_over_time':
                data = self.pytrends.interest_over_time()
            elif data_type == 'related_queries':
                try:
                    data = self.pytrends.related_queries()
                    # Check if data is empty or has no content
                    if not data or (isinstance(data, dict) and not any(data.values())):
                        logger.warning(f"Google Trends returned empty data for {disease_name} - {data_type}")
                        # Return empty but valid structure
                        data = {disease_name: {'top': pd.DataFrame(), 'rising': pd.DataFrame()}}
                except IndexError as e:
                    logger.warning(f"Google Trends returned empty rankedList for {disease_name} - {data_type}: {e}")
                    # Return empty but valid structure
                    data = {disease_name: {'top': pd.DataFrame(), 'rising': pd.DataFrame()}}
            elif data_type == 'related_topics':
                try:
                    data = self.pytrends.related_topics()
                    # Check if data is empty or has no content
                    if not data or (isinstance(data, dict) and not any(data.values())):
                        logger.warning(f"Google Trends returned empty data for {disease_name} - {data_type}")
                        # Return empty but valid structure
                        data = {disease_name: {'top': pd.DataFrame(), 'rising': pd.DataFrame()}}
                except IndexError as e:
                    logger.warning(f"Google Trends returned empty rankedList for {disease_name} - {data_type}: {e}")
                    # Return empty but valid structure
                    data = {disease_name: {'top': pd.DataFrame(), 'rising': pd.DataFrame()}}
            elif data_type == 'interest_by_region':
                data = self.pytrends.interest_by_region()
            else:
                return False, None, f"Unsupported data type: {data_type}"
            
            logger.info(f"Raw Google Trends data for {disease_name} - {data_type}: {type(data)}")
            logger.info(f"Raw data repr: {repr(data)}")
            
            # Safe data inspection to avoid index errors
            try:
                if hasattr(data, 'shape'):
                    logger.info(f"DataFrame shape: {data.shape}")
                    logger.info(f"DataFrame columns: {list(data.columns) if hasattr(data, 'columns') else 'No columns'}")
                    logger.info(f"DataFrame head: {data.head() if not data.empty else 'Empty DataFrame'}")
                elif isinstance(data, dict):
                    logger.info(f"Dict keys: {list(data.keys())}")
                    logger.info(f"Dict length: {len(data)}")
                    
                    # Safe iteration over dict items
                    for i, (key, value) in enumerate(data.items()):
                        logger.info(f"  Item {i}: Key='{key}', Type={type(value)}")
                        
                        if hasattr(value, 'shape'):
                            logger.info(f"    DataFrame shape: {value.shape}")
                            logger.info(f"    DataFrame columns: {list(value.columns)}")
                        elif isinstance(value, dict):
                            logger.info(f"    Dict with keys: {list(value.keys())}")
                            logger.info(f"    Dict length: {len(value)}")
                        elif isinstance(value, list):
                            logger.info(f"    List length: {len(value)}")
                            if value:
                                logger.info(f"    First item type: {type(value[0])}")
                                logger.info(f"    First item: {value[0]}")
                        else:
                            logger.info(f"    Value: {value}")
                    
                    # Check if disease_name exists in data
                    if disease_name in data:
                        logger.info(f"Found disease '{disease_name}' in data")
                        disease_data = data[disease_name]
                        logger.info(f"Data for {disease_name}: {type(disease_data)}")
                        
                        if hasattr(disease_data, 'shape'):
                            logger.info(f"  DataFrame shape: {disease_data.shape}")
                            logger.info(f"  DataFrame columns: {list(disease_data.columns)}")
                            if not disease_data.empty:
                                logger.info(f"  DataFrame head: {disease_data.head()}")
                        elif isinstance(disease_data, dict):
                            logger.info(f"  Dict keys: {list(disease_data.keys())}")
                            for key, value in disease_data.items():
                                logger.info(f"    Key '{key}': type={type(value)}")
                                if hasattr(value, 'shape'):
                                    logger.info(f"      DataFrame shape: {value.shape}")
                                    if not value.empty:
                                        logger.info(f"      DataFrame head: {value.head()}")
                                elif isinstance(value, list):
                                    logger.info(f"      List length: {len(value)}")
                                    if value:
                                        logger.info(f"      First item: {value[0]}")
                        elif isinstance(disease_data, list):
                            logger.info(f"  List length: {len(disease_data)}")
                            if disease_data:
                                logger.info(f"  First item: {disease_data[0]}")
                        else:
                            logger.info(f"  Data content: {disease_data}")
                    else:
                        logger.warning(f"Disease name '{disease_name}' not found in data keys: {list(data.keys())}")
                        # Try to find any available data
                        for key, value in data.items():
                            logger.info(f"Available key '{key}': type={type(value)}")
                            if hasattr(value, 'shape'):
                                logger.info(f"  DataFrame shape: {value.shape}")
                                if not value.empty:
                                    logger.info(f"  DataFrame head: {value.head()}")
                            elif isinstance(value, dict):
                                logger.info(f"  Dict with keys: {list(value.keys())}")
                            elif isinstance(value, list):
                                logger.info(f"  List length: {len(value)}")
                                if value:
                                    logger.info(f"  First item: {value[0]}")
                elif isinstance(data, list):
                    logger.info(f"Data is list with {len(data)} items")
                    if data:
                        logger.info(f"First item type: {type(data[0])}")
                        logger.info(f"First item: {data[0]}")
                        if len(data) > 1:
                            logger.info(f"Second item: {data[1]}")
                else:
                    logger.info(f"Data type: {type(data)}")
                    if hasattr(data, '__len__'):
                        try:
                            logger.info(f"Data length: {len(data)}")
                        except Exception as e:
                            logger.warning(f"Could not get length: {e}")
                    
                    if hasattr(data, '__iter__'):
                        try:
                            # Safe iteration to avoid index errors
                            data_list = list(data)
                            logger.info(f"Data content (first 5 items): {data_list[:5] if len(data_list) > 5 else data_list}")
                        except Exception as e:
                            logger.warning(f"Could not iterate over data: {e}")
                            logger.warning(f"Data repr: {repr(data)}")
                            
            except Exception as debug_error:
                logger.error(f"Error during data inspection: {debug_error}")
                logger.error(f"Debug error type: {type(debug_error).__name__}")
                import traceback
                logger.error(f"Debug error traceback: {traceback.format_exc()}")
            
            response_time = time.time() - start_time
            
            # Log successful request with actual parameters
            self._log_request(
                disease_name, data_type, time_range or 'unknown', geo or 'unknown',
                'success', response_time
            )
            
            logger.info(f"=== END DEBUG: Successfully fetched {data_type} for {disease_name} ===")
            return True, data, None
            
        except TooManyRequestsError as e:
            response_time = time.time() - start_time
            error_msg = f"Rate limited by Google: {str(e)}"
            logger.error(f"Rate limit error for {disease_name} - {data_type}: {error_msg}")
            self._log_request(
                disease_name, data_type, time_range or 'unknown', geo or 'unknown',
                'rate_limited', response_time, error_msg
            )
            return False, None, error_msg
            
        except ResponseError as e:
            response_time = time.time() - start_time
            error_msg = f"Google API error: {str(e)}"
            logger.error(f"Google API error for {disease_name} - {data_type}: {error_msg}")
            self._log_request(
                disease_name, data_type, time_range or 'unknown', geo or 'unknown',
                'error', response_time, error_msg
            )
            return False, None, error_msg
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error for {disease_name} - {data_type}: {error_msg}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            self._log_request(
                disease_name, data_type, time_range or 'unknown', geo or 'unknown',
                'error', response_time, error_msg
            )
            return False, None, error_msg

    def _process_interest_over_time(self, data: Any, disease_name: str) -> Dict[str, Any]:
        """Process interest over time data into useful metrics"""
        # Handle both DataFrame and dict responses from pytrends
        if isinstance(data, dict):
            # Convert dict to DataFrame if possible
            try:
                import pandas as pd
                data = pd.DataFrame(data)
            except Exception:
                # If conversion fails, try to extract data from dict structure
                if disease_name in data:
                    # Handle case where data is already in the right format
                    interest_data = []
                    for date_str, value in data[disease_name].items():
                        try:
                            # Try to parse date and convert value
                            from datetime import datetime
                            if isinstance(date_str, str):
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            else:
                                date_obj = date_str
                            interest_data.append({
                                'date': date_obj.strftime('%Y-%m-%d'),
                                'interest': float(value)
                            })
                        except (ValueError, TypeError):
                            continue
                    
                    if interest_data:
                        return self._calculate_metrics_from_interest_data(interest_data)
                    return {}
                return {}
        
        # Handle DataFrame case
        if hasattr(data, 'empty') and data.empty:
            return {}
        
        # Convert to list of dictionaries
        interest_data = []
        try:
            if disease_name in data.columns:
                for index, row in data.iterrows():
                    try:
                        # Handle different date formats
                        if hasattr(index, 'strftime'):
                            date_str = index.strftime('%Y-%m-%d')
                        else:
                            date_str = str(index)
                        
                        interest_value = float(row[disease_name])
                        interest_data.append({
                            'date': date_str,
                            'interest': interest_value
                        })
                    except (ValueError, TypeError):
                        continue
        except Exception as e:
            logger.error(f"Error processing interest data: {e}")
            return {}
        
        if not interest_data:
            return {}
        
        return self._calculate_metrics_from_interest_data(interest_data)

    def _calculate_metrics_from_interest_data(self, interest_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics from interest data"""
        if not interest_data:
            return {}
        
        try:
            # Sort by date to get current and historical data
            sorted_data = sorted(interest_data, key=lambda x: x['date'])
            
            # Safe access to list elements with bounds checking
            if len(sorted_data) > 0:
                current_interest = sorted_data[-1]['interest']
            else:
                current_interest = 0
                
            peak_interest = max(item['interest'] for item in interest_data) if interest_data else 0
            average_interest = sum(item['interest'] for item in interest_data) / len(interest_data) if interest_data else 0
            
            # Calculate trend direction and strength
            if len(sorted_data) >= 2:
                # Safe slicing with bounds checking
                recent_count = min(3, len(sorted_data))
                older_count = min(3, len(sorted_data))
                
                recent_avg = sum(item['interest'] for item in sorted_data[-recent_count:]) / recent_count
                older_avg = sum(item['interest'] for item in sorted_data[:older_count]) / older_count
                
                if recent_avg > older_avg * 1.1:
                    trend_direction = 'rising'
                    trend_strength = min(1.0, (recent_avg - older_avg) / older_avg) if older_avg > 0 else 0.0
                elif recent_avg < older_avg * 0.9:
                    trend_direction = 'falling'
                    trend_strength = min(1.0, (older_avg - recent_avg) / older_avg) if older_avg > 0 else 0.0
                else:
                    trend_direction = 'stable'
                    trend_strength = 0.0
            else:
                trend_direction = 'stable'
                trend_strength = 0.0
            
            # Estimate total searches (this is a rough approximation)
            total_searches = int(average_interest * 10000)  # Rough estimate
            
            return {
                'current_interest': current_interest,
                'trend_direction': trend_direction,
                'trend_strength': round(trend_strength, 2),
                'total_searches': total_searches,
                'peak_interest': peak_interest,
                'average_interest': round(average_interest, 2),
                'data_points': len(interest_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}

    def _process_related_queries(self, data: Any, disease_name: str) -> Dict[str, Any]:
        """
        Process related queries data from Google Trends
        
        Args:
            data: Raw data from Google Trends
            disease_name: Name of the disease
            
        Returns:
            Dictionary with processed related queries data
        """
        logger.info(f"=== DEBUG: Processing related queries for {disease_name} ===")
        logger.info(f"Raw data type: {type(data)}")
        
        try:
            # Handle different data types
            if isinstance(data, dict):
                logger.info(f"Raw data: {data}")
                
                # Check if data has the expected structure
                if disease_name in data and isinstance(data[disease_name], dict):
                    disease_data = data[disease_name]
                    logger.info(f"Data is dict with keys: {list(data.keys())}")
                    logger.info(f"Data for {disease_name}: {disease_data}")
                    logger.info(f"Data type for {disease_name}: {type(disease_data)}")
                    
                    # Extract 'top' and 'rising' DataFrames
                    top_queries = []
                    rising_queries = []
                    
                    if 'top' in disease_data and disease_data['top'] is not None:
                        if isinstance(disease_data['top'], pd.DataFrame):
                            top_queries = disease_data['top'].to_dict('records')
                        else:
                            logger.warning(f"Top queries data is not a DataFrame: {type(disease_data['top'])}")
                    
                    if 'rising' in disease_data and disease_data['rising'] is not None:
                        if isinstance(disease_data['rising'], pd.DataFrame):
                            rising_queries = disease_data['rising'].to_dict('records')
                        else:
                            logger.warning(f"Rising queries data is not a DataFrame: {type(disease_data['rising'])}")
                    
                    logger.info(f"Extracted top_queries: {len(top_queries)} items")
                    logger.info(f"Extracted rising_queries: {len(rising_queries)} items")
                    
                    return {
                        'top_queries': top_queries,
                        'rising_queries': rising_queries,
                        'total_top': len(top_queries),
                        'total_rising': len(rising_queries)
                    }
                else:
                    logger.warning(f"Unexpected data structure for {disease_name}: {data}")
                    return {
                        'top_queries': [],
                        'rising_queries': [],
                        'total_top': 0,
                        'total_rising': 0
                    }
            
            elif isinstance(data, pd.DataFrame):
                logger.info(f"Data is DataFrame with shape: {data.shape}")
                logger.info(f"DataFrame columns: {list(data.columns)}")
                
                # Convert DataFrame to list of dictionaries
                queries_list = data.to_dict('records')
                return {
                    'top_queries': queries_list,
                    'rising_queries': [],
                    'total_top': len(queries_list),
                    'total_rising': 0
                }
            
            elif isinstance(data, list):
                logger.info(f"Data is list with {len(data)} items")
                return {
                    'top_queries': data,
                    'rising_queries': [],
                    'total_top': len(data),
                    'total_rising': 0
                }
            
            else:
                logger.warning(f"Unexpected data type: {type(data)}")
                return {
                    'top_queries': [],
                    'rising_queries': [],
                    'total_top': 0,
                    'total_rising': 0
                }
                
        except Exception as e:
            logger.error(f"Error processing related queries for {disease_name}: {str(e)}")
            return {
                'top_queries': [],
                'rising_queries': [],
                'total_top': 0,
                'total_rising': 0,
                'error': str(e)
            }
        finally:
            logger.info(f"=== END DEBUG: Related queries for {disease_name} ===")

    def _process_related_topics(self, data: Any, disease_name: str) -> Dict[str, Any]:
        """
        Process related topics data from Google Trends
        
        Args:
            data: Raw data from Google Trends
            disease_name: Name of the disease
            
        Returns:
            Dictionary with processed related topics data
        """
        logger.info(f"=== DEBUG: Processing related topics for {disease_name} ===")
        logger.info(f"Raw data type: {type(data)}")
        logger.info(f"Raw data repr: {repr(data)}")
        
        try:
            # Handle different data types
            if isinstance(data, dict):
                logger.info(f"Raw data: {data}")
                logger.info(f"Data keys: {list(data.keys())}")
                logger.info(f"Data length: {len(data)}")
                
                # Check if data has the expected structure
                if disease_name in data and isinstance(data[disease_name], dict):
                    disease_data = data[disease_name]
                    logger.info(f"Data is dict with keys: {list(data.keys())}")
                    logger.info(f"Data for {disease_name}: {disease_data}")
                    logger.info(f"Data type for {disease_name}: {type(disease_data)}")
                    logger.info(f"Keys in disease_data: {list(disease_data.keys()) if isinstance(disease_data, dict) else 'Not a dict'}")
                    
                    # Extract 'top' and 'rising' DataFrames
                    top_topics = []
                    rising_topics = []
                    
                    if 'top' in disease_data and disease_data['top'] is not None:
                        logger.info(f"Top topics data type: {type(disease_data['top'])}")
                        if isinstance(disease_data['top'], pd.DataFrame):
                            logger.info(f"Top topics DataFrame shape: {disease_data['top'].shape}")
                            logger.info(f"Top topics DataFrame columns: {list(disease_data['top'].columns)}")
                            if not disease_data['top'].empty:
                                logger.info(f"Top topics DataFrame head: {disease_data['top'].head()}")
                            try:
                                top_topics = disease_data['top'].to_dict('records')
                                logger.info(f"Successfully converted top topics to records: {len(top_topics)} items")
                            except Exception as e:
                                logger.error(f"Error converting top topics to records: {e}")
                                logger.error(f"Top topics DataFrame info: {disease_data['top'].info() if hasattr(disease_data['top'], 'info') else 'No info method'}")
                                top_topics = []
                        else:
                            logger.warning(f"Top topics data is not a DataFrame: {type(disease_data['top'])}")
                            logger.warning(f"Top topics data content: {disease_data['top']}")
                    else:
                        logger.warning(f"No 'top' key found in disease_data for {disease_name}")
                    
                    if 'rising' in disease_data and disease_data['rising'] is not None:
                        logger.info(f"Rising topics data type: {type(disease_data['rising'])}")
                        if isinstance(disease_data['rising'], pd.DataFrame):
                            logger.info(f"Rising topics DataFrame shape: {disease_data['rising'].shape}")
                            logger.info(f"Rising topics DataFrame columns: {list(disease_data['rising'].columns)}")
                            if not disease_data['rising'].empty:
                                logger.info(f"Rising topics DataFrame head: {disease_data['rising'].head()}")
                            try:
                                rising_topics = disease_data['rising'].to_dict('records')
                                logger.info(f"Successfully converted rising topics to records: {len(rising_topics)} items")
                            except Exception as e:
                                logger.error(f"Error converting rising topics to records: {e}")
                                logger.error(f"Rising topics DataFrame info: {disease_data['rising'].info() if hasattr(disease_data['rising'], 'info') else 'No info method'}")
                                rising_topics = []
                        else:
                            logger.warning(f"Rising topics data is not a DataFrame: {type(disease_data['rising'])}")
                            logger.warning(f"Rising topics data content: {disease_data['rising']}")
                    else:
                        logger.warning(f"No 'rising' key found in disease_data for {disease_name}")
                    
                    logger.info(f"Extracted top_topics: {len(top_topics)} items")
                    logger.info(f"Extracted rising_topics: {len(rising_topics)} items")
                    
                    # If we still have no data, try to extract from any available keys
                    if not top_topics and not rising_topics:
                        logger.info("No standard 'top' or 'rising' data found, checking for alternative structures")
                        for key, value in disease_data.items():
                            logger.info(f"Checking key '{key}' with type {type(value)} and value: {value}")
                            if isinstance(value, pd.DataFrame) and not value.empty:
                                logger.info(f"Found DataFrame in key '{key}' with shape {value.shape}")
                                logger.info(f"DataFrame columns: {list(value.columns)}")
                                logger.info(f"DataFrame head: {value.head()}")
                                # Try to extract topics from this DataFrame
                                try:
                                    # Safe conversion with bounds checking
                                    if hasattr(value, 'to_dict'):
                                        topics_list = value.to_dict('records')
                                        logger.info(f"Converted to records: {len(topics_list)} items")
                                        if topics_list and isinstance(topics_list, list) and len(topics_list) > 0:
                                            top_topics = topics_list
                                            logger.info(f"Extracted {len(top_topics)} topics from key '{key}'")
                                            break
                                        else:
                                            logger.warning(f"Empty or invalid topics list from key '{key}': {topics_list}")
                                    else:
                                        logger.warning(f"DataFrame in key '{key}' has no to_dict method")
                                except Exception as e:
                                    logger.warning(f"Failed to extract topics from key '{key}': {e}")
                                    logger.warning(f"Value type: {type(value)}, has to_dict: {hasattr(value, 'to_dict')}")
                                    logger.warning(f"Value info: {value.info() if hasattr(value, 'info') else 'No info method'}")
                                    continue  # Continue to next key if this one fails
                    
                    # Final safety check - ensure we have valid lists
                    try:
                        if not isinstance(top_topics, list):
                            logger.warning(f"top_topics is not a list: {type(top_topics)}, converting to empty list")
                            top_topics = []
                        if not isinstance(rising_topics, list):
                            logger.warning(f"rising_topics is not a list: {type(rising_topics)}, converting to empty list")
                            rising_topics = []
                    except Exception as e:
                        logger.warning(f"Error during final safety check: {e}")
                        top_topics = []
                        rising_topics = []
                    
                    logger.info(f"Final extracted top_topics: {len(top_topics)} items")
                    logger.info(f"Final extracted rising_topics: {len(rising_topics)} items")
                    
                    # Additional safety check for list contents
                    try:
                        if top_topics:
                            logger.info(f"First top topic: {top_topics[0] if len(top_topics) > 0 else 'None'}")
                        if rising_topics:
                            logger.info(f"First rising topic: {rising_topics[0] if len(rising_topics) > 0 else 'None'}")
                    except Exception as e:
                        logger.warning(f"Error accessing first items: {e}")
                    
                    return {
                        'top_topics': top_topics,
                        'rising_topics': rising_topics,
                        'total_top': len(top_topics),
                        'total_rising': len(rising_topics)
                    }
                else:
                    logger.warning(f"Unexpected data structure for {disease_name}: {data}")
                    if disease_name not in data:
                        logger.warning(f"Disease name '{disease_name}' not found in data keys")
                    if disease_name in data and not isinstance(data[disease_name], dict):
                        logger.warning(f"Data for {disease_name} is not a dict: {type(data[disease_name])}")
                    return {
                        'top_topics': [],
                        'rising_topics': [],
                        'total_top': 0,
                        'total_rising': 0
                    }
            
            elif isinstance(data, pd.DataFrame):
                logger.info(f"Data is DataFrame with shape: {data.shape}")
                logger.info(f"DataFrame columns: {list(data.columns)}")
                if not data.empty:
                    logger.info(f"DataFrame head: {data.head()}")
                
                # Convert DataFrame to list of dictionaries
                try:
                    topics_list = data.to_dict('records')
                    logger.info(f"Successfully converted DataFrame to records: {len(topics_list)} items")
                    if topics_list:
                        logger.info(f"First item: {topics_list[0]}")
                    return {
                        'top_topics': topics_list,
                        'rising_topics': [],
                        'total_top': len(topics_list),
                        'total_rising': 0
                    }
                except Exception as e:
                    logger.error(f"Error converting DataFrame to records: {e}")
                    logger.error(f"DataFrame info: {data.info() if hasattr(data, 'info') else 'No info method'}")
                    return {
                        'top_topics': [],
                        'rising_topics': [],
                        'total_top': 0,
                        'total_rising': 0
                    }
            
            elif isinstance(data, list):
                logger.info(f"Data is list with {len(data)} items")
                if data:
                    logger.info(f"First item type: {type(data[0])}")
                    logger.info(f"First item: {data[0]}")
                    if len(data) > 1:
                        logger.info(f"Second item: {data[1]}")
                return {
                    'top_topics': data,
                    'rising_topics': [],
                    'total_top': len(data),
                    'total_rising': 0
                }
            
            else:
                logger.warning(f"Unexpected data type: {type(data)}")
                logger.warning(f"Data repr: {repr(data)}")
                return {
                    'top_topics': [],
                    'rising_topics': [],
                    'total_top': 0,
                    'total_rising': 0
                }
                
        except Exception as e:
            logger.error(f"Error processing related topics for {disease_name}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'top_topics': [],
                'rising_topics': [],
                'total_top': 0,
                'total_rising': 0,
                'error': str(e)
            }
        finally:
            logger.info(f"=== END DEBUG: Related topics for {disease_name} ===")

    def _map_numeric_region_to_name(self, region_code: str, geo: str = 'GH') -> str:
        """
        Map numeric region codes to actual region names
        
        Args:
            region_code: Numeric region code from Google Trends
            geo: Geographic location code (default: GH for Ghana)
            
        Returns:
            Actual region name or the original code if mapping not found
        """
        # Ghana region mappings based on common Google Trends numeric codes
        if geo == 'GH':
            ghana_regions = {
                # Major regions with their numeric codes
                '100': 'Greater Accra',
                '42': 'Ashanti',
                '95': 'Western',
                '98': 'Central',
                '70': 'Eastern',
                '41': 'Volta',
                '58': 'Northern',
                '39': 'Upper East',
                '51': 'Upper West',
                '82': 'Bono',
                '83': 'Ahafo',
                '84': 'Bono East',
                '85': 'Savannah',
                '86': 'North East',
                '87': 'Oti',
                '88': 'Western North',
                
                # Additional codes that appear in our data
                '91': 'Western North',  # Alternative code for Western North
                '69': 'Eastern',        # Alternative code for Eastern
                '57': 'Northern',       # Alternative code for Northern
                '55': 'Northern',       # Alternative code for Northern
                '38': 'Upper East',     # Alternative code for Upper East
                '21': 'Upper West',     # Alternative code for Upper West
                '47': 'Volta',          # Alternative code for Volta
                '34': 'Upper East',     # Alternative code for Upper East
                '94': 'Western',        # Alternative code for Western
                '36': 'Central',        # Alternative code for Central
                '97': 'Central',        # Alternative code for Central
                '0': 'Unknown Region',  # Special case for zero values
                
                # Additional mappings based on common patterns
                '52': 'Ashanti',        # Likely Ashanti region
                '81': 'Bono',           # Likely Bono region
                '50': 'Upper West',     # Likely Upper West region
                
                # Additional codes from the data
                '62': 'Greater Accra',  # From your data
                '43': 'Central',        # Likely Central region
                '59': 'Northern',       # Likely Northern region
                '56': 'Northern',       # Likely Northern region
                '84': 'Bono East',      # Bono East region
                '100': 'Greater Accra', # Greater Accra region
                '21': 'Upper West',     # Upper West region
                '39': 'Upper East',     # Upper East region
                '98': 'Central',        # Central region
                '0': 'Unknown Region',  # Special case for zero values
            }
            
            # Return mapped name or a descriptive fallback
            if region_code in ghana_regions:
                return ghana_regions[region_code]
            elif region_code == '0':
                return 'Unknown Region'
            else:
                # For unmapped codes, try to make an educated guess based on common patterns
                try:
                    code_num = int(region_code)
                    if code_num >= 80 and code_num <= 89:
                        return 'Bono Region'  # Likely Bono-related
                    elif code_num >= 90 and code_num <= 99:
                        return 'Western Region'  # Likely Western-related
                    elif code_num >= 40 and code_num <= 49:
                        return 'Central/Volta Region'  # Likely Central or Volta
                    elif code_num >= 50 and code_num <= 59:
                        return 'Northern Region'  # Likely Northern
                    elif code_num >= 60 and code_num <= 69:
                        return 'Eastern Region'  # Likely Eastern
                    elif code_num >= 70 and code_num <= 79:
                        return 'Eastern Region'  # Likely Eastern
                    else:
                        return f"Region {region_code} (Ghana)"
                except ValueError:
                    return f"Region {region_code} (Ghana)"
        
        # For other countries, return the original code
        return region_code

    def _process_interest_by_region(self, data: Any, disease_name: str) -> Dict[str, Any]:
        """
        Process interest by region data from Google Trends
        
        Args:
            data: Raw data from Google Trends
            disease_name: Name of the disease
            
        Returns:
            Dictionary with processed interest by region data
        """
        logger.info(f"=== DEBUG: Processing interest by region for {disease_name} ===")
        logger.info(f"Raw data type: {type(data)}")
        
        try:
            # Handle different data types
            if isinstance(data, dict):
                logger.info(f"Raw data: {data}")
                
                # Check if data has the expected structure
                if disease_name in data and isinstance(data[disease_name], pd.DataFrame):
                    df_data = data[disease_name]
                    logger.info(f"Data is dict with DataFrame for {disease_name}")
                else:
                    logger.warning(f"Unexpected data structure for {disease_name}: {data}")
                    return {
                        'top_regions': [],
                        'regional_distribution': {}
                    }
            elif isinstance(data, pd.DataFrame):
                df_data = data
                logger.info(f"Data is DataFrame with shape: {df_data.shape}")
            else:
                logger.warning(f"Unexpected data type: {type(data)}")
                return {
                    'top_regions': [],
                    'regional_distribution': {}
                }
            
            if hasattr(df_data, 'empty') and df_data.empty:
                logger.warning(f"Empty DataFrame for {disease_name} interest by region")
                return {
                    'top_regions': [],
                    'regional_distribution': {}
                }
            
            # Log the actual structure for debugging
            logger.info(f"Interest by region DataFrame columns: {list(df_data.columns) if hasattr(df_data, 'columns') else 'No columns'}")
            logger.info(f"Interest by region DataFrame shape: {df_data.shape if hasattr(df_data, 'shape') else 'No shape'}")
            
            # Get top regions and regional distribution
            top_regions = []
            regional_distribution = {}
            
            # Try different possible column names for region names
            region_columns = ['geoName', 'region', 'location', 'geo', 'country', 'state']
            region_col = None
            for col in region_columns:
                if col in df_data.columns:
                    region_col = col
                    break
            
            # Try different possible column names for interest values
            interest_columns = [disease_name, 'interest', 'value', 'score', 'count']
            interest_col = None
            for col in interest_columns:
                if col in df_data.columns:
                    interest_col = col
                    break
            
            if region_col and interest_col:
                # Sort by interest value and get top regions
                top_df = df_data.nlargest(10, interest_col)
                top_regions = []
                
                for _, row in top_df.iterrows():
                    region_code = str(row[region_col])
                    interest = float(row[interest_col])
                    
                    if pd.notna(region_code) and pd.notna(interest):
                        # Check if it's a numeric region code
                        if region_code.isdigit():
                            region_name = self._map_numeric_region_to_name(region_code)
                            region_note = f"Originally: {region_code}"
                        else:
                            region_name = region_code
                            region_note = None
                        
                        top_regions.append({
                            'region': region_name,
                            'interest': interest,
                            'region_note': region_note
                        })
                        
                        regional_distribution[region_name] = interest
                
                logger.info(f"Found numeric region codes for {disease_name}, attempting to map to region names")
                logger.info(f"Final result - top_regions: {len(top_regions)}, regional_distribution: {len(regional_distribution)}")
            
            # If we still don't have data, try to extract from any available columns
            if not top_regions and len(df_data.columns) > 0:
                logger.info("No data found with standard columns, trying column-based extraction")
                # Try to use first two columns as region and interest
                col1, col2 = df_data.columns[0], df_data.columns[1] if len(df_data.columns) > 1 else df_data.columns[0]
                logger.info(f"Using columns: {col1} and {col2}")
                
                for _, row in df_data.head(10).iterrows():
                    try:
                        region_code = str(row[col1])
                        interest = float(row[col2]) if col2 != col1 else 1.0
                        
                        if region_code and region_code != 'nan':
                            # Check if it's a numeric region code
                            if region_code.isdigit():
                                region_name = self._map_numeric_region_to_name(region_code)
                                region_note = f"Originally: {region_code}"
                            else:
                                region_name = region_code
                                region_note = None
                            
                            top_regions.append({
                                'region': region_name,
                                'interest': interest,
                                'region_note': region_note
                            })
                            regional_distribution[region_name] = interest
                            
                            logger.info(f"Added region: {region_name} with interest: {interest}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to process row {row}: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"Error processing interest by region for {disease_name}: {e}")
            return {
                'top_regions': [],
                'regional_distribution': {},
                'error': str(e)
            }
        finally:
            logger.info(f"=== END DEBUG: Interest by region for {disease_name} ===")
        
        return {
            'top_regions': top_regions,
            'regional_distribution': regional_distribution
        }

    def _validate_timeframe(self, timeframe: str) -> Tuple[bool, str]:
        """
        Validate if a timeframe is supported by Google Trends
        
        Args:
            timeframe: Timeframe string to validate
            
        Returns:
            Tuple of (is_valid, error_message_or_suggested_timeframe)
        """
        # Valid Google Trends timeframes
        valid_timeframes = {
            # Short-term (most reliable)
            'now 1-H': 'Last hour',
            'now 4-H': 'Last 4 hours', 
            'now 1-d': 'Last 24 hours',
            'now 7-d': 'Last 7 days',
            
            # Medium-term (reliable)
            'today 1-m': 'Last month',
            'today 3-m': 'Last 3 months',
            'today 6-m': 'Last 6 months',
            'today 12-m': 'Last 12 months',
            
            # Long-term (less reliable for some data types)
            'today 5-y': 'Last 5 years',
            'today 10-y': 'Last 10 years',
            'today 15-y': 'Last 15 years',
            'today 20-y': 'Last 20 years',
            'today 25-y': 'Last 25 years',
            'today 30-y': 'Last 30 years',
            'today 35-y': 'Last 35 years',
            'today 40-y': 'Last 40 years',
            'today 45-y': 'Last 45 years',
            'today 50-y': 'Last 50 years'
        }
        
        if timeframe in valid_timeframes:
            return True, "valid"
        
        # Check for custom date ranges (YYYY-MM-DD YYYY-MM-DD format)
        if ' ' in timeframe and len(timeframe.split(' ')) == 2:
            try:
                from datetime import datetime
                start_date = datetime.strptime(timeframe.split(' ')[0], '%Y-%m-%d')
                end_date = datetime.strptime(timeframe.split(' ')[1], '%Y-%m-%d')
                
                # Check if date range is reasonable (not too short, not too long)
                date_diff = (end_date - start_date).days
                if 1 <= date_diff <= 365:
                    return True, "valid"
                else:
                    return False, f"Date range too {'short' if date_diff < 1 else 'long'} ({date_diff} days). Use 1-365 days."
            except:
                pass
        
        # Suggest alternatives
        if timeframe.startswith('now 30-d'):
            return False, "Invalid timeframe. Use 'today 1-m' for last 30 days or 'today 3-m' for better data quality."
        elif timeframe.startswith('now'):
            return False, "Invalid 'now' timeframe. Use 'today' timeframes for periods longer than 7 days."
        
        return False, f"Invalid timeframe. Valid options: {', '.join(list(valid_timeframes.keys())[:5])}..."

    def _get_timeframe_description(self, timeframe: str) -> str:
        """
        Get human-readable description of timeframe
        
        Args:
            timeframe: Google Trends timeframe string
            
        Returns:
            Human-readable description
        """
        timeframe_map = {
            # Short-term (most reliable)
            'now 1-H': 'Last hour',
            'now 4-H': 'Last 4 hours', 
            'now 1-d': 'Last 24 hours',
            'now 7-d': 'Last 7 days',
            
            # Medium-term (reliable)
            'today 1-m': 'Last month',
            'today 3-m': 'Last 3 months',
            'today 6-m': 'Last 6 months',
            'today 12-m': 'Last 12 months',
            
            # Long-term (less reliable for some data types)
            'today 5-y': 'Last 5 years',
            'today 10-y': 'Last 10 years',
            'today 15-y': 'Last 15 years',
            'today 20-y': 'Last 20 years',
            'today 25-y': 'Last 25 years',
            'today 30-y': 'Last 30 years',
            'today 35-y': 'Last 35 years',
            'today 40-y': 'Last 40 years',
            'today 45-y': 'Last 45 years',
            'today 50-y': 'Last 50 years'
        }
        
        # Check for custom date ranges (YYYY-MM-DD YYYY-MM-DD format)
        if ' ' in timeframe and len(timeframe.split(' ')) == 2:
            try:
                from datetime import datetime
                start_date = datetime.strptime(timeframe.split(' ')[0], '%Y-%m-%d')
                end_date = datetime.strptime(timeframe.split(' ')[1], '%Y-%m-%d')
                return f"From {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
            except:
                pass
        
        return timeframe_map.get(timeframe, f"Custom timeframe: {timeframe}")

    def _suggest_alternative_timeframe(self, requested_timeframe: str) -> str:
        """
        Suggest an alternative timeframe when the requested one is invalid
        
        Args:
            requested_timeframe: The invalid timeframe that was requested
            
        Returns:
            Suggested alternative timeframe
        """
        # Map invalid timeframes to valid alternatives
        alternatives = {
            'now 30-d': 'today 1-m',  # Last 30 days -> Last month
            'now 14-d': 'today 1-m',  # Last 14 days -> Last month
            'now 10-d': 'now 7-d',    # Last 10 days -> Last 7 days
            'now 5-d': 'now 7-d',     # Last 5 days -> Last 7 days
            'now 2-d': 'now 7-d',     # Last 2 days -> Last 7 days
        }
        
        # Check for patterns
        for invalid, alternative in alternatives.items():
            if requested_timeframe == invalid:
                return alternative
        
        # Default suggestions based on pattern
        if requested_timeframe.startswith('now') and 'd' in requested_timeframe:
            return 'today 1-m'  # Any "now X-d" -> today 1-m
        elif requested_timeframe.startswith('now') and 'H' in requested_timeframe:
            return 'now 7-d'    # Any "now X-H" -> now 7-d
        
        # Default fallback
        return 'today 1-m'

    def _convert_to_valid_timeframe(self, requested_timeframe: str) -> str:
        """
        Convert an invalid timeframe to a valid one automatically
        
        Args:
            requested_timeframe: The timeframe that might be invalid
            
        Returns:
            Valid timeframe string
        """
        # First validate
        is_valid, _ = self._validate_timeframe(requested_timeframe)
        if is_valid:
            return requested_timeframe
        
        # Convert invalid timeframes to valid ones
        conversions = {
            'now 30-d': 'today 1-m',  # Last 30 days -> Last month
            'now 14-d': 'today 1-m',  # Last 14 days -> Last month
            'now 10-d': 'now 7-d',    # Last 10 days -> Last 7 days
            'now 5-d': 'now 7-d',     # Last 5 days -> Last 7 days
            'now 2-d': 'now 7-d',     # Last 2 days -> Last 7 days
        }
        
        return conversions.get(requested_timeframe, 'today 1-m')

    def get_trends_data(self, disease_name: str, time_range: str = 'now 7-d', 
                        geo: str = 'GH', data_types: List[str] = None) -> Dict[str, Any]:
        """
        Get Google Trends data for a disease with intelligent caching
        
        Args:
            disease_name: Name of the disease
            time_range: Timeframe for the data
            geo: Geographic location (default: GH for Ghana)
            data_types: List of data types to fetch
            
        Returns:
            Dictionary containing the requested data
        """
        if disease_name.lower() not in [d.lower() for d in self.SUPPORTED_DISEASES]:
            return {
                'error': f'Unsupported disease: {disease_name}. Supported: {", ".join(self.SUPPORTED_DISEASES)}'
            }
        
        # Validate timeframe and convert if invalid
        is_valid, timeframe_message = self._validate_timeframe(time_range)
        if not is_valid:
            # Convert to valid timeframe automatically
            original_timeframe = time_range
            time_range = self._convert_to_valid_timeframe(time_range)
            logger.warning(f"Invalid timeframe '{original_timeframe}' converted to '{time_range}'. {timeframe_message}")
        
        if data_types is None:
            data_types = ['interest_over_time']
        
        # Validate data types
        invalid_types = [dt for dt in data_types if dt not in self.DATA_TYPES]
        if invalid_types:
            return {
                'error': f'Invalid data types: {invalid_types}. Valid: {", ".join(self.DATA_TYPES)}'
            }
        
        result = {
            'disease_name': disease_name,
            'timeframe': time_range,
            'timeframe_description': self._get_timeframe_description(time_range),
            'geo': geo,
            'data_source': 'google_trends',
            'cache_status': 'unknown',
            'last_updated': None
        }
        
        # Add timeframe conversion info if it happened
        if 'original_timeframe' in locals():
            result['original_timeframe'] = original_timeframe
            result['timeframe_converted'] = True
            result['conversion_note'] = f"'{original_timeframe}' was converted to '{time_range}' for better data quality"
        
        # Check cache status for all data types first
        cache_status = {}
        needs_fetch = False
        
        for data_type in data_types:
            cache_key = self._generate_cache_key(disease_name, data_type, time_range, geo)
            from disease_monitor.models import GoogleTrendsCache
            cache_obj = GoogleTrendsCache.objects.filter(cache_key=cache_key).first()
            
            if cache_obj:
                cache_obj.mark_accessed()
                cache_obj.update_status()
                cache_status[data_type] = cache_obj
                
                # Check if we need to fetch fresh data
                if self._should_fetch_from_google(cache_obj):
                    needs_fetch = True
            else:
                needs_fetch = True
        
        # If we need fresh data, make a single Google API call and build payload once
        if needs_fetch:
            # Respect rate limit only once for all data types
            self._respect_rate_limit()
            
            # Build payload once for all data types
            if self.pytrends:
                try:
                    self.pytrends.build_payload(
                        kw_list=[disease_name],
                        timeframe=time_range,
                        geo=geo
                    )
                    
                    # Fetch all data types in sequence without additional rate limiting
                    for i, data_type in enumerate(data_types):
                        cache_key = self._generate_cache_key(disease_name, data_type, time_range, geo)
                        cache_obj = cache_status.get(data_type)
                        
                        # Add a small delay between data type fetches (except for the first one)
                        if i > 0:
                            logger.info(f"Adding 2-second delay between data types ({data_types[i-1]} -> {data_type})")
                            time.sleep(2)  # 2 second delay between data types
                        
                        # Fetch data from Google
                        success, data, error = self._fetch_from_google_single(disease_name, data_type, time_range, geo)
                        
                        if success:
                            # Process the data with better error handling
                            try:
                                logger.info(f"=== DEBUG: Processing {data_type} for {disease_name} ===")
                                logger.info(f"Raw data type: {type(data)}")
                                logger.info(f"Raw data: {data}")
                                
                                if data_type == 'interest_over_time':
                                    processed_data = self._process_interest_over_time(data, disease_name)
                                elif data_type == 'related_queries':
                                    processed_data = self._process_related_queries(data, disease_name)
                                elif data_type == 'related_topics':
                                    processed_data = self._process_related_topics(data, disease_name)
                                elif data_type == 'interest_by_region':
                                    processed_data = self._process_interest_by_region(data, disease_name)
                                else:
                                    processed_data = {}
                                
                                logger.info(f"Processed data for {data_type}: {processed_data}")
                                
                                # Validate processed data
                                if not processed_data or (isinstance(processed_data, dict) and 'error' in processed_data):
                                    logger.warning(f"Processing failed for {disease_name} - {data_type}: {processed_data}")
                                    processed_data = {'error': 'Data processing failed'}
                                    
                            except Exception as process_error:
                                logger.error(f"Error processing {data_type} for {disease_name}: {process_error}")
                                logger.error(f"Process error type: {type(process_error).__name__}")
                                import traceback
                                logger.error(f"Process error traceback: {traceback.format_exc()}")
                                processed_data = {'error': f'Processing error: {str(process_error)}'}
                            
                            logger.info(f"=== END DEBUG: Processing {data_type} for {disease_name} ===")
                            
                            # Cache the data
                            from datetime import timedelta
                            cache_expiry = timezone.now() + timedelta(hours=self.CACHE_EXPIRY_HOURS)
                            
                            if cache_obj:
                                # Update existing cache
                                cache_obj.cached_data = processed_data
                                cache_obj.last_fetched = timezone.now()
                                cache_obj.cache_expiry = cache_expiry
                                cache_obj.fetch_count += 1
                                cache_obj.status = 'fresh'
                                cache_obj.last_error = None
                                cache_obj.retry_count = 0
                                cache_obj.save()
                            else:
                                # Create new cache entry
                                from disease_monitor.models import GoogleTrendsCache
                                GoogleTrendsCache.objects.create(
                                    cache_key=cache_key,
                                    disease_name=disease_name,
                                    data_type=data_type,
                                    timeframe=time_range,
                                    geo=geo,
                                    cached_data=processed_data,
                                    cache_expiry=cache_expiry,
                                    status='fresh'
                                )
                            
                            result[data_type] = processed_data
                            result['cache_status'] = 'fresh'
                            result['last_updated'] = timezone.now()
                            
                        else:
                            # Use cached data if available, otherwise return error
                            if cache_obj and cache_obj.cached_data:
                                result[data_type] = cache_obj.cached_data
                                result['cache_status'] = 'stale_cached'
                                result['last_updated'] = cache_obj.last_fetched
                                
                                # Log the error for debugging
                                cache_obj.last_error = error
                                cache_obj.retry_count += 1
                                cache_obj.save()
                            else:
                                result[data_type] = {'error': error}
                                result['cache_status'] = 'error'
                except Exception as e:
                    # Handle any errors during payload building or data fetching
                    logger.error(f"Error fetching data for {disease_name}: {e}")
                    for data_type in data_types:
                        result[data_type] = {'error': f'Failed to fetch data: {str(e)}'}
                        result['cache_status'] = 'error'
            else:
                # Service not initialized
                for data_type in data_types:
                    result[data_type] = {'error': 'Google Trends service not initialized'}
                    result['cache_status'] = 'error'
        else:
            # Use cached data for all types
            for data_type in data_types:
                cache_obj = cache_status.get(data_type)
                if cache_obj and cache_obj.cached_data:
                    result[data_type] = cache_obj.cached_data
                    result['cache_status'] = cache_obj.status
                    result['last_updated'] = cache_obj.last_fetched
                else:
                    result[data_type] = {'error': 'No cached data available'}
                    result['cache_status'] = 'no_cache'
        
        return result

    def get_disease_summary(self, disease_name: str, time_range: str = 'now 7-d', 
                           geo: str = 'GH') -> Dict[str, Any]:
        """
        Get a comprehensive summary of Google Trends data for a disease
        
        Args:
            disease_name: Name of the disease
            time_range: Timeframe for the data
            geo: Geographic location
            
        Returns:
            Dictionary containing summary data
        """
        # Get ALL data types in one call to minimize API requests
        all_data = self.get_trends_data(
            disease_name, time_range, geo, ['interest_over_time', 'related_queries', 'related_topics', 'interest_by_region']
        )
        
        if 'error' in all_data:
            return all_data
        
        interest_data = all_data.get('interest_over_time', {})
        
        if not interest_data:
            return {
                'error': 'No interest data available',
                'disease_name': disease_name
            }
        
        # Build summary from the single batch fetch
        summary = {
            'disease_name': disease_name,
            'timeframe': time_range,
            'timeframe_description': self._get_timeframe_description(time_range),
            'geo': geo,
            'current_interest': interest_data.get('current_interest', 0),
            'trend_direction': interest_data.get('trend_direction', 'stable'),
            'trend_strength': interest_data.get('trend_strength', 0),
            'total_searches': interest_data.get('total_searches', 0),
            'peak_interest': interest_data.get('peak_interest', 0),
            'average_interest': interest_data.get('average_interest', 0),
            'top_related_queries': all_data.get('related_queries', {}).get('top_queries', []),
            'top_related_topics': all_data.get('related_topics', {}).get('top_topics', []),
            'top_regions': all_data.get('interest_by_region', {}).get('top_regions', []),
            'last_updated': all_data.get('last_updated'),
            'cache_status': all_data.get('cache_status'),
            'data_source': 'google_trends'
        }
        
        # Add timeframe conversion info if it exists
        if 'original_timeframe' in all_data:
            summary['original_timeframe'] = all_data['original_timeframe']
            summary['timeframe_converted'] = all_data['timeframe_converted']
            summary['conversion_note'] = all_data['conversion_note']
        
        return summary
    
    def get_all_diseases_summary(self, time_range: str = 'now 7-d', 
                                geo: str = 'GH') -> Dict[str, Any]:
        """
        Get summary data for all supported diseases with retry logic and rate limiting
        
        Args:
            time_range: Timeframe for the data
            geo: Geographic location
            
        Returns:
            Dictionary containing summaries for all diseases
        """
        summaries = {}
        
        for disease in self.SUPPORTED_DISEASES:
            success = False
            attempt = 0
            
            while not success and attempt < self.MAX_RETRIES:
                try:
                    if attempt > 0:
                        # Use exponential backoff for retries
                        self._handle_rate_limit_error(attempt - 1)
                    
                    summary = self.get_disease_summary(disease, time_range, geo)
                    summaries[disease] = summary
                    success = True
                    
                    # Add delay between diseases to respect rate limits
                    if disease != self.SUPPORTED_DISEASES[-1]:  # Don't delay after the last disease
                        self._respect_rate_limit()
                        
                except Exception as e:
                    attempt += 1
                    if attempt >= self.MAX_RETRIES:
                        logger.error(f"Failed to get summary for {disease} after {self.MAX_RETRIES} attempts: {e}")
                        summaries[disease] = {
                            'error': f"Failed after {self.MAX_RETRIES} attempts: {str(e)}",
                            'disease_name': disease
                        }
                    else:
                        logger.warning(f"Attempt {attempt} failed for {disease}: {e}, retrying...")
        
        result = {
            'timeframe': time_range,
            'timeframe_description': self._get_timeframe_description(time_range),
            'geo': geo,
            'diseases': summaries,
            'total_diseases': len(self.SUPPORTED_DISEASES),
            'last_updated': timezone.now()
        }
        
        # Add timeframe conversion info if any disease had conversion
        if any('timeframe_converted' in summary for summary in summaries.values()):
            result['timeframe_converted'] = True
            result['conversion_note'] = "Some timeframes were automatically converted for better data quality"
        
        return result
    
    def clear_cache(self, disease_name: str = None, data_type: str = None) -> Dict[str, Any]:
        """
        Clear cached data
        
        Args:
            disease_name: Specific disease to clear cache for (None for all)
            data_type: Specific data type to clear cache for (None for all)
            
        Returns:
            Dictionary with cache clearing results
        """
        try:
            from disease_monitor.models import GoogleTrendsCache
            
            if disease_name and data_type:
                # Clear specific cache entry
                deleted_count = GoogleTrendsCache.objects.filter(
                    disease_name=disease_name,
                    data_type=data_type
                ).delete()[0]
                message = f"Cleared {deleted_count} cache entries for {disease_name} - {data_type}"
            elif disease_name:
                # Clear all cache for a specific disease
                deleted_count = GoogleTrendsCache.objects.filter(
                    disease_name=disease_name
                ).delete()[0]
                message = f"Cleared {deleted_count} cache entries for {disease_name}"
            elif data_type:
                # Clear all cache for a specific data type
                deleted_count = GoogleTrendsCache.objects.filter(
                    data_type=data_type
                ).delete()[0]
                message = f"Cleared {deleted_count} cache entries for {data_type}"
            else:
                # Clear all cache
                deleted_count = GoogleTrendsCache.objects.all().delete()[0]
                message = f"Cleared all {deleted_count} cache entries"
            
            logger.info(f"Cache cleared: {message}")
            return {
                'success': True,
                'message': message,
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            error_msg = f"Failed to clear cache: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def clear_all_cache(self) -> Dict[str, Any]:
        """
        Clear all cached data (convenience method)
        
        Returns:
            Dictionary with cache clearing results
        """
        return self.clear_cache()
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get status of all cache entries"""
        try:
            from disease_monitor.models import GoogleTrendsCache
            total_entries = GoogleTrendsCache.objects.count()
            fresh_entries = GoogleTrendsCache.objects.filter(status='fresh').count()
            stale_entries = GoogleTrendsCache.objects.filter(status='stale').count()
            expired_entries = GoogleTrendsCache.objects.filter(status='expired').count()
            
            # Get cache by disease
            disease_stats = {}
            for disease in self.SUPPORTED_DISEASES:
                disease_stats[disease] = {
                    'total': GoogleTrendsCache.objects.filter(disease_name=disease).count(),
                    'fresh': GoogleTrendsCache.objects.filter(disease_name=disease, status='fresh').count(),
                    'stale': GoogleTrendsCache.objects.filter(disease_name=disease, status='stale').count(),
                    'expired': GoogleTrendsCache.objects.filter(disease_name=disease, status='expired').count(),
                }
            
            return {
                'total_entries': total_entries,
                'fresh_entries': fresh_entries,
                'stale_entries': stale_entries,
                'expired_entries': expired_entries,
                'disease_stats': disease_stats,
                'last_updated': timezone.now()
            }
        except Exception as e:
            logger.error(f"Error getting cache status: {e}")
            return {
                'error': str(e)
            }
    
    def get_optimal_timeframe_for_data_type(self, data_type: str) -> str:
        """
        Get the optimal timeframe for a specific data type
        
        Args:
            data_type: Type of data to fetch
            
        Returns:
            Optimal timeframe string
        """
        timeframe_recommendations = {
            'interest_over_time': 'now 7-d',  # Good for recent trends
            'related_queries': 'today 3-m',   # Better for related data
            'related_topics': 'today 3-m',    # Better for related data
            'interest_by_region': 'today 6-m' # Better for regional data
        }
        
        return timeframe_recommendations.get(data_type, 'today 3-m')
    
    def get_trends_data_with_fallback(self, disease_name: str, time_range: str = 'now 7-d', 
                                     geo: str = 'GH', data_types: List[str] = None) -> Dict[str, Any]:
        """
        Get Google Trends data with fallback to optimal timeframes for better data
        
        Args:
            disease_name: Name of the disease
            time_range: Preferred timeframe for the data
            geo: Geographic location
            data_types: List of data types to fetch
            
        Returns:
            Dictionary containing the requested data with fallback information
        """
        if data_types is None:
            data_types = ['interest_over_time']
        
        result = {
            'disease_name': disease_name,
            'preferred_timeframe': time_range,
            'geo': geo,
            'data_source': 'google_trends',
            'fallback_used': {},
            'data': {}
        }
        
        for data_type in data_types:
            # Try preferred timeframe first
            data = self.get_trends_data(disease_name, time_range, geo, [data_type])
            
            if data_type in data and not data[data_type].get('error'):
                # Check if we got meaningful data
                if data_type in ['related_queries', 'related_topics', 'interest_by_region']:
                    data_content = data[data_type]
                    has_content = (
                        (data_type == 'related_queries' and (data_content.get('top_queries') or data_content.get('top_rising'))) or
                        (data_type == 'related_topics' and (data_content.get('top_topics') or data_content.get('top_rising'))) or
                        (data_type == 'interest_by_region' and (data_content.get('top_regions') or data_content.get('regional_distribution')))
                    )
                    
                    if not has_content:
                        # Try fallback timeframe
                        fallback_timeframe = self.get_optimal_timeframe_for_data_type(data_type)
                        logger.info(f"Trying fallback timeframe {fallback_timeframe} for {data_type}")
                        
                        fallback_data = self.get_trends_data(disease_name, fallback_timeframe, geo, [data_type])
                        if data_type in fallback_data and not fallback_data[data_type].get('error'):
                            result['data'][data_type] = fallback_data[data_type]
                            result['fallback_used'][data_type] = fallback_timeframe
                        else:
                            result['data'][data_type] = data[data_type]
                            result['fallback_used'][data_type] = None
                    else:
                        result['data'][data_type] = data[data_type]
                        result['fallback_used'][data_type] = None
                else:
                    result['data'][data_type] = data[data_type]
                    result['fallback_used'][data_type] = None
            else:
                # Try fallback timeframe if preferred failed
                fallback_timeframe = self.get_optimal_timeframe_for_data_type(data_type)
                logger.info(f"Preferred timeframe failed, trying fallback {fallback_timeframe} for {data_type}")
                
                fallback_data = self.get_trends_data(disease_name, fallback_timeframe, geo, [data_type])
                if data_type in fallback_data and not fallback_data[data_type].get('error'):
                    result['data'][data_type] = fallback_data[data_type]
                    result['fallback_used'][data_type] = fallback_timeframe
                else:
                    result['data'][data_type] = data.get(data_type, {'error': 'Failed to fetch data'})
                    result['fallback_used'][data_type] = None
        
        return result
    
    def get_disease_summary_with_fallback(self, disease_name: str, time_range: str = 'now 7-d', 
                                        geo: str = 'GH') -> Dict[str, Any]:
        """
        Get a comprehensive summary with fallback timeframes for better data
        
        Args:
            disease_name: Name of the disease
            time_range: Preferred timeframe for the data
            geo: Geographic location
            
        Returns:
            Dictionary containing summary data with fallback information
        """
        # Get data with fallback timeframes
        all_data = self.get_trends_data_with_fallback(
            disease_name, time_range, geo, 
            ['interest_over_time', 'related_queries', 'related_topics', 'interest_by_region']
        )
        
        if 'error' in all_data:
            return all_data
        
        interest_data = all_data['data'].get('interest_over_time', {})
        
        if not interest_data:
            return {
                'error': 'No interest data available',
                'disease_name': disease_name
            }
        
        # Build summary from the data with fallback information
        summary = {
            'disease_name': disease_name,
            'preferred_timeframe': time_range,
            'geo': geo,
            'current_interest': interest_data.get('current_interest', 0),
            'trend_direction': interest_data.get('trend_direction', 'stable'),
            'trend_strength': interest_data.get('trend_strength', 0),
            'total_searches': interest_data.get('total_searches', 0),
            'peak_interest': interest_data.get('peak_interest', 0),
            'average_interest': interest_data.get('average_interest', 0),
            'top_related_queries': all_data['data'].get('related_queries', {}).get('top_queries', []),
            'top_related_topics': all_data['data'].get('related_topics', {}).get('top_topics', []),
            'top_regions': all_data['data'].get('interest_by_region', {}).get('top_regions', []),
            'fallback_timeframes_used': all_data['fallback_used'],
            'data_source': 'google_trends'
        }
        
        return summary 
    
    def get_all_diseases_summary_with_fallback(self, time_range: str = 'now 7-d', 
                                             geo: str = 'GH') -> Dict[str, Any]:
        """
        Get summary data for all supported diseases with fallback timeframes for better data
        
        Args:
            time_range: Preferred timeframe for the data
            geo: Geographic location
            
        Returns:
            Dictionary containing summaries for all diseases with fallback information
        """
        summaries = {}
        
        for disease in self.SUPPORTED_DISEASES:
            try:
                summary = self.get_disease_summary_with_fallback(disease, time_range, geo)
                summaries[disease] = summary
            except Exception as e:
                logger.error(f"Error getting summary for {disease}: {e}")
                summaries[disease] = {
                    'error': str(e),
                    'disease_name': disease
                }
        
        return {
            'preferred_timeframe': time_range,
            'geo': geo,
            'diseases': summaries,
            'total_diseases': len(self.SUPPORTED_DISEASES),
            'fallback_recommendation': 'Use longer timeframes (3-6 months) for better related queries, topics, and regional data',
            'last_updated': timezone.now()
        } 