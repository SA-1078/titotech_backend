# titotech/serializers/user.py
from rest_framework import serializers
from django.contrib.auth.models import User
from titotech.models import CustomerProfile


class RegisterSerializer(serializers.Serializer):
    username  = serializers.CharField(max_length=150)
    email     = serializers.EmailField()
    password  = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Las contraseñas no coinciden.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Crear automáticamente el perfil de cliente al registrarse
        CustomerProfile.objects.create(user=user)
        return user


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomerProfile
        fields = ['id', 'phone_number', 'shipping_address', 'city']


class CustomerProfileAdminSerializer(serializers.ModelSerializer):
    """Serializer extendido para panel admin — incluye datos del usuario."""
    username = serializers.CharField(source='user.username', read_only=True)
    email    = serializers.CharField(source='user.email',    read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    num_orders = serializers.SerializerMethodField()

    class Meta:
        model  = CustomerProfile
        fields = [
            'id', 'username', 'email', 'is_active',
            'phone_number', 'shipping_address', 'city', 'num_orders',
        ]
        read_only_fields = ['id', 'username', 'email', 'is_active']

    def get_num_orders(self, obj):
        return obj.orders.count()


class UserSerializer(serializers.ModelSerializer):
    profile    = CustomerProfileSerializer(read_only=True)
    num_orders = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined', 'num_orders', 'profile',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_num_orders(self, obj):
        try:
            return obj.profile.orders.count()
        except CustomerProfile.DoesNotExist:
            return 0


class UserProfileSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']

    def validate_email(self, value):
        request = self.context.get('request')
        if User.objects.filter(email=value).exclude(pk=request.user.pk).exists():
            raise serializers.ValidationError('Este correo ya está en uso por otro usuario.')
        return value

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        # Actualizar campos del User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Actualizar campos del CustomerProfile
        profile, _ = CustomerProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(min_length=8, write_only=True)
    new_password2    = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Las nuevas contraseñas no coinciden.'})
        return data
