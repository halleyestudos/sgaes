import { useEffect, useState, type FormEvent } from "react";
import {
  anonimizarAluno,
  calcularDeslocamento,
  createConsentimento,
  createHistorico,
  createResponsavel,
  createStudent,
  getAlunoMascarado,
  getConsentimentos,
  getHistoricos,
  getResponsaveis,
  getStudents,
  updateStudent,
  type Aluno,
  type Consentimento,
  type HistoricoEscolar,
  type Responsavel,
} from "./api";

const emptyForm = {
  nome: "",
  nome_social: "",
  data_nascimento: "",
  sexo: "",
  cor_raca: "",
  naturalidade_cidade: "",
  naturalidade_uf: "",
  telefone: "",
  email: "",
  nome_mae: "",
  nome_pai: "",
  endereco: "",
  numero: "",
  complemento: "",
  bairro: "",
  cidade: "",
  uf: "",
  cep: "",
  latitude: "",
  longitude: "",
  modal_transporte: "a_pe",
  acesso_internet: false,
  acesso_materiais: false,
  necessidades_especiais: "",
};

type Props = {
  onChanged?: () => void;
};

export default function AlunoCompleto({ onChanged }: Props) {
  const [alunos, setAlunos] = useState<Aluno[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [responsaveis, setResponsaveis] = useState<Responsavel[]>([]);
  const [historicos, setHistoricos] = useState<HistoricoEscolar[]>([]);
  const [consentimentos, setConsentimentos] = useState<Consentimento[]>([]);
  const [respNome, setRespNome] = useState("");
  const [respParentesco, setRespParentesco] = useState("mãe");
  const [respTelefone, setRespTelefone] = useState("");
  const [histEscola, setHistEscola] = useState("");
  const [histAno, setHistAno] = useState("");
  const [histUltima, setHistUltima] = useState(true);
  const [mascara, setMascara] = useState<Record<string, unknown> | null>(null);

  const load = async () => {
    const loaded = await getStudents();
    setAlunos(loaded);
  };

  const loadExtras = async (alunoId: number) => {
    const [r, h, c] = await Promise.all([getResponsaveis(alunoId), getHistoricos(alunoId), getConsentimentos(alunoId)]);
    setResponsaveis(r);
    setHistoricos(h);
    setConsentimentos(c);
  };

  useEffect(() => {
    void load().catch((error) => setMessage(error instanceof Error ? error.message : "Falha ao carregar alunos."));
  }, []);

  const setField = (key: keyof typeof emptyForm, value: string | boolean) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const payloadFromForm = () => ({
    nome: form.nome.trim(),
    nome_social: form.nome_social.trim() || null,
    data_nascimento: form.data_nascimento || null,
    sexo: form.sexo || null,
    cor_raca: form.cor_raca || null,
    naturalidade_cidade: form.naturalidade_cidade.trim() || null,
    naturalidade_uf: form.naturalidade_uf.trim().toUpperCase() || null,
    telefone: form.telefone.trim() || null,
    email: form.email.trim() || null,
    nome_mae: form.nome_mae.trim() || null,
    nome_pai: form.nome_pai.trim() || null,
    endereco: form.endereco.trim() || null,
    numero: form.numero.trim() || null,
    complemento: form.complemento.trim() || null,
    bairro: form.bairro.trim() || null,
    cidade: form.cidade.trim() || null,
    uf: form.uf.trim().toUpperCase() || null,
    cep: form.cep.trim() || null,
    latitude: form.latitude ? Number(form.latitude) : null,
    longitude: form.longitude ? Number(form.longitude) : null,
    modal_transporte: form.modal_transporte || null,
    acesso_internet: form.acesso_internet,
    acesso_materiais: form.acesso_materiais,
    necessidades_especiais: form.necessidades_especiais.trim() || null,
    ativo: true,
  });

  const fillFromAluno = (aluno: Aluno) => {
    setForm({
      nome: aluno.nome || "",
      nome_social: aluno.nome_social || "",
      data_nascimento: aluno.data_nascimento || "",
      sexo: aluno.sexo || "",
      cor_raca: aluno.cor_raca || "",
      naturalidade_cidade: aluno.naturalidade_cidade || "",
      naturalidade_uf: aluno.naturalidade_uf || "",
      telefone: aluno.telefone || "",
      email: aluno.email || "",
      nome_mae: aluno.nome_mae || "",
      nome_pai: aluno.nome_pai || "",
      endereco: aluno.endereco || "",
      numero: aluno.numero || "",
      complemento: aluno.complemento || "",
      bairro: aluno.bairro || "",
      cidade: aluno.cidade || "",
      uf: aluno.uf || "",
      cep: aluno.cep || "",
      latitude: aluno.latitude != null ? String(aluno.latitude) : "",
      longitude: aluno.longitude != null ? String(aluno.longitude) : "",
      modal_transporte: aluno.modal_transporte || "a_pe",
      acesso_internet: Boolean(aluno.acesso_internet),
      acesso_materiais: Boolean(aluno.acesso_materiais),
      necessidades_especiais: aluno.necessidades_especiais || "",
    });
  };

  async function submitAluno(event: FormEvent) {
    event.preventDefault();
    if (form.nome.trim().length < 2 || busy) return;
    setBusy(true);
    try {
      const payload = payloadFromForm();
      if (selectedId) {
        const updated = await updateStudent(Number(selectedId), payload);
        setAlunos((items) => items.map((item) => (item.id === updated.id ? updated : item)));
        setMessage(`Aluno ${updated.nome} atualizado.`);
      } else {
        const created = await createStudent(payload);
        setAlunos((items) => [...items, created]);
        setSelectedId(String(created.id));
        setMessage(`Aluno ${created.nome} cadastrado.`);
      }
      onChanged?.();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar aluno.");
    } finally {
      setBusy(false);
    }
  }

  async function onSelectAluno(id: string) {
    setSelectedId(id);
    setMascara(null);
    if (!id) {
      setForm(emptyForm);
      setResponsaveis([]);
      setHistoricos([]);
      setConsentimentos([]);
      return;
    }
    const aluno = alunos.find((item) => item.id === Number(id));
    if (aluno) fillFromAluno(aluno);
    await loadExtras(Number(id));
  }

  async function addResponsavel(event: FormEvent) {
    event.preventDefault();
    if (!selectedId || !respNome.trim()) return;
    const created = await createResponsavel({ aluno_id: Number(selectedId), nome: respNome.trim(), parentesco: respParentesco, telefone: respTelefone || undefined, principal: true });
    setResponsaveis((items) => [...items, created]);
    setRespNome("");
    setRespTelefone("");
    setMessage("Responsável registrado.");
  }

  async function addHistorico(event: FormEvent) {
    event.preventDefault();
    if (!selectedId || !histEscola.trim()) return;
    const created = await createHistorico({
      aluno_id: Number(selectedId),
      nome_escola: histEscola.trim(),
      ano: histAno ? Number(histAno) : undefined,
      ultima_escola: histUltima,
    });
    setHistoricos(await getHistoricos(Number(selectedId)));
    setHistEscola("");
    setHistAno("");
    setMessage(created.ultima_escola ? "Última escola registrada." : "Histórico escolar registrado.");
  }

  async function calcGeo() {
    if (!selectedId) return;
    try {
      const result = await calcularDeslocamento(Number(selectedId), form.modal_transporte);
      setMessage(`Deslocamento: ${result.distancia_metros} m · ${result.tempo_deslocamento_min} min (${result.metodo}).`);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha no cálculo de deslocamento.");
    }
  }

  async function registrarConsentimento() {
    if (!selectedId) return;
    await createConsentimento({
      aluno_id: Number(selectedId),
      tipo: "tratamento_dados_educacionais",
      finalidade: "Gestão escolar, frequência e análise agregada de deslocamento.",
      concedido: true,
    });
    setConsentimentos(await getConsentimentos(Number(selectedId)));
    setMessage("Consentimento LGPD registrado.");
  }

  async function verMascara() {
    if (!selectedId) return;
    setMascara(await getAlunoMascarado(Number(selectedId)));
  }

  async function anonimizar() {
    if (!selectedId || !window.confirm("Anonimizar dados pessoais deste aluno? Ação irreversível no cadastro.")) return;
    await anonimizarAluno(Number(selectedId));
    await load();
    const aluno = (await getStudents()).find((item) => item.id === Number(selectedId));
    if (aluno) fillFromAluno(aluno);
    setMessage("Aluno anonimizado.");
  }

  return (
    <div className="aluno-completo">
      <div className="section-heading">
        <div>
          <span className="eyebrow">CENSO / LGPD / GEO</span>
          <h2>Cadastro completo do aluno</h2>
          <p>Endereço, filiação, responsáveis, histórico escolar, deslocamento e consentimento.</p>
        </div>
      </div>

      <label className="select-aluno">
        Editar aluno existente
        <select value={selectedId} onChange={(event) => void onSelectAluno(event.target.value)}>
          <option value="">Novo aluno</option>
          {alunos.map((item) => (
            <option key={item.id} value={item.id}>{item.nome}</option>
          ))}
        </select>
      </label>

      <form className="form-panel dense-form" onSubmit={submitAluno}>
        <div className="fields-3">
          <label>Nome<input value={form.nome} onChange={(e) => setField("nome", e.target.value)} required minLength={2} /></label>
          <label>Nome social<input value={form.nome_social} onChange={(e) => setField("nome_social", e.target.value)} /></label>
          <label>Nascimento<input type="date" value={form.data_nascimento} onChange={(e) => setField("data_nascimento", e.target.value)} /></label>
          <label>Sexo
            <select value={form.sexo} onChange={(e) => setField("sexo", e.target.value)}>
              <option value="">—</option>
              <option value="F">Feminino</option>
              <option value="M">Masculino</option>
            </select>
          </label>
          <label>Cor/raça
            <select value={form.cor_raca} onChange={(e) => setField("cor_raca", e.target.value)}>
              <option value="">—</option>
              <option value="branca">Branca</option>
              <option value="preta">Preta</option>
              <option value="parda">Parda</option>
              <option value="amarela">Amarela</option>
              <option value="indigena">Indígena</option>
              <option value="nao_declarada">Não declarada</option>
            </select>
          </label>
          <label>Naturalidade<input value={form.naturalidade_cidade} onChange={(e) => setField("naturalidade_cidade", e.target.value)} placeholder="Cidade" /></label>
          <label>UF nat.<input value={form.naturalidade_uf} onChange={(e) => setField("naturalidade_uf", e.target.value)} maxLength={2} /></label>
          <label>Telefone<input value={form.telefone} onChange={(e) => setField("telefone", e.target.value)} /></label>
          <label>E-mail<input value={form.email} onChange={(e) => setField("email", e.target.value)} /></label>
          <label>Nome da mãe<input value={form.nome_mae} onChange={(e) => setField("nome_mae", e.target.value)} /></label>
          <label>Nome do pai<input value={form.nome_pai} onChange={(e) => setField("nome_pai", e.target.value)} /></label>
          <label>Endereço<input value={form.endereco} onChange={(e) => setField("endereco", e.target.value)} /></label>
          <label>Número<input value={form.numero} onChange={(e) => setField("numero", e.target.value)} /></label>
          <label>Complemento<input value={form.complemento} onChange={(e) => setField("complemento", e.target.value)} /></label>
          <label>Bairro<input value={form.bairro} onChange={(e) => setField("bairro", e.target.value)} /></label>
          <label>Cidade<input value={form.cidade} onChange={(e) => setField("cidade", e.target.value)} /></label>
          <label>UF<input value={form.uf} onChange={(e) => setField("uf", e.target.value)} maxLength={2} /></label>
          <label>CEP<input value={form.cep} onChange={(e) => setField("cep", e.target.value)} /></label>
          <label>Latitude<input value={form.latitude} onChange={(e) => setField("latitude", e.target.value)} placeholder="-15.78" /></label>
          <label>Longitude<input value={form.longitude} onChange={(e) => setField("longitude", e.target.value)} placeholder="-47.93" /></label>
          <label>Modal
            <select value={form.modal_transporte} onChange={(e) => setField("modal_transporte", e.target.value)}>
              <option value="a_pe">A pé</option>
              <option value="onibus_escolar">Ônibus escolar</option>
              <option value="transporte_publico">Transporte público</option>
              <option value="bicicleta">Bicicleta</option>
              <option value="outro">Outro</option>
            </select>
          </label>
          <label className="checkbox-label"><input type="checkbox" checked={form.acesso_internet} onChange={(e) => setField("acesso_internet", e.target.checked)} />Acesso à internet</label>
          <label className="checkbox-label"><input type="checkbox" checked={form.acesso_materiais} onChange={(e) => setField("acesso_materiais", e.target.checked)} />Acesso a materiais</label>
          <label>Necessidades especiais<input value={form.necessidades_especiais} onChange={(e) => setField("necessidades_especiais", e.target.value)} /></label>
        </div>
        <div className="action-row">
          <button className="primary" type="submit" disabled={busy}>{selectedId ? "Salvar alterações" : "Cadastrar aluno"}</button>
          {selectedId && <button className="quiet" type="button" onClick={() => void calcGeo()}>Calcular deslocamento</button>}
        </div>
      </form>

      {selectedId && (
        <div className="gestao-grid">
          <form className="form-panel" onSubmit={(e) => void addResponsavel(e).catch((err) => setMessage(err instanceof Error ? err.message : "Erro"))}>
            <h3>Responsáveis</h3>
            <label>Nome<input value={respNome} onChange={(e) => setRespNome(e.target.value)} /></label>
            <label>Parentesco<input value={respParentesco} onChange={(e) => setRespParentesco(e.target.value)} /></label>
            <label>Telefone<input value={respTelefone} onChange={(e) => setRespTelefone(e.target.value)} /></label>
            <button className="quiet" type="submit">Adicionar responsável</button>
            <ul className="plain-list">
              {responsaveis.map((item) => <li key={item.id}><strong>{item.nome}</strong><small>{item.parentesco} · {item.telefone}</small></li>)}
            </ul>
          </form>

          <form className="form-panel" onSubmit={(e) => void addHistorico(e).catch((err) => setMessage(err instanceof Error ? err.message : "Erro"))}>
            <h3>Histórico escolar</h3>
            <label>Escola anterior<input value={histEscola} onChange={(e) => setHistEscola(e.target.value)} /></label>
            <label>Ano<input value={histAno} onChange={(e) => setHistAno(e.target.value)} /></label>
            <label className="checkbox-label"><input type="checkbox" checked={histUltima} onChange={(e) => setHistUltima(e.target.checked)} />Última escola</label>
            <button className="quiet" type="submit">Registrar histórico</button>
            <ul className="plain-list">
              {historicos.map((item) => (
                <li key={item.id}>
                  <strong>{item.nome_escola}</strong>
                  <small>{item.ano ?? "—"} {item.ultima_escola ? "· última escola" : ""}</small>
                </li>
              ))}
            </ul>
          </form>

          <article className="form-panel">
            <h3>LGPD</h3>
            <div className="action-row">
              <button className="quiet" type="button" onClick={() => void registrarConsentimento().catch((e) => setMessage(e instanceof Error ? e.message : "Erro"))}>Registrar consentimento</button>
              <button className="quiet" type="button" onClick={() => void verMascara().catch((e) => setMessage(e instanceof Error ? e.message : "Erro"))}>Ver mascarado</button>
              <button className="danger-quiet quiet" type="button" onClick={() => void anonimizar().catch((e) => setMessage(e instanceof Error ? e.message : "Erro"))}>Anonimizar</button>
            </div>
            <ul className="plain-list">
              {consentimentos.map((item) => (
                <li key={item.id}><strong>{item.tipo}</strong><small>{item.concedido ? "concedido" : "negado"} · {new Date(item.data_registro).toLocaleString()}</small></li>
              ))}
            </ul>
            {mascara && <pre className="mask-preview">{JSON.stringify(mascara, null, 2)}</pre>}
          </article>
        </div>
      )}

      <p className="feedback" role="status">{message}</p>
    </div>
  );
}
