from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from wolontariat.models import Projekt, Oferta, Uzytkownik, Organizacja, Recenzja, Zlecenie

class OrganizacjaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizacja
        fields = ['id', 'nazwa_organizacji', 'nr_telefonu', 'nip', 'weryfikacja']

class UzytkownikSerializer(serializers.ModelSerializer):
    organizacja = OrganizacjaSerializer(read_only=True)
    organizacja_id = serializers.PrimaryKeyRelatedField(
        source='organizacja', queryset=Organizacja.objects.all(), write_only=True, required=False
    )
    organizacja_nazwa = serializers.CharField(source='organizacja.nazwa_organizacji', read_only=True)
    czy_maloletni = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Uzytkownik
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nr_telefonu', 'wiek', 'organizacja', 'organizacja_id', 'organizacja_nazwa', 'rola', 'czy_maloletni'
        ]
        read_only_fields = ['id', 'username', 'email']

    def get_czy_maloletni(self, obj: Uzytkownik):
        try:
            return obj.wiek is not None and int(obj.wiek) < 18
        except Exception:
            return False

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
            'tytul_oferty', 'lokalizacja', 'tematyka', 'czas_trwania', 'wymagania',
            'data',
            'data_wyslania', 'wolontariusz', 'wolontariusz_info',
            'wolontariusze', 'liczba_uczestnikow', 'czy_ukonczone'
        ]
        read_only_fields = ['organizacja', 'data_wyslania']

    def get_wolontariusze(self, obj):
        # Fetch volunteers with their specific Zlecenie status
        zlecenia = Zlecenie.objects.filter(oferta=obj).select_related('wolontariusz')
        results = []
        for z in zlecenia:
            user_data = UzytkownikSerializer(z.wolontariusz).data
            user_data['czy_potwierdzone'] = z.czy_potwierdzone
            user_data['czy_ukonczone'] = z.czy_ukonczone
            results.append(user_data)
        return results

    def get_liczba_uczestnikow(self, obj):
        return Zlecenie.objects.filter(oferta=obj).count()

class OfertaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oferta
        fields = [
            'projekt', 'tytul_oferty', 'lokalizacja',
            'tematyka', 'czas_trwania', 'wymagania', 'data',
            'data_wyslania'
        ]

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Uzytkownik
        fields = ['username', 'email', 'password', 'password2', 'rola', 'nr_telefonu', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = Uzytkownik.objects.create_user(**validated_data)
        return user

class RecenzjaSerializer(serializers.ModelSerializer):
    organizacja = serializers.StringRelatedField(read_only=True)
    wolontariusz = serializers.StringRelatedField(read_only=True)
    oferta = serializers.PrimaryKeyRelatedField(queryset=Oferta.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Recenzja
        fields = ['id', 'organizacja', 'wolontariusz', 'oferta', 'ocena', 'komentarz', 'created_at']
        read_only_fields = ['id', 'organizacja', 'wolontariusz', 'created_at']

class RecenzjaCreateSerializer(serializers.ModelSerializer):
    oferta = serializers.PrimaryKeyRelatedField(queryset=Oferta.objects.all(), required=False, allow_null=True)
    wolontariusz = serializers.PrimaryKeyRelatedField(queryset=Uzytkownik.objects.all(), required=False, allow_null=True, write_only=True)

    class Meta:
        model = Recenzja
        fields = ['oferta', 'ocena', 'komentarz', 'wolontariusz']

    def validate_ocena(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Ocena musi być liczbą od 1 do 5.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        # 1. Check Permissions
        if not user or getattr(user, 'rola', None) != 'organizacja':
            raise serializers.ValidationError("Tylko organizacje mogą wystawiać recenzje.")

        oferta = data.get('oferta', None)
        if not oferta:
             raise serializers.ValidationError("Musisz podać 'oferta' aby ocenić wolontariusza.")

        # 2. Check Ownership
        if oferta.organizacja != user.organizacja:
            raise serializers.ValidationError("Ta oferta nie należy do Twojej organizacji.")

        # 3. Determine Volunteer (Explicit or Implicit)
        target_volunteer = None
        explicit_vol = data.get('wolontariusz')

        if explicit_vol:
             # Check if this volunteer is actually assigned to the offer
             # Use the correct model import here:
             from wolontariat.models import Zlecenie
             if not Zlecenie.objects.filter(oferta=oferta, wolontariusz=explicit_vol).exists():
                 # Fallback for legacy data (direct assignment)
                 if oferta.wolontariusz_id != explicit_vol.id:
                     raise serializers.ValidationError("Podany wolontariusz nie jest uczestnikiem tej oferty.")
             target_volunteer = explicit_vol
             data['wolontariusz'] = explicit_vol
        else:
             # Try to deduce volunteer
             if oferta.wolontariusz:
                 target_volunteer = oferta.wolontariusz
             else:
                 from wolontariat.models import Zlecenie
                 zlecenia = Zlecenie.objects.filter(oferta=oferta)
                 if zlecenia.count() == 1:
                     target_volunteer = zlecenia.first().wolontariusz
                 elif zlecenia.count() == 0:
                     raise serializers.ValidationError("Brak uczestników dla tej oferty.")
                 else:
                     raise serializers.ValidationError("W ofercie bierze udział wielu wolontariuszy. Wskaż konkretnego wolontariusza (pole 'wolontariusz').")
             data['wolontariusz'] = target_volunteer

        # 4. Check Completion Status (Volunteer-Specific)
        # We check if THIS volunteer has finished the work (Zlecenie.czy_ukonczone=True)
        # OR if the offer is globally closed (legacy support)
        from wolontariat.models import Zlecenie
        is_completed = False

        # Check specific Zlecenie
        if Zlecenie.objects.filter(oferta=oferta, wolontariusz=target_volunteer, czy_ukonczone=True).exists():
            is_completed = True
        # Check global flag
        elif oferta.czy_ukonczone:
            is_completed = True

        if not is_completed:
             raise serializers.ValidationError("Można ocenić wolontariusza tylko po zakończeniu jego wolontariatu (zatwierdzeniu ukończenia).")

        # 5. Check Duplicates
        if Recenzja.objects.filter(oferta=oferta, organizacja=user.organizacja, wolontariusz=target_volunteer).exists():
            raise serializers.ValidationError("Recenzja dla tego wolontariusza w tej ofercie już istnieje.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        org = request.user.organizacja
        validated_data['organizacja'] = org
        return super().create(validated_data)
