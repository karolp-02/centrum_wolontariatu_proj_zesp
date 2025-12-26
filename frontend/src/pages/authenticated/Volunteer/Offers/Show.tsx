import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getOfferById, applyToOffer, withdrawApplication } from "@/api/offers";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Calendar, MapPin, Clock, Tag, Users, Building } from "lucide-react";

export default function VolunteerOfferShowPage() {
  const params = useParams();
  const id = Number(params.id);
  const [offer, setOffer] = useState<Oferta | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    getOfferById(id).then((o) => setOffer(o || null));
  }, [id]);

  if (!offer) return <div>Nie znaleziono oferty</div>;

  // Determine user status in this offer
  const myStatus =
    offer.wolontariusze?.find((u) => u.id === user?.id) ||
    (offer.wolontariusz?.id === user?.id ? offer.wolontariusz : null);
  const alreadyApplied = Boolean(myStatus);
  const isConfirmed = myStatus?.czy_potwierdzone;

  const canApply = Boolean(user && !alreadyApplied && !offer.czy_ukonczone);
  // CANNOT withdraw if already confirmed
  const canWithdraw = Boolean(
    user && alreadyApplied && !offer.czy_ukonczone && !isConfirmed,
  );

  const onApply = async () => {
    if (!user) return;
    const updated = await applyToOffer(offer.id, user);
    if (updated) setOffer({ ...offer, ...updated });
  };

  const onWithdraw = async () => {
    if (!user) return;
    const updated = await withdrawApplication(offer.id, user);
    if (updated) setOffer({ ...offer, ...updated });
  };

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {offer.tytul_oferty}
          </h1>
          <div className="text-gray-500 mt-1">
            {offer.projekt.nazwa_projektu}
          </div>
        </div>
        <Link className="text-blue-600 hover:underline" to="/volunteer/offers">
          Wróć do listy
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <Card className="p-6 space-y-4">
            <h2 className="font-semibold text-xl">Opis i wymagania</h2>
            <div className="text-gray-700 whitespace-pre-line leading-relaxed">
              {offer.wymagania ||
                "Brak szczegółowych wymagań. Skontaktuj się z organizatorem, aby dowiedzieć się więcej."}
            </div>
          </Card>

          <Card className="p-6 space-y-4">
            <h2 className="font-semibold text-xl">Szczegóły projektu</h2>
            <p className="text-gray-700">{offer.projekt.opis_projektu}</p>

            <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 uppercase tracking-wide">
                  Organizator
                </div>
                <div className="font-medium">
                  {offer.organizacja.nazwa_organizacji}
                </div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 uppercase tracking-wide">
                  Kontakt
                </div>
                <div className="font-medium">
                  {offer.organizacja.nr_telefonu}
                </div>
              </div>
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <Card className="p-5 space-y-4">
            <div className="space-y-3 text-sm">
              {offer.data && (
                <div className="flex items-center gap-3">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <span>
                    {new Date(offer.data + "T00:00:00").toLocaleDateString(
                      "pl-PL",
                    )}
                  </span>
                </div>
              )}
              {offer.lokalizacja && (
                <div className="flex items-center gap-3">
                  <MapPin className="w-4 h-4 text-gray-500" />
                  <span>{offer.lokalizacja}</span>
                </div>
              )}
              {offer.czas_trwania && (
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span>{offer.czas_trwania}</span>
                </div>
              )}
              {offer.tematyka && (
                <div className="flex items-center gap-3">
                  <Tag className="w-4 h-4 text-gray-500" />
                  <span>{offer.tematyka}</span>
                </div>
              )}
              <div className="flex items-center gap-3">
                <Users className="w-4 h-4 text-gray-500" />
                <span>
                  Uczestnicy:{" "}
                  {offer.liczba_uczestnikow ?? (offer.wolontariusz ? 1 : 0)}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <Building className="w-4 h-4 text-gray-500" />
                <span>
                  Status: {offer.czy_ukonczone ? "Ukończone" : "Otwarte"}
                </span>
              </div>
            </div>

            <div className="pt-4 border-t">
              {alreadyApplied ? (
                <div className="space-y-2">
                  <Button
                    disabled
                    className="w-full bg-green-600/10 text-green-700 hover:bg-green-600/20 border-green-200 border"
                  >
                    {isConfirmed
                      ? "Zgłoszenie przyjęte"
                      : "Zgłoszono - Oczekuj"}
                  </Button>
                  {canWithdraw && (
                    <Button
                      variant="outline"
                      className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={onWithdraw}
                    >
                      Wycofaj zgłoszenie
                    </Button>
                  )}
                  {isConfirmed && (
                    <p className="text-xs text-center text-gray-500">
                      Nie możesz wycofać potwierdzonego zgłoszenia.
                    </p>
                  )}
                </div>
              ) : (
                <Button
                  className="w-full"
                  onClick={onApply}
                  disabled={!canApply}
                >
                  Aplikuj teraz
                </Button>
              )}
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
