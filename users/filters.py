import django_filters
from django.contrib.auth import get_user_model


User = get_user_model()
class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    class Meta:
        model = User
        fields = ['name']