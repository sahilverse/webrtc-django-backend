from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all required fields, plus repeated password."""
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        # Check passwords match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all fields but replaces password field with admin's password hash display."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )

    def clean_password(self):
        return self.initial["password"]


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "id",
        "email",
        "full_name",
        "is_online",
        "last_seen",
        "created_at",
        "profile_picture_preview",
        "is_staff",
    )
    list_filter = ("is_online", "created_at", "updated_at", "is_staff", "is_superuser")
    search_fields = ("id", "email", "first_name", "last_name")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at", "profile_picture_preview")

    fieldsets = (
        (_("Identification"), {"fields": ("id",)}),
        (_("Login Info"), {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name", "profile_image", "profile_picture_preview")}),
        (_("Status"), {"fields": ("is_online", "last_seen")}),
        (_("Important Dates"), {"fields": ("created_at", "updated_at")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    def full_name(self, obj):
        return obj.get_full_name()

    full_name.short_description = "Full Name"

    def profile_picture_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%;" />',
                obj.profile_image.url,
            )
        return "-"

    profile_picture_preview.short_description = "Profile Picture"
