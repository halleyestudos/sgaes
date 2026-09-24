import { useEffect, useState, type FormEvent } from "react";
import {
  calcularDeslocamento,
  getAlerts,
  getAmbienteBairro,
  getCorrelacaoGeo,
  getEstatisticas,
  getModulosFuturos,
  getProfessores,
  type Alert,
  type AmbienteBairro,
  type CorrelacaoGeo,
  type DeslocamentoResult,
  type EstatisticasRede,
  type ModuloFuturo,
  type Professor,
  type Student,
} from "./api";
import MapaRota from "./MapaRota";

type Props = {
  students: Student[];
  onToast: (message: string) => void;
};

export default function PainelGestao({ students, onToast }: Props) {
  const [stats, setStats] = useState<EstatisticasRede | null>(null);
  const [professores, setProfessores] = useState<Professor[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [ambiente, setAmbiente] = useState<AmbienteBairro[]>([]);
  const [correlacao, setCorrelacao] = useState<CorrelacaoGeo | null>(null);
  const [futuros, setFuturos] = useState<ModuloFuturo[]>([]);
  const [bairroFiltro, setBairroFiltro] = useState("");
  const [avisoFuturo, setAvisoFuturo] = useState("");
  const [rotaAluno, setRotaAluno] = useState<{ nome: string; result: DeslocamentoResult } | null>(null);
  const [carregandoRota, setCarregandoRota] = useState<number | null>(null);

  const carregar = async () => {
    try {
      const [s, p, a, amb, corr, fut] = await Promise.all([
        getEstatisticas(),
        getProfessores(),
        getAlerts(),
        getAmbienteBairro(),
        getCorrelacaoGeo(),
        getModulosFuturos(),
      ]);
      setStats(s);
      setProfessores(p);
      setAlerts(a);
      setAmbiente(amb);
      setCorrelacao(corr);
      setFuturos(fut);
    } catch (error) {
      onToast(error instanceof Error ? error.message : "Falha ao carregar o painel gestor.");
    }
  };

  useEffect(() => {
    void carregar();
  }, []);

  const filtrarBairro = async (event: FormEvent) => {
    event.preventDefault();
    try {
      setAmbiente(await getAmbienteBairro(bairroFiltro.trim() || undefined));
    } catch (error) {
      onToast(error instanceof Error ? error.message : "Falha ao filtrar bairro.");
    }
  };

  async function verTrajetoria(alunoId: number, nome: string) {
    setCarregandoRota(alunoId);
    try {
      const result = await calcularDeslocamento(alunoId);
      setRotaAluno({ nome, result });
    } catch (error) {
      onToast(error instanceof Error ? error.message : "Não foi possível carregar a trajetória.");
    } finally {
      setCarregandoRota(null);
    }
  }

  return (
    <section className="workspace gestao-workspace">
      <div className="section-heading">
        <div>
          <span className="eyebrow">VISÃO DA REDE</span>
          <h2>Painel gestor</h2>
          <p>Secretaria, professores, frequência, deslocamento e contexto por bairro.</p>
        </div>
      </div>

      <div className="metrics metrics-wide">
        <div><strong>{stats?.escolas_ativas ?? "—"}</strong><span>escolas ativas</span></div>
        <div><strong>{stats?.turmas_ativas ?? "—"}</strong><span>turmas ativas</span></div>
        <div><strong>{stats?.alunos_ativos ?? "—"}</strong><span>alunos ativos</span></div>
        <div><strong>{stats?.professores ?? "—"}</strong><span>professores</span></div>
        <div><strong>{stats?.frequencia_media_rede != null ? `${stats.frequencia_media_rede}%` : "—"}</strong><span>frequência da rede</span></div>
        <div><strong>{students.length ? Math.round(students.reduce((sum, item) => sum + Number(item.percentual), 0) / students.length) : 0}%</strong><span>turma selecionada</span></div>
      </div>

      <div className="gestao-grid">
        <article className="form-panel">
          <h3>Professores</h3>
          {professores.length === 0 ? <p className="empty">Nenhum professor cadastrado.</p> : (
            <ul className="plain-list">
              {professores.map((item) => (
                <li key={item.id}><strong>{item.nome}</strong><small>{item.email}</small></li>
              ))}
            </ul>
          )}
        </article>

        <article className="form-panel">
          <h3>Busca ativa</h3>
          {alerts.length === 0 ? <p className="empty">Nenhum alerta aberto.</p> : alerts.map((alert) => (
            <div className="alert-row" key={alert.id}>
              <span>
                <strong>Aluno {alert.aluno_id}</strong>
                <small>{alert.nivel === "LIMITE_LEGAL_30" ? "Abaixo do limite legal" : "Risco de abandono"}</small>
              </span>
              <b>{alert.percentual}%</b>
            </div>
          ))}
        </article>

        <article className="form-panel">
          <h3>Deslocamento × faltas</h3>
          <p className="form-hint">
            Correlação Pearson: {correlacao?.correlacao_pearson_distancia_faltas ?? "sem amostra suficiente"}
            {correlacao ? ` · ${correlacao.amostra} aluno(s) com distância` : ""}
          </p>
          <ul className="plain-list compact">
            {(correlacao?.itens || []).slice(0, 8).map((item) => {
              const alunoId = Number(item.aluno_id);
              const nome = String(item.nome);
              return (
                <li key={String(item.aluno_id)} className="correlacao-row">
                  <div>
                    <strong>{nome}</strong>
                    <small>
                      {item.distancia_metros != null ? `${Math.round(Number(item.distancia_metros))} m` : "—"}
                      {" · "}
                      {item.tempo_deslocamento_min != null ? `${item.tempo_deslocamento_min} min` : "—"}
                      {" · faltas "}
                      {String(item.percentual_faltas)}%
                    </small>
                  </div>
                  <button
                    className="quiet linkish"
                    type="button"
                    disabled={carregandoRota === alunoId}
                    onClick={() => void verTrajetoria(alunoId, nome)}
                  >
                    {carregandoRota === alunoId ? "Carregando…" : "Ver trajetória"}
                  </button>
                </li>
              );
            })}
          </ul>
        </article>

        <article className="form-panel">
          <h3>Ambiente e rotina por bairro</h3>
          <form className="inline-filter" onSubmit={filtrarBairro}>
            <input value={bairroFiltro} onChange={(e) => setBairroFiltro(e.target.value)} placeholder="Filtrar bairro" />
            <button className="quiet" type="submit">Comparar</button>
          </form>
          {ambiente.length === 0 ? <p className="empty">Cadastre bairro e contexto nos alunos para comparar.</p> : ambiente.map((item) => (
            <div className="bairro-card" key={item.bairro}>
              <strong>{item.bairro}</strong>
              <small>
                {item.alunos} aluno(s) · freq. média {item.frequencia_media ?? "—"}%
                · internet {item.com_internet} · materiais {item.com_materiais}
              </small>
            </div>
          ))}
        </article>
      </div>

      <div className="future-modules">
        <h3>Módulos futuros</h3>
        <p className="form-hint">Botões indicativos — implementação posterior.</p>
        <div className="future-grid">
          {futuros.map((modulo) => (
            <button
              key={modulo.codigo}
              className="future-btn"
              type="button"
              onClick={() => setAvisoFuturo(`${modulo.titulo}: em breve.`)}
            >
              <strong>{modulo.titulo}</strong>
              <span>{modulo.descricao}</span>
              <em>Em breve</em>
            </button>
          ))}
        </div>
        {avisoFuturo && <p className="feedback" role="status">{avisoFuturo}</p>}
      </div>

      {rotaAluno && (
        <div className="modal-backdrop" role="dialog" aria-modal="true" onClick={() => setRotaAluno(null)}>
          <div className="modal-card" onClick={(event) => event.stopPropagation()}>
            <div className="roster-heading">
              <h3>Trajetória — {rotaAluno.nome}</h3>
              <button className="quiet" type="button" onClick={() => setRotaAluno(null)}>Fechar</button>
            </div>
            <p className="form-hint">
              {Math.round(rotaAluno.result.distancia_metros)} m · {rotaAluno.result.tempo_deslocamento_min} min
              {" · "}{rotaAluno.result.metodo}
              {rotaAluno.result.escola_nome ? ` · ${rotaAluno.result.escola_nome}` : ""}
            </p>
            <MapaRota
              origem={rotaAluno.result.origem}
              destino={rotaAluno.result.destino}
              geometria={rotaAluno.result.geometria || []}
              altura={340}
            />
            {rotaAluno.result.mapa_osm_url && (
              <div className="mapa-actions">
                <a href={rotaAluno.result.mapa_osm_url} target="_blank" rel="noreferrer">
                  Abrir no OpenStreetMap
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
