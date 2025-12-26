import api from "./axios";
import { mapProjektFromApi, mapOfertaFromApi } from "./mappers";

export async function getProjects(search?: string): Promise<Projekt[]> {
  const params: any = {};
  if (search) params.search = search;

  const res = await api.get("projects/", { params });
  const items = Array.isArray(res.data) ? res.data : res.data?.results || [];
  return items.map(mapProjektFromApi);
}

export async function getProjectById(id: number): Promise<Projekt | undefined> {
  const res = await api.get(`projects/${id}/`);
  return mapProjektFromApi(res.data);
}

export async function getProjectOffers(projectId: number): Promise<Oferta[]> {
  const res = await api.get(`projects/${projectId}/oferty/`);
  const items = Array.isArray(res.data) ? res.data : [];
  return items.map(mapOfertaFromApi);
}

export async function createProject(data: {
  nazwa_projektu: string;
  opis_projektu: string;
  organizacja?: number;
}): Promise<Projekt> {
  const res = await api.post("projects/", data);
  return mapProjektFromApi(res.data);
}

export async function updateProject(
  id: number,
  data: Partial<{
    nazwa_projektu: string;
    opis_projektu: string;
    organizacja: number;
  }>,
): Promise<Projekt> {
  const res = await api.patch(`projects/${id}/`, data);
  return mapProjektFromApi(res.data);
}

export async function deleteProject(id: number): Promise<void> {
  await api.delete(`projects/${id}/`);
}
