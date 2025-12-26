// Temporary mock-backed API with TODOs for real endpoints
import api from "./axios";
import { mockUzytkownicy } from "@/mock-data/data";

export async function getUsers(): Promise<Uzytkownik[]> {
  try {
    // Tries to fetch real data from backend
    const res = await api.get("volunteers/volunteers/");
    const items = Array.isArray(res.data) ? res.data : res.data?.results || [];
    return items as Uzytkownik[];
  } catch {
    // Fallback to mock data
    console.warn("Failed to fetch users, using mock data");
    return Promise.resolve(mockUzytkownicy);
  }
}

export async function getUserById(id: number): Promise<Uzytkownik | undefined> {
  try {
    const res = await api.get(`volunteers/${id}/`);
    return res.data as Uzytkownik;
  } catch {
    return Promise.resolve(mockUzytkownicy.find((u) => u.id === id));
  }
}

export async function findUserByUsername(
  username: string,
): Promise<Uzytkownik | undefined> {
  // TODO: replace with a server-side lookup
  return Promise.resolve(mockUzytkownicy.find((u) => u.username === username));
}

export async function getCurrentProfile(): Promise<Uzytkownik | null> {
  try {
    const res = await api.get("volunteers/me/");
    return res.data as Uzytkownik;
  } catch {
    return null;
  }
}

export async function downloadVolunteerCertificate(
  volunteerId: number,
  volunteerName: string,
): Promise<void> {
  const res = await api.get(`volunteers/${volunteerId}/certificate/`, {
    responseType: "blob",
  });
  const blob = new Blob([res.data], { type: "application/pdf" });

  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `certificate_${volunteerName}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
