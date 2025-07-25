from rest_framework import serializers
from django.contrib.auth import get_user_model
from .forms import ProfileUpdateForm, PasswordChangeForm
from .forms import UserRegistrationForm

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "username", "gender", "created_at", "updated_at"]
        read_only_fields = ["id", "email", "created_at", "updated_at"]

class ProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=150)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, allow_blank=True, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        form = ProfileUpdateForm(data=data, user=self.user, instance=self.user)
        if not form.is_valid():
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors
            raise serializers.ValidationError(errors)
        return form.cleaned_data

    def save(self):
        form = ProfileUpdateForm(data=self.validated_data, user=self.user, instance=self.user)
        if form.is_valid():
            return form.save()
        return None

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        form = PasswordChangeForm(user=self.user, data=data)
        if not form.is_valid():
            errors = {}
            for field, field_errors in form.errors.items():
                if field == "__all__":
                    errors["non_field_errors"] = field_errors
                else:
                    errors[field] = field_errors
            raise serializers.ValidationError(errors)
        return form.cleaned_data

    def save(self):
        form = PasswordChangeForm(user=self.user, data=self.validated_data)
        if form.is_valid():
            return form.save()
        return None

class UserRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, allow_blank=True, required=False)

    def validate(self, data):
        form = UserRegistrationForm(data=data)
        if not form.is_valid():
            errors = {}
            for field, field_errors in form.errors.items():
                if field == "__all__":
                    errors["non_field_errors"] = field_errors
                else:
                    errors[field] = field_errors
            raise serializers.ValidationError(errors)
        return form.cleaned_data

    # 建立使用者
    def create(self, validated_data):
        form = UserRegistrationForm(data=validated_data)
        if form.is_valid():
            return form.save()
        return None
