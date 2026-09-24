const SESSION_KEY = "sga.session";

export type UsuarioSessao = {
  id: number;
  nome: string;
  email: string;
  perfil: string;
  rede_id: number;
  escola_id: number | null;
};

export type Sessao = {
  access_token: string;
  token_type: string;
  expires_in: number;
  usuario: UsuarioSessao;
};

export function getSession(): Sessao | null {
  const raw = localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Sessao;
  } catch {
    localStorage.removeItem(SESSION_KEY);
    return null;
  }
}

export function setSession(session: Sessao) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export function canManageRecords(perfil: string) {
  return ["administrador", "gestor", "diretor", "secretaria"].includes(perfil);
}
