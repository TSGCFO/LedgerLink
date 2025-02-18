from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.utils import timezone
from .utils import get_client_ip
import jwt
import logging

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that extends the default JWT authentication
    with additional features like token blacklisting and device tracking.
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, token).
        """
        try:
            # Get the raw token from the request
            raw_token = self.get_raw_token(request)
            if raw_token is None:
                return None

            # Validate the token
            validated_token = self.get_validated_token(raw_token)

            # Get the user from the validated token
            user = self.get_user(validated_token)

            # Check if token is blacklisted
            if self.is_token_blacklisted(validated_token):
                raise AuthenticationFailed('Token is blacklisted')

            # Track the authentication
            self.track_authentication(request, user, validated_token)

            return user, validated_token

        except InvalidToken as e:
            logger.warning(
                'Invalid token authentication attempt',
                extra={
                    'token_error': str(e),
                    'ip_address': get_client_ip(request),
                }
            )
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            logger.error(
                'Authentication error',
                exc_info=True,
                extra={
                    'ip_address': get_client_ip(request),
                }
            )
            raise

    def is_token_blacklisted(self, validated_token):
        """
        Check if the token has been blacklisted.
        """
        from django.core.cache import cache
        jti = validated_token.get('jti')
        return cache.get(f'blacklisted_token_{jti}') is not None

    def track_authentication(self, request, user, token):
        """
        Track authentication attempts and user sessions.
        """
        from django.contrib.auth.signals import user_logged_in
        user_logged_in.send(
            sender=user.__class__,
            request=request,
            user=user
        )

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for API key based authentication.
    Useful for service-to-service communication.
    """

    def authenticate(self, request):
        """
        Authenticate the request using API key.
        """
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None

        try:
            if not self.is_valid_api_key(api_key):
                raise AuthenticationFailed('Invalid API key')

            user = self.get_api_key_user(api_key)
            return user, None

        except Exception as e:
            logger.error(
                'API key authentication error',
                exc_info=True,
                extra={
                    'ip_address': get_client_ip(request),
                }
            )
            raise

    def is_valid_api_key(self, api_key):
        """
        Validate the API key.
        """
        from django.core.cache import cache
        # Check cache first
        cache_key = f'api_key_{api_key}'
        if cache.get(cache_key):
            return True

        # Check database
        from django.contrib.auth import get_user_model
        User = get_user_model()
        valid = User.objects.filter(api_key=api_key, is_active=True).exists()

        if valid:
            # Cache the result
            cache.set(cache_key, True, timeout=300)  # 5 minutes

        return valid

    def get_api_key_user(self, api_key):
        """
        Get the user associated with the API key.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(api_key=api_key, is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

def create_tokens_for_user(user):
    """
    Create access and refresh tokens for the given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def blacklist_token(token):
    """
    Blacklist a token to prevent its future use.
    """
    try:
        # Decode the token
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        
        # Add to blacklist
        from django.core.cache import cache
        jti = decoded_token.get('jti')
        if jti:
            cache.set(
                f'blacklisted_token_{jti}',
                True,
                timeout=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            )
        
        return True
    except (jwt.InvalidTokenError, TokenError):
        return False

def get_token_user(token):
    """
    Get user from token without validating expiration.
    Useful for handling refresh tokens.
    """
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256'],
            options={'verify_exp': False}
        )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_id = decoded_token.get('user_id')
        
        return User.objects.get(id=user_id)
    except Exception:
        return None