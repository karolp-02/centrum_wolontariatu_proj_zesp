import React, { useMemo, useState } from "react";
import {
  Calendar,
  dateFnsLocalizer,
  View,
  Event as RBCEvent,
} from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button"; // Added Button
import { Link } from "react-router-dom"; // Added Link
import { useAuth } from "@/hooks/useAuth"; // Added useAuth
import {
  addHours,
  format,
  parse,
  startOfWeek,
  getDay,
  parseISO,
  isValid,
} from "date-fns";
import pl from "date-fns/locale/pl";

type OfferCalendarProps = {
  offers: Oferta[];
  defaultView?: View;
  className?: string;
};

const locales = {
  pl,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

type EventType = RBCEvent & { resource: Oferta };
type ToolbarProps = {
  label: string;
  onNavigate: (
    action: "PREV" | "NEXT" | "TODAY" | "DATE",
    newDate?: Date,
  ) => void;
};

export default function OfferCalendar({
  offers,
  defaultView = "month",
  className,
}: OfferCalendarProps) {
  const [selected, setSelected] = useState<Oferta | null>(null);
  const { user } = useAuth(); // Get current user

  const events: EventType[] = useMemo(() => {
    return (offers || []).map((o) => {
      const dateStr = o.data ? `${o.data}` : undefined;
      let start = dateStr ? parseISO(dateStr) : new Date();
      if (!isValid(start)) {
        try {
          start = parse(dateStr ?? "", "yyyy-MM-dd", new Date());
        } catch {
          start = new Date();
        }
      }
      const end = addHours(start, 1);
      return {
        title: o.tytul_oferty,
        start,
        end,
        allDay: true,
        resource: o,
      } as EventType;
    });
  }, [offers]);

  const messages = useMemo(
    () => ({
      date: "Data",
      time: "Czas",
      event: "Wydarzenie",
      allDay: "Cały dzień",
      week: "Tydzień",
      work_week: "Tydzień roboczy",
      day: "Dzień",
      month: "Miesiąc",
      previous: "Poprzedni",
      next: "Następny",
      yesterday: "Wczoraj",
      tomorrow: "Jutro",
      today: "Dziś",
      agenda: "Agenda",
      noEventsInRange: "Brak wydarzeń w tym zakresie",
      showMore: (total: number) => `Pokaż więcej (+${total})`,
    }),
    [],
  );

  // Determine link based on role
  const getOfferLink = (id: number) => {
    if (user?.rola === "organizacja" || user?.rola === "koordynator") {
      return `/organization/offers/${id}`;
    }
    return `/volunteer/offers/${id}`;
  };

  const CustomToolbar = ({ label, onNavigate }: ToolbarProps) => (
    <div className="rbc-toolbar">
      <span className="rbc-btn-group">
        <button type="button" onClick={() => onNavigate("PREV")}>
          Poprzedni
        </button>
        <button type="button" onClick={() => onNavigate("TODAY")}>
          Dzisiaj
        </button>
        <button type="button" onClick={() => onNavigate("NEXT")}>
          Następny
        </button>
      </span>
      <span className="rbc-toolbar-label">{label}</span>
    </div>
  );

  const CustomEvent = (props: any) => {
    const event = props.event as EventType;
    return <span>{event.title}</span>;
  };

  return (
    <div className={className}>
      <Calendar
        culture="pl"
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 520 }}
        defaultView={defaultView}
        views={["month"]}
        popup
        messages={messages}
        components={{
          toolbar: CustomToolbar as any,
          event: CustomEvent as any,
        }}
        onSelectEvent={(e) => {
          const ev = e as EventType;
          setSelected(ev.resource);
        }}
      />
      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setSelected(null)}
          />
          <Card className="relative z-10 w-[92vw] max-w-xl p-6 shadow-xl">
            <div className="flex items-start justify-between gap-4 mb-4">
              <h3 className="text-xl font-bold">{selected.tytul_oferty}</h3>
              <button
                className="text-2xl text-gray-500 hover:text-black leading-none"
                onClick={() => setSelected(null)}
              >
                &times;
              </button>
            </div>

            <div className="space-y-2 text-sm text-gray-700">
              {selected.organizacja?.nazwa_organizacji && (
                <div className="flex gap-2">
                  <span className="font-semibold w-24 shrink-0">
                    Organizacja:
                  </span>
                  <span>{selected.organizacja.nazwa_organizacji}</span>
                </div>
              )}
              {selected.data && (
                <div className="flex gap-2">
                  <span className="font-semibold w-24 shrink-0">Data:</span>
                  <span>
                    {format(parseISO(selected.data), "PPP", { locale: pl })}
                  </span>
                </div>
              )}
              {selected.lokalizacja && (
                <div className="flex gap-2">
                  <span className="font-semibold w-24 shrink-0">
                    Lokalizacja:
                  </span>
                  <span>{selected.lokalizacja}</span>
                </div>
              )}
              {selected.tematyka && (
                <div className="flex gap-2">
                  <span className="font-semibold w-24 shrink-0">Tematyka:</span>
                  <span>{selected.tematyka}</span>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setSelected(null)}>
                Zamknij
              </Button>
              <Button asChild>
                <Link to={getOfferLink(selected.id)}>Zobacz szczegóły</Link>
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
