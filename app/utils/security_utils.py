"""
Security utility functions for authentication and login protection.
Provides rate limiting, attempt tracking, and security monitoring.
"""
from datetime import datetime, timedelta
from app import db
from app.models import LoginAttempt

# Configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
ATTEMPT_WINDOW_MINUTES = 15


def log_login_attempt(username, ip_address, success=False, user_agent=None):
    """
    Log a login attempt to the database.
    
    Args:
        username (str): Username attempted
        ip_address (str): IP address of the request
        success (bool): Whether login was successful
        user_agent (str): Browser/device user agent string
    """
    attempt = LoginAttempt(
        username=username,
        ip_address=ip_address,
        success=success,
        user_agent=user_agent
    )
    db.session.add(attempt)
    db.session.commit()


def get_failed_attempts(username, ip_address, minutes=ATTEMPT_WINDOW_MINUTES):
    """
    Get count of failed login attempts within the specified time window.
    
    Args:
        username (str): Username to check
        ip_address (str): IP address to check
        minutes (int): Time window in minutes
        
    Returns:
        int: Number of failed attempts
    """
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    
    # Count failed attempts for this username OR this IP
    count = LoginAttempt.query.filter(
        db.or_(
            LoginAttempt.username == username,
            LoginAttempt.ip_address == ip_address
        ),
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= cutoff_time
    ).count()
    
    return count


def is_account_locked(username, ip_address):
    """
    Check if account/IP is currently locked due to too many failed attempts.
    
    Args:
        username (str): Username to check
        ip_address (str): IP address to check
        
    Returns:
        bool: True if locked, False otherwise
    """
    failed_count = get_failed_attempts(username, ip_address)
    return failed_count >= MAX_LOGIN_ATTEMPTS


def get_lockout_time_remaining(username, ip_address):
    """
    Get the time remaining until account unlock.
    
    Args:
        username (str): Username to check
        ip_address (str): IP address to check
        
    Returns:
        dict: {'minutes': int, 'seconds': int, 'total_seconds': int} or None if not locked
    """
    if not is_account_locked(username, ip_address):
        return None
    
    cutoff_time = datetime.now() - timedelta(minutes=ATTEMPT_WINDOW_MINUTES)
    
    # Get the most recent failed attempt
    last_attempt = LoginAttempt.query.filter(
        db.or_(
            LoginAttempt.username == username,
            LoginAttempt.ip_address == ip_address
        ),
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= cutoff_time
    ).order_by(LoginAttempt.timestamp.desc()).first()
    
    if not last_attempt:
        return None
    
    # Calculate unlock time
    unlock_time = last_attempt.timestamp + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    time_remaining = unlock_time - datetime.now()
    
    if time_remaining.total_seconds() <= 0:
        return None
    
    total_seconds = int(time_remaining.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    return {
        'minutes': minutes,
        'seconds': seconds,
        'total_seconds': total_seconds
    }


def clear_successful_attempts(username):
    """
    Clear failed attempts after a successful login.
    
    Args:
        username (str): Username that successfully logged in
    """
    cutoff_time = datetime.now() - timedelta(minutes=ATTEMPT_WINDOW_MINUTES)
    
    # Delete recent failed attempts for this username
    LoginAttempt.query.filter(
        LoginAttempt.username == username,
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= cutoff_time
    ).delete()
    
    db.session.commit()


def cleanup_old_attempts(days=30):
    """
    Remove login attempt records older than specified days.
    Helps keep database clean.
    
    Args:
        days (int): Remove records older than this many days
        
    Returns:
        int: Number of records deleted
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    deleted = LoginAttempt.query.filter(
        LoginAttempt.timestamp < cutoff_date
    ).delete()
    
    db.session.commit()
    
    return deleted


def get_client_ip(request):
    """
    Get the client's IP address, handling proxies.
    
    Args:
        request: Flask request object
        
    Returns:
        str: Client IP address
    """
    # Check for proxy headers
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, get the first one
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    
    return ip or 'unknown'
