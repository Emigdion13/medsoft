from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    
    Returns:
        dict with 'access' and 'refresh' token strings
    """
    refresh = RefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }
