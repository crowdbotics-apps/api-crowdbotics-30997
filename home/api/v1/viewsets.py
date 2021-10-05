from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from home.api.v1.serializers import (
    SignupSerializer,
    UserSerializer,
    AppSerializer,
    SubscriptionSerializer,
    PlanSerializer,
)
from home.models import App, Subscription, Plan
from rest_framework.permissions import IsAuthenticated


class SignupViewSet(ModelViewSet):
    serializer_class = SignupSerializer
    http_method_names = ["post"]


class LoginViewSet(ViewSet):
    """Based on rest_framework.authtoken.views.ObtainAuthToken"""

    serializer_class = AuthTokenSerializer

    def create(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        return Response({"token": token.key, "user": user_serializer.data})


class AppViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AppSerializer

    def get_queryset(self):
        return App.objects.filter(user=self.request.user)


class SubscriptionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    http_method_names = ['get', 'post', 'put', 'patch']

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class PlanViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PlanSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return Plan.objects.all()
