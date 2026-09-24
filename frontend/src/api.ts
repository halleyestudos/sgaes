import { clearSession, getSession } from "./auth";

const fieldLabels: Record<string, string> = {
  nome: "Nome",
  codigo_inep: "Código INEP",
  serie: "Série",
  turno: "Turno",
  escola_id: "Escola",
  ano_letivo_id: "Ano letivo",
  aluno_id: "Aluno",
  turma_id: "Turma",
  email: "E-mail",
  senha: "Senha",
  itens: "Itens da chamada",
  bairro: "Bairro",
  telefone: "Telefone",
};

function readDetail(data: unknown): string | null {
  if (typeof data !== "object" || data === null || !("detail" in data)) return null;
  const detail = (data as { detail: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const parts = detail.map((item) => {
      if (typeof item !== "object" || item === null) return String(item);
      const loc = "loc" in item && Array.isArray(item.loc) ? item.loc.filter((part: unknown) => part !== "body" && part !== "query") : [];
      const field = loc.length ? fieldLabels[String(loc[0])] || String(loc[0]) : "";
      const msg = "msg" in item && typeof item.msg === "string" ? item.msg : "valor inválido";
      if (msg.includes("at least")) {
        const digits = msg.match(/\d+/);
        return field ? `${field} precisa ter pelo menos ${digits?.[0] ?? "2"} caracteres.` : msg;
      }
      return field ? `${field}: ${msg}` : msg;
    });
    return parts.join(" ");
  }
  return null;
}

const api = async <T>(path: string, options?: RequestInit): Promise<T> => {
  const session = getSession();
  const headers = new Headers(options?.headers);
  if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (session?.access_token) headers.set("Authorization", `Bearer ${session.access_token}`);

  let response: Response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch {
    throw new Error("Não foi possível conectar à API. Confirme se o backend está em http://127.0.0.1:8000.");
  }
  const body = await response.text();
  let data: unknown = null;
  if (body.trim()) {
    try {
      data = JSON.parse(body);
    } catch {
      data = null;
    }
  }
  if (response.status === 401 && !path.includes("/auth/login")) {
    clearSession();
    window.dispatchEvent(new Event("sga:unauthorized"));
  }
  if (!response.ok) {
    throw new Error(readDetail(data) || `Servidor retornou HTTP ${response.status}.`);
  }
  return data as T;
};

export type Student = { aluno_id: number; nome: string; aulas: number; presencas: number; faltas: number; percentual: string; nivel_alerta: string | null };
export type DayAttendance = { aluno_id: number; nome: string; presente: boolean; observacao: string | null; registrada: boolean };
export type Alert = { id: number; aluno_id: number; ano_letivo_id: number; nivel: string; percentual: string; resolvido: boolean };
export type Aluno = {
  id: number;
  nome: string;
  nome_social?: string | null;
  data_nascimento?: string | null;
  sexo?: string | null;
  cor_raca?: string | null;
  naturalidade_cidade?: string | null;
  naturalidade_uf?: string | null;
  telefone?: string | null;
  email?: string | null;
  nome_mae?: string | null;
  nome_pai?: string | null;
  endereco?: string | null;
  numero?: string | null;
  complemento?: string | null;
  bairro?: string | null;
  cidade?: string | null;
  uf?: string | null;
  cep?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  modal_transporte?: string | null;
  distancia_metros?: number | null;
  tempo_deslocamento_min?: number | null;
  metodo_distancia?: string | null;
  acesso_internet?: boolean | null;
  acesso_materiais?: boolean | null;
  necessidades_especiais?: string | null;
  dados_anonimizados?: boolean;
  ativo: boolean;
  rede_id: number;
};
export type AlunoPayload = Partial<Omit<Aluno, "id" | "rede_id" | "distancia_metros" | "tempo_deslocamento_min" | "metodo_distancia" | "dados_anonimizados">> & { nome: string; ativo?: boolean };
export type AlunoTurma = { aluno_id: number; nome: string; matricula_id: number; status: string };
export type MatriculaAtiva = {
  matricula_id: number;
  aluno_id: number;
  aluno_nome: string;
  turma_id: number;
  turma_nome: string;
  ano_letivo_id: number;
  status: string;
};
export type Escola = {
  id: number;
  nome: string;
  codigo_inep: string | null;
  dependencia_administrativa?: string | null;
  telefone?: string | null;
  email?: string | null;
  endereco?: string | null;
  bairro?: string | null;
  cidade?: string | null;
  uf?: string | null;
  cep?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  ativo: boolean;
  rede_id: number;
};
export type EscolaPayload = Partial<Omit<Escola, "id" | "rede_id">> & { nome: string; ativo?: boolean };
export type AnoLetivo = { id: number; nome: string; ativo: boolean; rede_id: number };
export type Turma = {
  id: number;
  nome: string;
  serie: string | null;
  turno: string | null;
  professor_id?: number | null;
  oferece_merenda?: boolean;
  apoio_pedagogico?: boolean;
  ativa: boolean;
  rede_id: number;
  escola_id: number;
  ano_letivo_id: number;
};
export type AuthResponse = { access_token: string; token_type: string; expires_in: number; usuario: { id: number; nome: string; email: string; perfil: string; rede_id: number; escola_id: number | null } };
export type Responsavel = { id: number; aluno_id: number; nome: string; parentesco: string | null; telefone: string | null; email: string | null; principal: boolean };
export type HistoricoEscolar = { id: number; aluno_id: number; nome_escola: string; codigo_inep: string | null; ano: number | null; serie: string | null; ultima_escola: boolean; observacao: string | null };
export type Consentimento = { id: number; aluno_id: number; tipo: string; finalidade: string | null; concedido: boolean; data_registro: string };
export type EstatisticasRede = { escolas_ativas: number; turmas_ativas: number; alunos_ativos: number; professores: number; frequencia_media_rede: number | null };
export type Professor = { id: number; nome: string; email: string; escola_id: number | null; perfil: string };
export type AmbienteBairro = { bairro: string; alunos: number; frequencia_media: number | null; com_internet: number; com_materiais: number; detalhes: Array<Record<string, unknown>> };
export type CorrelacaoGeo = { amostra: number; correlacao_pearson_distancia_faltas: number | null; itens: Array<Record<string, unknown>> };
export type DeslocamentoResult = {
  aluno_id: number;
  escola_id: number;
  escola_nome?: string;
  origem: { latitude: number; longitude: number };
  destino: { latitude: number; longitude: number };
  distancia_metros: number;
  tempo_deslocamento_min: number;
  metodo: string;
  modal?: string;
  geometria?: number[][];
  mapa_osm_url?: string;
};
export type ModuloFuturo = { codigo: string; titulo: string; descricao: string; status: string };

export const login = (email: string, senha: string) => api<AuthResponse>("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ email, senha }) });
export const getClassSummary = (turmaId: number) => api<Student[]>(`/api/v1/frequencia/turma/${turmaId}/consolidado`);
export const getDayAttendance = (turmaId: number, data: string, ordem = 1) => api<DayAttendance[]>(`/api/v1/frequencia/turma/${turmaId}/chamada?data=${data}&ordem=${ordem}`);
export const getAlerts = () => api<Alert[]>("/api/v1/frequencia/busca-ativa");
export const sendAttendance = (payload: unknown) => api<unknown[]>("/api/v1/frequencia/chamada", { method: "POST", body: JSON.stringify(payload) });
export const getStudents = () => api<Aluno[]>("/api/v1/alunos?limit=200");
export const getClassStudents = (turmaId: number) => api<AlunoTurma[]>(`/api/v1/matriculas/turma/${turmaId}/alunos`);
export const getActiveEnrollments = (anoLetivoId?: number) =>
  api<MatriculaAtiva[]>(`/api/v1/matriculas/ativas${anoLetivoId != null ? `?ano_letivo_id=${anoLetivoId}` : ""}`);
export const getSchools = () => api<Escola[]>("/api/v1/escolas?limit=200");
export const getSchoolYears = () => api<AnoLetivo[]>("/api/v1/anos-letivos?limit=200");
export const getClasses = () => api<Turma[]>("/api/v1/turmas?limit=200");
export const createStudent = (payload: AlunoPayload) => api<Aluno>("/api/v1/alunos", { method: "POST", body: JSON.stringify({ ativo: true, ...payload }) });
export const createSchool = (payload: EscolaPayload) => api<Escola>("/api/v1/escolas", { method: "POST", body: JSON.stringify({ ativo: true, ...payload }) });
export const createSchoolYear = (nome: string) => api<AnoLetivo>("/api/v1/anos-letivos", { method: "POST", body: JSON.stringify({ nome, ativo: true }) });
export const createClass = (payload: { nome: string; serie?: string; turno?: string; escola_id: number; ano_letivo_id: number; professor_id?: number | null; oferece_merenda?: boolean; apoio_pedagogico?: boolean }) =>
  api<Turma>("/api/v1/turmas", { method: "POST", body: JSON.stringify({ ...payload, serie: payload.serie || null, turno: payload.turno || null, ativa: true }) });
export const updateStudent = (id: number, payload: Partial<AlunoPayload>) => api<Aluno>(`/api/v1/alunos/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const updateSchool = (id: number, payload: Partial<EscolaPayload>) => api<Escola>(`/api/v1/escolas/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const updateSchoolYear = (id: number, payload: { nome?: string; ativo?: boolean }) => api<AnoLetivo>(`/api/v1/anos-letivos/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const updateClass = (id: number, payload: Partial<Turma>) => api<Turma>(`/api/v1/turmas/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const enrollStudent = (alunoId: number, turmaId: number, anoLetivoId: number) => api<unknown>("/api/v1/matriculas", { method: "POST", body: JSON.stringify({ aluno_id: alunoId, turma_id: turmaId, ano_letivo_id: anoLetivoId }) });
export const transferEnrollment = (matriculaId: number, novaTurmaId: number, motivo?: string) => api<unknown>(`/api/v1/matriculas/${matriculaId}/transferir`, { method: "PUT", body: JSON.stringify({ nova_turma_id: novaTurmaId, motivo: motivo || "Transferência de turma" }) });
export const endEnrollment = (matriculaId: number, motivo: string) => api<unknown>(`/api/v1/matriculas/${matriculaId}/encerrar`, { method: "PUT", body: JSON.stringify({ motivo }) });

export const getResponsaveis = (alunoId: number) => api<Responsavel[]>(`/api/v1/responsaveis?aluno_id=${alunoId}`);
export const createResponsavel = (payload: { aluno_id: number; nome: string; parentesco?: string; telefone?: string; principal?: boolean }) =>
  api<Responsavel>("/api/v1/responsaveis", { method: "POST", body: JSON.stringify(payload) });
export const getHistoricos = (alunoId: number) => api<HistoricoEscolar[]>(`/api/v1/historicos-escolares?aluno_id=${alunoId}`);
export const createHistorico = (payload: { aluno_id: number; nome_escola: string; codigo_inep?: string; ano?: number; serie?: string; ultima_escola?: boolean }) =>
  api<HistoricoEscolar>("/api/v1/historicos-escolares", { method: "POST", body: JSON.stringify(payload) });
export const calcularDeslocamento = (alunoId: number, modal?: string) =>
  api<DeslocamentoResult>("/api/v1/geo/deslocamento", { method: "POST", body: JSON.stringify({ aluno_id: alunoId, modal_transporte: modal || null, persistir: true }) });
export const getCorrelacaoGeo = () => api<CorrelacaoGeo>("/api/v1/geo/correlacao-faltas");
export const getEstatisticas = () => api<EstatisticasRede>("/api/v1/gestao/estatisticas");
export const getProfessores = () => api<Professor[]>("/api/v1/gestao/professores");
export const getAmbienteBairro = (bairro?: string) => api<AmbienteBairro[]>(`/api/v1/gestao/ambiente-bairro${bairro ? `?bairro=${encodeURIComponent(bairro)}` : ""}`);
export const createConsentimento = (payload: { aluno_id: number; tipo?: string; finalidade?: string; concedido?: boolean }) =>
  api<Consentimento>("/api/v1/lgpd/consentimentos", { method: "POST", body: JSON.stringify(payload) });
export const getConsentimentos = (alunoId: number) => api<Consentimento[]>(`/api/v1/lgpd/consentimentos?aluno_id=${alunoId}`);
export const getAlunoMascarado = (alunoId: number) => api<Record<string, unknown>>(`/api/v1/lgpd/alunos/${alunoId}/mascarado`);
export const anonimizarAluno = (alunoId: number) => api<Record<string, unknown>>(`/api/v1/lgpd/alunos/${alunoId}/anonimizar`, { method: "POST", body: JSON.stringify({ confirmar: true }) });
export const getModulosFuturos = () => api<ModuloFuturo[]>("/api/v1/modulos-futuros");
