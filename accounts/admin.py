from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Address, ProfessionalInfo
from accounts.services.stripe_service import create_stripe_account

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'phone_number',
            'subscribed_to_newsletter', 'is_staff', 'is_verifier', 'is_active'
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'phone_number',
            'subscribed_to_newsletter', 'accepted_terms', 'accepted_terms_at',
            'is_staff', 'is_verifier', 'is_active', 'groups'
        )

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'username', 'first_name', 'last_name', 'email', 'phone_number',
        'role', 'rating', 'stripe_account_id', 'stripe_account_status', 'is_kyc_verified',
        'subscribed_to_newsletter', 'accepted_terms', 'accepted_terms_at',
        'is_staff', 'is_verifier', 'is_superuser', 'is_active'
    )
    list_filter = ('is_staff', 'is_verifier', 'is_superuser', 'is_active', 'subscribed_to_newsletter', 'accepted_terms')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': (
            'first_name', 'last_name', 'email', 'phone_number',
            'subscribed_to_newsletter', 'accepted_terms', 'accepted_terms_at',
            'role', 'rating', 'stripe_account_status', 'is_kyc_verified'
        )
        }),
        ('Permissions', {'fields': ('is_staff', 'is_verifier', 'is_superuser', 'is_active', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'phone_number',
                'subscribed_to_newsletter', 'role',
                'password1', 'password2',
                'is_staff', 'is_verifier', 'is_active', 'groups'
            ),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('username',)
    filter_horizontal = ('groups',)
    readonly_fields = ('rating', 'stripe_account_id', 'is_kyc_verified')

    def save_model(self, request, obj, form, change):
        # S'assurer que le mot de passe est haché pour les nouveaux utilisateurs
        if not change and form.cleaned_data.get('password1'):
            obj.set_password(form.cleaned_data['password1'])

        if obj.role == User.Role.PARTICULIER and obj.is_seller and not obj.stripe_account_id:
            create_stripe_account(obj)

        super().save_model(request, obj, form, change)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'city', 'postal_code', 'country')
    search_fields = ('user__username', 'street', 'city', 'postal_code', 'country')
    list_filter = ('country', 'city')


@admin.register(ProfessionalInfo)
class ProfessionalInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'siret_number', 'vat_number')
    search_fields = ('user__username', 'company_name', 'siret_number', 'vat_number')
