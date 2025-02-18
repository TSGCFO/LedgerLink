from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Material, BoxPrice
from .serializers import MaterialSerializer, BoxPriceSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]

class BoxPriceViewSet(viewsets.ModelViewSet):
    queryset = BoxPrice.objects.all()
    serializer_class = BoxPriceSerializer
    permission_classes = [IsAuthenticated]
