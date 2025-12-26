from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .pdf_utils import get_pl_font_names
from io import BytesIO
from django.core.files.base import ContentFile

# ---Organizacja---
class Organizacja(models.Model):
    telefon_validator = RegexValidator(
        regex=r'^\d{9}$',
        message="Numer telefonu musi składać się z dokładnie 9 cyfr."
    )

    nazwa_organizacji = models.CharField(max_length=100)
    nr_telefonu = models.CharField(max_length=9, validators=[telefon_validator], help_text="Podaj numer telefonu składający się tylko z 9 cyfr")
    nip = models.CharField(max_length=10, unique=True)
    weryfikacja = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.nip:
            self.weryfikacja = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nazwa_organizacji


# ---Uzytkownik---
class Uzytkownik(AbstractUser):
    telefon_validator = RegexValidator(regex=r'^\d{9}$', message="Numer telefonu musi składać się z dokładnie 9 cyfr.")

    email = models.EmailField(unique=True)
    nr_telefonu = models.CharField(max_length=9, validators=[telefon_validator], help_text="Podaj numer telefonu składający się tylko z 9 cyfr")
    wiek = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Wiek")
    organizacja = models.ForeignKey('Organizacja', on_delete=models.SET_NULL, null=True, blank=True, related_name='uzytkownicy')

    ROLE_TYPE = [
        ('wolontariusz', 'Wolontariusz'),
        ('koordynator', 'Koordynator'),
        ('organizacja', 'Organizacja'),
    ]
    rola = models.CharField(max_length=20, choices=ROLE_TYPE)

    groups = models.ManyToManyField(
        'auth.Group', verbose_name='groups', blank=True, related_name='uzytkownik_set', related_query_name='uzytkownik'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name='user permissions', blank=True, related_name='uzytkownik_set', related_query_name='uzytkownik'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.rola})"

    def certyfikat_gen(self):
        # Fetch completed assignments via Zlecenie
        completed_zlecenia = self.zlecenia.filter(czy_ukonczone=True)

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawCentredString(width / 2, height - 100, "Zaświadczenie ukończenia zleceń")

        pdf.setFont("Helvetica", 14)
        pdf.drawString(100, height - 150, f"Wolontariusz: {self.username}")
        pdf.drawString(100, height - 170, f"E-mail: {self.email}")

        pdf.drawString(100, height - 200, "Ukończone zlecenia:")
        y = height - 220
        for zlecenie in completed_zlecenia:
            pdf.drawString(120, y, f"- {zlecenie.oferta.tytul_oferty} ({zlecenie.oferta.projekt.nazwa_projektu})")
            y -= 20
            if y < 50:
                pdf.showPage()
                y = height - 50

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return ContentFile(buffer.read(), name=f"zaswiadczenie_{self.username}.pdf")


# ---Projekt---
class Projekt(models.Model):
    organizacja = models.ForeignKey(Organizacja, on_delete=models.CASCADE, related_name='projekty')
    nazwa_projektu = models.CharField(max_length=100)
    opis_projektu = models.TextField()

    def __str__(self):
        return self.nazwa_projektu


# ---Oferta---
class Oferta(models.Model):
    organizacja = models.ForeignKey(Organizacja, on_delete=models.CASCADE, related_name='oferty')
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE, related_name='oferty')
    tytul_oferty = models.CharField(max_length=100)
    lokalizacja = models.CharField(max_length=100)
    data = models.DateField(null=True, blank=True)
    data_wyslania = models.DateTimeField(default=timezone.now)

    # NOTE: We keep this for backward compatibility but business logic should rely on Zlecenie
    wolontariusz = models.ForeignKey(Uzytkownik, on_delete=models.SET_NULL, null=True, blank=True, related_name='oferty')

    czy_ukonczone = models.BooleanField(default=False)
    tematyka = models.CharField(max_length=100, blank=True)
    czas_trwania = models.CharField(max_length=50, blank=True)
    wymagania = models.TextField(blank=True)

    def __str__(self):
        return self.tytul_oferty


# ---Zlecenie---
class Zlecenie(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='zlecenia')
    # CHANGED: ForeignKey instead of ManyToMany to track individual status
    wolontariusz = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='zlecenia')

    czy_ukonczone = models.BooleanField(default=False)     # Did they finish the job?
    czy_potwierdzone = models.BooleanField(default=False)  # Did the Org accept their application?

    class Meta:
        unique_together = ('oferta', 'wolontariusz')

    def __str__(self):
        return f"Zlecenie: {self.oferta} - {self.wolontariusz}"

# ---Wiadomosc & Recenzja (unchanged)---
class Wiadomosc(models.Model):
    nadawca = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='wyslane_wiadomosci')
    odbiorca = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='otrzymane_wiadomosci')
    tresc = models.TextField()
    data_wyslania = models.DateTimeField(auto_now_add=True)

class Recenzja(models.Model):
    organizacja = models.ForeignKey('Organizacja', on_delete=models.CASCADE, related_name='recenzje')
    wolontariusz = models.ForeignKey('Uzytkownik', on_delete=models.CASCADE, related_name='recenzje')
    oferta = models.ForeignKey('Oferta', on_delete=models.SET_NULL, null=True, blank=True, related_name='recenzje')
    ocena = models.PositiveSmallIntegerField()
    komentarz = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('oferta', 'organizacja')
