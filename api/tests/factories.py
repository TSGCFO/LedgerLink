import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

fake = Faker()

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True
    is_staff = False
    is_superuser = False
    date_joined = factory.LazyFunction(timezone.now)
    
    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for group in extracted:
                self.groups.add(group)