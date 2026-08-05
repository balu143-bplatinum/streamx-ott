# web/middleware.py
from django.shortcuts import redirect
from django.contrib import messages

class SubscriptionPaywallMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Intercept access on video detail views
        if view_func.__name__ == 'video_detail':
            video_id = view_kwargs.get('pk')
            user = request.user
            
            # If user is not logged in or doesn't have an active subscription
            if not user.is_authenticated or not getattr(user, 'profile', None) or not user.profile.has_active_subscription:
                messages.warning(request, "Upgrade to Premium to stream this title.")
                return redirect('subscription_plans')
        return None