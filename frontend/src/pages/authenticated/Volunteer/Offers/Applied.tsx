import { useEffect, useMemo, useState } from "react";
import { getMyOffers } from "@/api/offers";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { downloadOfferCertificate } from "@/api/offers";
import { useAuth } from "@/hooks/useAuth";

export default function VolunteerAppliedOffersPage() {
  const { user } = useAuth();
  const [offers, setOffers] = useState<Oferta[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyOffers().then((os) => {
      setOffers(os);
      setLoading(false);
    });
  }, []);

  // Helper to find MY status in the offer's volunteer list
  const getMyStatus = (o: Oferta) => {
    if (!user) return { confirmed: false, completed: false };

    // Check the specific list first
    if (o.wolontariusze && Array.isArray(o.wolontariusze)) {
      const me = o.wolontariusze.find((v) => v.id === user.id);
      if (me) {
        return {
          confirmed: me.czy_potwierdzone ?? false,
          completed: me.czy_ukonczone ?? false,
        };
      }
    }

    // Fallback for single assignment legacy
    if (o.wolontariusz && o.wolontariusz.id === user.id) {
      // If single assigned, usually means confirmed. Completion is global.
      return { confirmed: true, completed: o.czy_ukonczone };
    }

    return { confirmed: false, completed: false };
  };

  const sorted = useMemo(() => {
    return [...offers].sort((a, b) => {
      const statusA = getMyStatus(a);
      const statusB = getMyStatus(b);
      // Sort: Completed -> Confirmed -> Applied
      const scoreA = (statusA.completed ? 2 : 0) + (statusA.confirmed ? 1 : 0);
      const scoreB = (statusB.completed ? 2 : 0) + (statusB.confirmed ? 1 : 0);
      return scoreB - scoreA;
    });
  }, [offers, user]);

  if (loading) return <div>Ładowanie…</div>;

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Zgłoszone oferty</h1>

      <Card className="p-4">
        {sorted.length === 0 ? (
          <div className="text-sm text-gray-600">Brak zgłoszonych ofert.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-gray-600 border-b">
                  <th className="py-2 pr-3">Tytuł</th>
                  <th className="py-2 pr-3">Organizacja</th>
                  <th className="py-2 pr-3">Data</th>
                  <th className="py-2 pr-3">Twój Status</th>
                  <th className="py-2 pr-3">Akcje</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((o) => {
                  const { confirmed, completed } = getMyStatus(o);

                  return (
                    <tr key={o.id} className="border-b last:border-0">
                      <td className="py-3 pr-3 font-medium">
                        {o.tytul_oferty}
                      </td>
                      <td className="py-3 pr-3 text-gray-600">
                        {o.organizacja.nazwa_organizacji}
                      </td>
                      <td className="py-3 pr-3">
                        {o.data
                          ? new Date(o.data + "T00:00:00").toLocaleDateString(
                              "pl-PL",
                            )
                          : "—"}
                      </td>
                      <td className="py-3 pr-3">
                        {completed ? (
                          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            Ukończono
                          </span>
                        ) : confirmed ? (
                          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                            Potwierdzony
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                            Oczekuje
                          </span>
                        )}
                      </td>
                      <td className="py-3 pr-3">
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={!completed}
                          onClick={async () => {
                            try {
                              await downloadOfferCertificate(o.id);
                            } catch (err: any) {
                              alert("Nie udało się pobrać certyfikatu.");
                            }
                          }}
                        >
                          Pobierz certyfikat
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </section>
  );
}
