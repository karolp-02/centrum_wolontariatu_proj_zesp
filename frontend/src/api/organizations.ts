import api from "./axios";
import { mapProjektFromApi } from "./mappers";

export async function getOrganizations(): Promise<Organizacja[]> {
  const res = await api.get("organizations/");
  const items = Array.isArray(res.data) ? res.data : res.data?.results || [];
  return items as Organizacja[];
}

export async function getOrganizationById(
  id: number,
): Promise<Organizacja | undefined> {
  const res = await api.get(`organizations/${id}/`);
  return res.data as Organizacja;
}

// Connects to @action projekty
export async function getOrganizationProjects(
  orgId: number,
): Promise<Projekt[]> {
  const res = await api.get(`organizations/${orgId}/projekty/`);
  const items = Array.isArray(res.data) ? res.data : [];
  return items.map(mapProjektFromApi);
}
