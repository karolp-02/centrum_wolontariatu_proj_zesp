from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from wolontariat.models import (
    Uzytkownik,
    Organizacja,
    Projekt,
    Oferta,
    Zlecenie,
    Wiadomosc,
    Recenzja,
)


@admin.register(Uzytkownik)
class UzytkownikAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("rola", "nr_telefonu", "wiek", "organizacja")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("rola", "nr_telefonu", "wiek", "organizacja")}),
    )
    list_display = ("email", "username", "rola", "is_staff")
    search_fields = ("email", "username")


admin.site.register(Organizacja)
admin.site.register(Projekt)
admin.site.register(Oferta)
admin.site.register(Zlecenie)
admin.site.register(Wiadomosc)
admin.site.register(Recenzja)
