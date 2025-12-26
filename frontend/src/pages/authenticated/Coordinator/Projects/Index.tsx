import { useEffect, useState } from "react";
import { getProjects } from "@/api/projects";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function CoordinatorProjectsPage() {
  const [projects, setProjects] = useState<Projekt[]>([]);

  useEffect(() => {
    getProjects().then(setProjects);
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">
          Projekty (Panel Koordynatora)
        </h1>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((p) => (
          <Card key={p.id} className="p-4 flex flex-col gap-2">
            <h3 className="font-semibold text-lg">{p.nazwa_projektu}</h3>
            <div className="text-sm text-gray-500">
              {p.organizacja.nazwa_organizacji}
            </div>
            <p className="text-sm text-gray-700 line-clamp-3 flex-1">
              {p.opis_projektu}
            </p>
            <div className="mt-2 text-xs text-gray-500">
              Liczba ofert: {p.oferty_count ?? 0}
            </div>

            {/* Directs to the Project Details page, where the Offers list is located */}
            <Button asChild variant="outline" className="mt-2">
              <Link to={`/organization/projects/${p.id}`}>Zobacz oferty</Link>
            </Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
