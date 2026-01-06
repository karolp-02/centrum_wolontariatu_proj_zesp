from django.contrib import admin
from .models import (
    Organizacja,
    Uzytkownik,
    Projekt,
    Oferta,
    Zlecenie,
    Wiadomosc,
    Recenzja,
)


# --- INLINES ---
class ZlecenieInline(admin.TabularInline):
    model = Zlecenie
    extra = 0
    # Temporarily removed autocomplete to prevent lookup errors
    fields = ("wolontariusz", "czy_potwierdzone", "czy_ukonczone")


class OfertaInline(admin.StackedInline):
    model = Oferta
    extra = 0
    show_change_link = True


# --- ADMIN CONFIGURATION ---


# FIX: We switch from UserAdmin to ModelAdmin.
# This stops Django from trying to hide fields it doesn't understand.
@admin.register(Uzytkownik)
class CustomUserAdmin(admin.ModelAdmin):
    # 1. The List View (Columns)
    list_display = ("email", "username", "rola", "nr_telefonu", "is_active")
    list_filter = ("rola", "is_staff", "is_active")
    search_fields = ("email", "username", "last_name")
    ordering = ("email",)

    # 2. The Edit Form (Explicitly defined so they MUST show up)
    fieldsets = (
        ("Konto", {"fields": ("email", "username", "password")}),
        (
            "Dane Osobowe",
            {"fields": ("first_name", "last_name", "nr_telefonu", "wiek")},
        ),
        ("Rola", {"fields": ("rola", "organizacja")}),
        (
            "Uprawnienia",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),  # Click to expand
            },
        ),
    )


@admin.register(Organizacja)
class OrganizacjaAdmin(admin.ModelAdmin):
    list_display = ("nazwa_organizacji", "nip", "nr_telefonu", "weryfikacja")
    search_fields = ("nazwa_organizacji", "nip")
    list_filter = ("weryfikacja",)
    actions = ["zweryfikuj_organizacje"]

    def zweryfikuj_organizacje(self, request, queryset):
        queryset.update(weryfikacja=True)


@admin.register(Projekt)
class ProjektAdmin(admin.ModelAdmin):
    list_display = ("nazwa_projektu", "organizacja")
    search_fields = ("nazwa_projektu",)
    list_filter = ("organizacja",)
    inlines = [OfertaInline]


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ("tytul_oferty", "organizacja", "czy_ukonczone")
    search_fields = ("tytul_oferty", "lokalizacja")
    list_filter = ("czy_ukonczone", "organizacja")
    inlines = [ZlecenieInline]


@admin.register(Zlecenie)
class ZlecenieAdmin(admin.ModelAdmin):
    list_display = ("oferta", "wolontariusz", "czy_ukonczone", "czy_potwierdzone")
    list_filter = ("czy_ukonczone", "czy_potwierdzone")
    search_fields = ("oferta__tytul_oferty", "wolontariusz__email")


@admin.register(Wiadomosc)
class WiadomoscAdmin(admin.ModelAdmin):
    list_display = ("nadawca", "odbiorca", "data_wyslania")
    search_fields = ("nadawca__email", "odbiorca__email")


@admin.register(Recenzja)
class RecenzjaAdmin(admin.ModelAdmin):
    list_display = ("organizacja", "wolontariusz", "ocena")
    list_filter = ("ocena",)
