from django.contrib.sessions.models import Session
from django.utils import timezone

class OneSessionPerUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Get the current user's sessions
            current_session_key = request.session.session_key
            user_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            
            for session in user_sessions:
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(request.user.id) and session.session_key != current_session_key:
                    session.delete()
                    
        response = self.get_response(request)
        return response
