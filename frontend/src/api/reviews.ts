import api from "./axios";

export async function getReviewsByVolunteer(
  volunteerId: number,
): Promise<Recenzja[]> {
  const res = await api.get("reviews/", {
    params: { wolontariusz: volunteerId },
  });
  const items = Array.isArray(res.data) ? res.data : res.data?.results || [];
  return items as Recenzja[];
}

export async function createReview(payload: {
  oferta: number;
  ocena: number;
  komentarz?: string;
  wolontariusz?: number; // Optional if backend infers it from Oferta
}): Promise<Recenzja> {
  const res = await api.post("reviews/", payload);
  return res.data as Recenzja;
}

export async function updateReview(
  id: number,
  payload: {
    ocena?: number;
    komentarz?: string;
  },
): Promise<Recenzja> {
  const res = await api.patch(`reviews/${id}/`, payload);
  return res.data as Recenzja;
}

export async function deleteReview(id: number): Promise<void> {
  await api.delete(`reviews/${id}/`);
}
