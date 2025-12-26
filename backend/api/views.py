from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.contrib.auth import authenticate
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from wolontariat.pdf_utils import get_pl_font_names
from wolontariat.models import Projekt, Oferta, Uzytkownik, Organizacja, Recenzja, Zlecenie
from .serializers import (
    ProjektSerializer, OfertaSerializer, OfertaCreateSerializer,
    UzytkownikSerializer, OrganizacjaSerializer,
    RecenzjaSerializer, RecenzjaCreateSerializer
)
from .permissions import IsOrganization, IsOwnerOrReadOnly



class ProjektViewSet(viewsets.ModelViewSet):
    serializer_class = ProjektSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Projekt.objects.all()

        # Filter by organization
        organizacja_id = self.request.query_params.get('organizacja')
        if organizacja_id:
            queryset = queryset.filter(organizacja_id=organizacja_id)

        # Search in project name or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nazwa_projektu__icontains=search) |
                Q(opis_projektu__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        if self.request.user.rola not in ['organizacja', 'koordynator']:
            raise PermissionError('Only organizations and coordinators can create projects')

        if self.request.user.rola == 'organizacja' and self.request.user.organizacja:
            serializer.save(organizacja=self.request.user.organizacja)
        else:
            serializer.save()

    @action(detail=True, methods=['get'])
    def oferty(self, request, pk=None):
        """Get all offers for a specific project"""
        project = self.get_object()
        offers = project.oferty.all()
        serializer = OfertaSerializer(offers, many=True)
        return Response(serializer.data)

class OfertaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return OfertaCreateSerializer
        return OfertaSerializer

    def get_queryset(self):
        queryset = Oferta.objects.all()

        projekt_id = self.request.query_params.get('projekt')
        if projekt_id:
            queryset = queryset.filter(projekt_id=projekt_id)

        organizacja_id = self.request.query_params.get('organizacja')
        if organizacja_id:
            queryset = queryset.filter(organizacja_id=organizacja_id)

        lokalizacja = self.request.query_params.get('lokalizacja')
        if lokalizacja:
            queryset = queryset.filter(lokalizacja__icontains=lokalizacja)

        tematyka = self.request.query_params.get('tematyka')
        if tematyka:
            queryset = queryset.filter(tematyka__icontains=tematyka)

        czas_trwania = self.request.query_params.get('czas_trwania')
        if czas_trwania:
            queryset = queryset.filter(czas_trwania__icontains=czas_trwania)

        tylko_wolne = self.request.query_params.get('tylko_wolne')
        if tylko_wolne and tylko_wolne.lower() == 'true':
            queryset = queryset.filter(zlecenia__isnull=True)

        wymagania = self.request.query_params.get('wymagania')
        if wymagania:
            queryset = queryset.filter(wymagania__icontains=wymagania)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(tytul_oferty__icontains=search) |
                Q(lokalizacja__icontains=search) |
                Q(tematyka__icontains=search) |
                Q(wymagania__icontains=search)
            )

        completed = self.request.query_params.get('completed')
        if completed is not None:
            if completed.lower() == 'true':
                queryset = queryset.filter(czy_ukonczone=True)
            else:
                queryset = queryset.filter(czy_ukonczone=False)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.rola in ['organizacja', 'koordynator'] and self.request.user.organizacja:
            serializer.save(organizacja=self.request.user.organizacja)
        else:
            raise serializers.ValidationError({"error": "Only organization users can create offers"})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        """Apply for an offer (volunteers only)"""
        offer = self.get_object()

        if request.user.rola != 'wolontariusz':
            return Response({'error': 'Only volunteers can apply'}, status=status.HTTP_403_FORBIDDEN)

        if offer.czy_ukonczone:
            return Response({'error': 'Offer is closed'}, status=status.HTTP_400_BAD_REQUEST)

        # Create Zlecenie with default status
        zlecenie, created = Zlecenie.objects.get_or_create(oferta=offer, wolontariusz=request.user)

        if not created:
             return Response({'message': 'Already applied'}, status=status.HTTP_200_OK)

        return Response(OfertaSerializer(offer).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm_volunteer(self, request, pk=None):
        """Organization/Coordinator accepts application"""
        offer = self.get_object()

        # Permission Check
        if request.user.rola not in ['organizacja', 'koordynator']:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # RESTRICTION: Only Organizations must own the offer. Coordinators can approve any (simplified).
        if request.user.rola == 'organizacja' and offer.organizacja != request.user.organizacja:
                return Response({'error': 'Not your offer'}, status=status.HTTP_403_FORBIDDEN)

        vol_id = request.data.get('wolontariusz_id')
        try:
            zlecenie = Zlecenie.objects.get(oferta=offer, wolontariusz_id=vol_id)
            zlecenie.czy_potwierdzone = True
            zlecenie.save()
            return Response(OfertaSerializer(offer).data)
        except Zlecenie.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve_volunteer(self, request, pk=None):
        """Organization/Coordinator marks work as done"""
        offer = self.get_object()

        # Permission Check
        if request.user.rola not in ['organizacja', 'koordynator']:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # RESTRICTION: Only Organizations must own the offer. Coordinators can approve any.
        if request.user.rola == 'organizacja' and offer.organizacja != request.user.organizacja:
                return Response({'error': 'Not your offer'}, status=status.HTTP_403_FORBIDDEN)

        vol_id = request.data.get('wolontariusz_id')
        try:
            zlecenie = Zlecenie.objects.get(oferta=offer, wolontariusz_id=vol_id)
            zlecenie.czy_ukonczone = True
            zlecenie.save()
            return Response(OfertaSerializer(offer).data)
        except Zlecenie.DoesNotExist:
            return Response({'error': 'Volunteer not assigned'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def withdraw(self, request, pk=None):
        """Withdraw application"""
        offer = self.get_object()
        Zlecenie.objects.filter(oferta=offer, wolontariusz=request.user).delete()
        return Response(OfertaSerializer(offer).data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def certificate(self, request, pk=None):
        offer = self.get_object()
        has_completed = Zlecenie.objects.filter(oferta=offer, wolontariusz=request.user, czy_ukonczone=True).exists()

        if not has_completed:
            return Response({'error': 'You have not completed this offer'}, status=status.HTTP_403_FORBIDDEN)

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        try:
            regular_font, bold_font = get_pl_font_names()
            pdf.setFont(bold_font, 20)
        except:
            pdf.setFont("Helvetica-Bold", 20)

        pdf.drawCentredString(A4[0] / 2, A4[1] - 100, "Zaświadczenie")
        pdf.drawString(100, A4[1] - 150, f"Wolontariusz: {request.user.username}")
        pdf.drawString(100, A4[1] - 180, f"Ukończył ofertę: {offer.tytul_oferty}")
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        resp = HttpResponse(buffer.read(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="certificate.pdf"'
        return resp

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_offers(self, request):
        if request.user.rola == 'wolontariusz':
            offers = Oferta.objects.filter(zlecenia__wolontariusz=request.user).distinct()
        elif request.user.rola in ['organizacja', 'koordynator'] and request.user.organizacja:
            offers = Oferta.objects.filter(organizacja=request.user.organizacja)
        else:
            offers = Oferta.objects.none()
        return Response(OfertaSerializer(offers, many=True).data)

class UzytkownikViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UzytkownikSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.rola in ['organizacja', 'koordynator']:
            return Uzytkownik.objects.filter(rola='wolontariusz')
        return Uzytkownik.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = UzytkownikSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def volunteers(self, request):
        """Get all volunteers (for organizations/coordinators)"""
        if request.user.rola not in ['organizacja', 'koordynator']:
            return Response(
                {'error': 'Only organizations and coordinators can view all volunteers'},
                status=status.HTTP_403_FORBIDDEN
            )

        volunteers = Uzytkownik.objects.filter(rola='wolontariusz')
        serializer = UzytkownikSerializer(volunteers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def certificate(self, request, pk=None):
        """
        Generate and download a certificate for the volunteer's completed offers
        """
        user = self.get_object()

        # Check if the requesting user is authorized to access this certificate
        if request.user != user and request.user.rola not in ['organizacja', 'koordynator']:
            return Response(
                {'error': 'You are not authorized to view this certificate'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the user is a volunteer
        if user.rola != 'wolontariusz':
            return Response(
                {'error': 'Certificates are only available for volunteers'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the volunteer has any completed assignments
        if not user.zlecenia.filter(czy_ukonczone=True).exists():
            return Response(
                {'error': 'This volunteer has no completed assignments'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Generate the certificate PDF
            pdf_file = user.certyfikat_gen()

            # Create the HTTP response with PDF content
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="certificate_{user.username}.pdf"'
            return response

        except Exception as e:
            return Response(
                {'error': f'Error generating certificate: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_certificate(self, request):
        """
        Generate and download certificate for the current user
        """
        user = request.user

        # Check if the user is a volunteer
        if user.rola != 'wolontariusz':
            return Response(
                {'error': 'Certificates are only available for volunteers'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the volunteer has any completed assignments
        if not user.zlecenia.filter(czy_ukonczone=True).exists():
            return Response(
                {'error': 'You have no completed assignments yet'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Generate the certificate PDF
            pdf_file = user.certyfikat_gen()

            # Create the HTTP response with PDF content
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="certificate_{user.username}.pdf"'
            return response

        except Exception as e:
            return Response(
                {'error': f'Error generating certificate: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OrganizacjaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrganizacjaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Organizacja.objects.filter(weryfikacja=True)

    @action(detail=True, methods=['get'])
    def projekty(self, request, pk=None):
        """Get all projects for a specific organization"""
        organization = self.get_object()
        projects = organization.projekty.all()
        serializer = ProjektSerializer(projects, many=True)
        return Response(serializer.data)

class RecenzjaViewSet(viewsets.ModelViewSet):
    """
    create: organization posts a review for a volunteer (via oferta)
    list: public list (or restricted) — we'll allow read for any, write only for org
    update/destroy: only the org that created the review may change it
    """
    queryset = Recenzja.objects.select_related('organizacja', 'wolontariusz', 'oferta').all()
    # Corrected permission assignment
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsOrganization()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return RecenzjaCreateSerializer
        return RecenzjaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Allow filtering by wolontariusz id via ?wolontariusz=123
        wol_id = self.request.query_params.get('wolontariusz')
        if wol_id:
            qs = qs.filter(wolontariusz__id=wol_id)
        return qs

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    User registration endpoint
    """
    required_fields = ['username', 'email', 'password', 'rola', 'nr_telefonu']

    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'Missing required field: {field}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    if Uzytkownik.objects.filter(username=request.data['username']).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if Uzytkownik.objects.filter(email=request.data['email']).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Additional validation for volunteers: require wiek
    rola = request.data.get('rola')
    if rola == 'wolontariusz':
        if 'wiek' not in request.data:
            return Response({'error': 'Missing required field: wiek'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            wiek_val = int(request.data.get('wiek'))
            if wiek_val < 0 or wiek_val > 120:
                return Response({'error': 'Wiek musi być liczbą w zakresie 0-120'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Wiek musi być liczbą całkowitą'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Uzytkownik.objects.create_user(
            username=request.data['username'],
            email=request.data['email'],
            password=request.data['password'],
            rola=request.data['rola'],
            nr_telefonu=request.data['nr_telefonu'],
            wiek=request.data.get('wiek', None),
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
        )

        # Optionally attach organization for organization/coordinator accounts
        if 'organizacja_id' in request.data and request.data['rola'] in ['organizacja', 'koordynator']:
            user.organizacja_id = request.data['organizacja_id']
            user.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'user': UzytkownikSerializer(user).data,
            'token': token.key,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login endpoint
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UzytkownikSerializer(user).data,
            'token': token.key
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """
    User logout endpoint
    """
    if request.auth:
        request.auth.delete()

    return Response({'message': 'Successfully logged out'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def certificate(request):
    """
    Generate and download a PDF certificate for the current user
    based on completed assignments.
    """
    user: Uzytkownik = request.user  # type: ignore
    try:
        content_file = user.certyfikat_gen()
        resp = HttpResponse(content_file.read(), content_type='application/pdf')
        filename = f"zaswiadczenie_{user.username}.pdf"
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
