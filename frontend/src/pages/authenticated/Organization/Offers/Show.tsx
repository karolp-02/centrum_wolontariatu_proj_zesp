import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Pencil, ArrowLeft, CheckCircle, UserCheck, Star } from "lucide-react";
import {
  getOfferById,
  confirmVolunteerApplication,
  approveVolunteerCompletion,
} from "@/api/offers";
import { Card } from "@/components/ui/card";
import { createReview } from "@/api/reviews";
import { useAuth } from "@/hooks/useAuth";

export default function OrganizationOffersShowPage() {
  const params = useParams();
  const id = Number(params.id);
  const [offer, setOffer] = useState<Oferta | null>(null);
  const { user } = useAuth();

  // Roles
  const isOrg = user?.rola === "organizacja";
  const isCoordinator = user?.rola === "koordynator";

  // Both Org and Coordinator can manage volunteers (Confirm/Approve)
  const canManage = isOrg || isCoordinator;

  const fetchOffer = () => {
    getOfferById(id).then((o) => setOffer(o || null));
  };

  useEffect(() => {
    fetchOffer();
  }, [id]);

  const volunteers = useMemo(() => {
    if (!offer) return [];
    if (Array.isArray(offer.wolontariusze) && offer.wolontariusze.length > 0) {
      return offer.wolontariusze;
    }
    return offer.wolontariusz ? [offer.wolontariusz] : [];
  }, [offer]);

  const handleConfirm = async (volId: number) => {
    if (!window.confirm("Zaakceptować zgłoszenie wolontariusza?")) return;
    try {
      await confirmVolunteerApplication(offer!.id, volId);
      fetchOffer();
    } catch {
      alert("Błąd podczas potwierdzania.");
    }
  };

  const handleApprove = async (volId: number) => {
    if (!window.confirm("Zatwierdzić ukończenie wolontariatu?")) return;
    try {
      await approveVolunteerCompletion(offer!.id, volId);
      fetchOffer();
    } catch {
      alert("Błąd podczas zatwierdzania.");
    }
  };

  const handleReview = async (volId: number) => {
    const ratingStr = window.prompt("Ocena (1-5):");
    if (!ratingStr) return;
    const ocena = Number(ratingStr);
    if (!Number.isInteger(ocena) || ocena < 1 || ocena > 5) {
      alert("Podaj liczbę całkowitą od 1 do 5");
      return;
    }
    const komentarz = window.prompt("Komentarz (opcjonalny):") || "";
    try {
      await createReview({
        oferta: offer!.id,
        ocena,
        komentarz,
        wolontariusz: volId,
      });
      alert("Recenzja została dodana.");
    } catch (e: any) {
      const msg =
        e?.response?.data?.detail ||
        e?.response?.data?.non_field_errors?.[0] ||
        "Wystąpił błąd.";
      alert(`Nie udało się dodać recenzji: ${msg}`);
    }
  };

  if (!offer) return <div>Nie znaleziono oferty</div>;

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">{offer.tytul_oferty}</h1>
            <div className="text-sm text-gray-700">
              Projekt: <b>{offer.projekt.nazwa_projektu}</b>
            </div>
            <div className="text-sm text-gray-700">
              Organizacja: <b>{offer.organizacja.nazwa_organizacji}</b>
            </div>
            <div className="text-sm text-gray-700">
              Globalny Status: {offer.czy_ukonczone ? "Zamknięta" : "Otwarta"}
            </div>
          </div>
          <div className="flex gap-2 shrink-0">
            {/* Allow Edit for both Org and Coordinator (since Coords can create offers) */}
            {canManage && (
              <Button asChild>
                <Link to={`/organization/offers/${offer.id}/edit`}>
                  <Pencil className="w-4 h-4 mr-2" /> Edytuj
                </Link>
              </Button>
            )}
            <Button asChild variant="outline">
              <Link to={`/organization/projects/${offer.projekt.id}`}>
                <ArrowLeft className="w-4 h-4 mr-2" /> Wróć
              </Link>
            </Button>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2 text-xs">
          {offer.lokalizacja && (
            <span className="rounded bg-gray-100 px-2 py-0.5">
              {offer.lokalizacja}
            </span>
          )}
          {offer.tematyka && (
            <span className="rounded bg-blue-100 text-blue-800 px-2 py-0.5">
              {offer.tematyka}
            </span>
          )}
        </div>
      </Card>

      <Card className="p-4">
        <h2 className="font-semibold mb-3">Zgłoszeni wolontariusze</h2>
        {volunteers.length === 0 ? (
          <div className="text-sm text-gray-600">
            Brak zgłoszeń dla tej oferty.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="text-left text-xs text-gray-600 border-b">
                <tr>
                  <th className="py-2 pr-4">Użytkownik</th>
                  <th className="py-2 pr-4">Kontakt</th>
                  <th className="py-2 pr-4">Status Zgłoszenia</th>
                  <th className="py-2 pr-4">Status Pracy</th>
                  <th className="py-2 pr-4">Akcje</th>
                </tr>
              </thead>
              <tbody>
                {volunteers.map((v) => {
                  const isConfirmed = v.czy_potwierdzone;
                  const isCompleted = v.czy_ukonczone;

                  // Review condition: Only Organization can review, and work must be completed
                  const canReview = isOrg && isCompleted;

                  return (
                    <tr key={v.id} className="border-b last:border-0">
                      <td className="py-3 pr-4 align-top">
                        <Link
                          className="text-blue-600 hover:underline font-medium"
                          to={`/organization/volunteers/${v.id}`}
                        >
                          {v.username}
                        </Link>
                        <div className="mt-1">
                          <span
                            className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded border ${v.czy_maloletni ? "bg-yellow-50 border-yellow-300 text-yellow-700" : "bg-emerald-50 border-emerald-300 text-emerald-700"}`}
                          >
                            {v.czy_maloletni ? "Małoletni" : "Pełnoletni"}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 pr-4 align-top text-gray-600">
                        <div>{v.email}</div>
                        <div className="text-xs">{v.nr_telefonu}</div>
                      </td>
                      <td className="py-3 pr-4 align-top">
                        {isConfirmed ? (
                          <span className="text-green-700 bg-green-50 px-2 py-1 rounded text-xs border border-green-200">
                            Zaakceptowany
                          </span>
                        ) : (
                          <span className="text-yellow-700 bg-yellow-50 px-2 py-1 rounded text-xs border border-yellow-200">
                            Oczekuje
                          </span>
                        )}
                      </td>
                      <td className="py-3 pr-4 align-top">
                        {isCompleted ? (
                          <span className="text-blue-700 font-semibold text-xs">
                            Ukończono
                          </span>
                        ) : (
                          <span className="text-gray-400 text-xs">
                            W trakcie / Nie zaczęto
                          </span>
                        )}
                      </td>
                      <td className="py-3 pr-4 align-top flex flex-col gap-2 items-start">
                        {/* ACTION BUTTONS: Visible for Org OR Coordinator */}
                        {canManage && (
                          <>
                            {!isConfirmed && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleConfirm(v.id)}
                                className="h-7 text-xs w-full"
                              >
                                <UserCheck className="w-3 h-3 mr-1" /> Przyjmij
                              </Button>
                            )}

                            {isConfirmed && !isCompleted && (
                              <Button
                                size="sm"
                                className="bg-green-600 hover:bg-green-700 h-7 text-xs w-full"
                                onClick={() => handleApprove(v.id)}
                              >
                                <CheckCircle className="w-3 h-3 mr-1" />{" "}
                                Zatwierdź
                              </Button>
                            )}
                          </>
                        )}

                        {/* REVIEW BUTTON: Strictly Org only */}
                        {canReview && (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 text-xs w-full justify-start px-0 hover:bg-transparent hover:text-blue-600"
                            onClick={() => handleReview(v.id)}
                          >
                            <Star className="w-3 h-3 mr-1" /> Dodaj recenzję
                          </Button>
                        )}

                        {!isOrg && isCompleted && (
                          <span className="text-[10px] text-gray-400">
                            Recenzje: Tylko Org
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
