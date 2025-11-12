from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from wolontariat.models import Projekt, Oferta, Uzytkownik, Organizacja, Recenzja

class ProjektSerializer(serializers.ModelSerializer):
    organizacja_nazwa = serializers.CharField(source='organizacja.nazwa_organizacji', read_only=True)
    oferty_count = serializers.IntegerField(source='oferty.count', read_only=True)

    class Meta:
        model = Projekt
        fields = [
            'id', 'organizacja', 'organizacja_nazwa', 'nazwa_projektu',
            'opis_projektu', 'oferty_count'
        ]

class OfertaSerializer(serializers.ModelSerializer):
    projekt_nazwa = serializers.CharField(source='projekt.nazwa_projektu', read_only=True)
    organizacja_nazwa = serializers.CharField(source='organizacja.nazwa_organizacji', read_only=True)
    wolontariusz_info = UzytkownikSerializer(source='wolontariusz', read_only=True)
    wolontariusze = serializers.SerializerMethodField()
    liczba_uczestnikow = serializers.SerializerMethodField()

    class Meta:
        model = Oferta
        fields = [
            'id', 'organizacja', 'organizacja_nazwa', 'projekt', 'projekt_nazwa',
            'tytul_oferty', 'lokalizacja', 'tematyka', 'czas_trwania', 'wymagania',  # Added new fields
            'data',
            'data_wyslania', 'wolontariusz', 'wolontariusz_info',
            'wolontariusze', 'liczba_uczestnikow', 'czy_ukonczone'
        ]
        read_only_fields = ['organizacja', 'data_wyslania']


    # Helpers for multi-assignment via Zlecenie
    def get_wolontariusze(self, obj):
        from wolontariat.models import Uzytkownik
        qs = Uzytkownik.objects.filter(zlecenia__oferta=obj).distinct()
        return UzytkownikSerializer(qs, many=True).data

    def get_liczba_uczestnikow(self, obj):
        from wolontariat.models import Uzytkownik
        return Uzytkownik.objects.filter(zlecenia__oferta=obj).distinct().count()

class OfertaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oferta
        fields = [
            'projekt', 'tytul_oferty', 'lokalizacja',
            'tematyka', 'czas_trwania', 'wymagania', 'data',  # Added new fields
            'data_wyslania'
        ]
    pass
