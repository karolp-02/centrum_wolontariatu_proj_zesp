import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useLocation, useNavigate } from "react-router-dom";
import { getProjects } from "@/api/projects";
import { getUsers } from "@/api/users";
import { createOffer } from "@/api/offers";
import { AutoForm } from "@/components/ui/autoform";
import { SubmitButton } from "@/components/ui/autoform/components/SubmitButton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { ZodProvider, fieldConfig } from "@autoform/zod";
import z from "zod";

const offerSchema = z.object({
  tytul_oferty: z
    .string()
    .min(1)
    .max(255)
    .superRefine(
      fieldConfig({
        label: "Tytuł oferty",
        inputProps: { placeholder: "Tytuł" },
      }),
    ),
  lokalizacja: z
    .string()
    .min(1)
    .superRefine(
      fieldConfig({
        label: "Lokalizacja",
        inputProps: { placeholder: "np. Kraków" },
      }),
    ),
  data: z
    .string()
    .optional()
    .superRefine(
      fieldConfig({
        label: "Data",
        inputProps: { placeholder: "RRRR-MM-DD", type: "date" },
      }),
    ),
  tematyka: z
    .string()
    .optional()
    .superRefine(
      fieldConfig({
        label: "Tematyka",
        inputProps: { placeholder: "Wybierz" },
        fieldType: "select",
        options: [
          { label: "Edukacja", value: "Edukacja" },
          { label: "Ekologia", value: "Ekologia" },
          { label: "Opieka nad zwierzętami", value: "Opieka nad zwierzętami" },
          { label: "Pomoc społeczna", value: "Pomoc społeczna" },
          { label: "Kultura", value: "Kultura" },
          { label: "Sport", value: "Sport" },
          { label: "Inne", value: "Inne" },
        ],
      }),
    ),
  czas_trwania: z
    .string()
    .optional()
    .superRefine(
      fieldConfig({
        label: "Czas trwania",
        inputProps: { placeholder: "Wybierz" },
        fieldType: "select",
        options: [
          { label: "Jednorazowo", value: "Jednorazowo" },
          { label: "1-2 godziny", value: "1-2 godziny" },
          { label: "3-5 godzin", value: "3-5 godzin" },
          { label: "Weekend", value: "Weekend" },
          { label: "Długoterminowo", value: "Długoterminowo" },
          { label: "Elastycznie", value: "Elastycznie" },
        ],
      }),
    ),
  wymagania: z
    .string()
    .optional()
    .superRefine(
      fieldConfig({
        label: "Wymagania (Opis)",
        fieldType: "textarea",
        inputProps: { placeholder: "Opisz wymagania i szczegóły oferty..." },
      }),
    ),
});
const provider = new ZodProvider(offerSchema);

export default function OrganizationOffersCreatePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [projects, setProjects] = useState<Projekt[]>([]);

  useEffect(() => {
    getProjects().then(setProjects);
  }, []);

  const optionsProjects: [string, string][] = useMemo(() => {
    const rawOrg = (user as any)?.organizacja;
    const orgId: number | null = rawOrg
      ? typeof rawOrg === "number"
        ? (rawOrg as number)
        : (rawOrg.id as number)
      : null;
    const list = orgId
      ? projects.filter((p) => p.organizacja.id === orgId)
      : projects;
    return list.map((p) => [String(p.id), p.nazwa_projektu]);
  }, [projects, user]);

  if (!user?.organizacja) return <div>Brak uprawnień</div>;

  const preselectProject = (() => {
    const sp = new URLSearchParams(location.search);
    const pid = sp.get("project");
    return pid ? String(Number(pid)) : "";
  })();

  return (
    <Card>
      <CardHeader className="text-lg font-semibold">Dodaj ofertę</CardHeader>
      <CardContent>
        <AutoForm
          schema={provider}
          fieldOptions={{
            projekt_id: { options: optionsProjects },
          }}
          defaultValues={{
            tytul_oferty: "",
            lokalizacja: "",
            data: "",
            tematyka: "",
            czas_trwania: "",
            wymagania: "",
          }}
          onSubmit={async (data) => {
            try {
              await createOffer({
                projekt: Number(preselectProject),
                tytul_oferty: data.tytul_oferty,
                lokalizacja: data.lokalizacja,
                data: data.data || undefined,
                tematyka: data.tematyka || undefined,
                czas_trwania: data.czas_trwania || undefined,
                wymagania: data.wymagania || undefined,
              });
            } finally {
              navigate(`/organization/projects/${preselectProject}`);
            }
          }}
        >
          <SubmitButton>Zapisz</SubmitButton>
        </AutoForm>
      </CardContent>
    </Card>
  );
}
