# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Address

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff', 'is_verifier', 'is_active')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff', 'is_verifier', 'is_active', 'groups')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('username', 'email', 'is_staff', 'is_verifier', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_verifier', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_staff', 'is_verifier', 'is_superuser', 'is_active', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_verifier', 'is_active', 'groups'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups',)

    def save_model(self, request, obj, form, change):
        # S'assurer que le mot de passe est haché pour les nouveaux utilisateurs
        if not change and form.cleaned_data.get('password1'):
            obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'city', 'postal_code', 'country')
    search_fields = ('user__username', 'street', 'city', 'postal_code', 'country')
    list_filter = ('country', 'city')