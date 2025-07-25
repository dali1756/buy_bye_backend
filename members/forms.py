from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "username", "gender"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "請輸入姓名"
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "請輸入用戶名"
            }),
            "gender": forms.Select(attrs={
                "class": "form-control"
            })
        }
        labels = {
            "name": "姓名",
            "username": "用戶名",
            "gender": "性別"
        }
        help_texts = {
            "username": "使用者名稱必需是唯一的",
            "name": "顯示在個人資料中的姓名"
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["username"].required = True
        self.fields["gender"].required = False

    # 驗證用戶名是否已被使用
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            raise ValidationError("使用者名稱不能為空。")
        # 排除當前使用者，檢查是否有其他使用者使用相同名稱
        if self.user:
            existing_users = User.objects.exclude(pk=self.user.pk).filter(username=username)
        else:
            existing_users = User.objects.filter(username=username)
        if existing_users.exists():
            raise ValidationError("該名稱已被使用，請選擇其他名稱。")
        return username

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name or not name.strip():
            raise ValidationError("姓名不能為空。")
        if len(name.strip()) < 2:
            raise ValidationError("姓名至少需要2個字元。")
        if len(name.strip()) > 30:
            raise ValidationError("姓名不能超過30個字元。")
        return name.strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

# 修改密碼
class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="當前密碼",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "請輸入當前密碼"
        }),
        help_text="請輸入您目前使用的密碼"
    )
    new_password = forms.CharField(
        label="新密碼",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "請輸入新密碼"
        }),
        help_text="密碼至少8個字元，包含字母和數字"
    )
    confirm_password = forms.CharField(
        label="確認新密碼",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "請再次輸入新密碼"
        }),
        help_text="請再次輸入新密碼以確認"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    # 驗證當前密碼
    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if not current_password:
            raise ValidationError("請輸入當前密碼。")
        if not self.user.check_password(current_password):
            raise ValidationError("當前密碼不正確。")
        return current_password

    # 驗證新密碼
    def clean_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        if not new_password:
            raise ValidationError("請輸入新密碼。")
        try:
            validate_password(new_password, self.user)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return new_password

    # 驗證表單
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        current_password = cleaned_data.get("current_password")
        # 檢查新密碼和再次確認的密碼是否相同
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError({"confirm_password": "新密碼與確認密碼不一致。"})
        # 檢查新密碼是否與當前密碼相同
        if current_password and new_password:
            if current_password == new_password:
                raise ValidationError({"new_password": "新密碼不能與當前密碼相同。"})
        return cleaned_data

    def save(self):
        new_password = self.cleaned_data["new_password"]
        self.user.set_password(new_password)
        self.user.save()
        return self.user

# 註冊表單
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "請輸入密碼"
        }),
        help_text="密碼至少8個字元，包含字母和數字"
    )
    password_confirmation = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "請再次輸入密碼"
        }),
        help_text="請再次輸入密碼"
    )

    class Meta:
        model = User
        fields = ["username", "email", "name", "gender"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "請輸入使用者名稱"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "請輸入電子信箱"
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "請輸入姓名"
            }),
            "gender": forms.Select(attrs={
                "class": "form-control"
            })
        }
        labels = {
            "username": "用戶名",
            "email": "電子信箱",
            "name": "姓名",
            "gender": "性別"
        }

    # 檢查 email 是否被使用過
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("此電子信箱已被註冊。")
        return email

    # 檢查用戶名是否被使用
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("該名稱已被使用。")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")
        if password and password_confirmation:
            if password != password_confirmation:
                raise ValidationError({"password_confirmation": "密碼與確認密碼不一致。"})
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
