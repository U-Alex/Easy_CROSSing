from rest_framework.authtoken import views as t_views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class AuthToken(t_views.ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key,
                         'user': [user.id, user.first_name, user.last_name, user.email]})


auth_token = AuthToken.as_view()
