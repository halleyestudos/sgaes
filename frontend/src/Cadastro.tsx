import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  createClass,
  createSchool,
  createSchoolYear,
  createStudent,
  endEnrollment,
  enrollStudent,
  getActiveEnrollments,
  getClassStudents,
  getClasses,
  getSchoolYears,
  getSchools,
  getStudents,
  transferEnrollment,
  updateClass,
  updateSchool,
  updateSchoolYear,
  updateStudent,
  type Aluno,
  type AlunoTurma,
  type AnoLetivo,
  type Escola,
  type MatriculaAtiva,
  type Turma,
} from "./api";
import AlunoCompleto from "./AlunoCompleto";

type Aba = "turmas" | "estrutura" | "alunos" | "completo";

type Props = {
  initialAba?: Aba;
  initialAlunoId?: number | null;
  onFocusConsumed?: () => void;
};

function messageFrom(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

function confirmInactivation(goingInactive: boolean) {
  if (!goingInactive) return true;
  return window.confirm("Inativar este registro? O histórico acadêmico será preservado.");
}

export default function Cadastro({ initialAba, initialAlunoId, onFocusConsumed }: Props) {
  const [aba, setAba] = useState<Aba>(initialAba ?? "turmas");
  const [focusAlunoId, setFocusAlunoId] = useState<number | null>(initialAlunoId ?? null);
  const [students, setStudents] = useState<Aluno[]>([]);
  const [schools, setSchools] = useState<Escola[]>([]);
  const [schoolYears, setSchoolYears] = useState<AnoLetivo[]>([]);
  const [classes, setClasses] = useState<Turma[]>([]);
  const [turmaAlunos, setTurmaAlunos] = useState<AlunoTurma[]>([]);
  const [matriculasAtivas, setMatriculasAtivas] = useState<MatriculaAtiva[]>([]);
  const [message, setMessage] = useState("Carregando cadastros...");
  const [busy, setBusy] = useState(false);

  const [filterSchoolId, setFilterSchoolId] = useState("");
  const [filterYearId, setFilterYearId] = useState("");
  const [workspaceClassId, setWorkspaceClassId] = useState("");
  const [editingAlunoId, setEditingAlunoId] = useState<number | null>(null);
  const [editingNome, setEditingNome] = useState("");
  const [studentSearch, setStudentSearch] = useState("");

  const [novoAlunoNome, setNovoAlunoNome] = useState("");
  const [matricularAlunoId, setMatricularAlunoId] = useState("");
  const [transferTargetId, setTransferTargetId] = useState("");

  const [schoolName, setSchoolName] = useState("");
  const [schoolInep, setSchoolInep] = useState("");
  const [schoolBairro, setSchoolBairro] = useState("");
  const [schoolCidade, setSchoolCidade] = useState("");
  const [schoolUf, setSchoolUf] = useState("DF");
  const [schoolLat, setSchoolLat] = useState("-15.7942");
  const [schoolLng, setSchoolLng] = useState("-47.8822");
  const [classMerenda, setClassMerenda] = useState(true);
  const [classApoio, setClassApoio] = useState(false);
  const [yearName, setYearName] = useState("");
  const [className, setClassName] = useState("");
  const [classSerie, setClassSerie] = useState("");
  const [classShift, setClassShift] = useState("");
  const [newClassSchoolId, setNewClassSchoolId] = useState("");
  const [newClassYearId, setNewClassYearId] = useState("");

  const [selectedSchoolId, setSelectedSchoolId] = useState("");
  const [selectedYearId, setSelectedYearId] = useState("");
  const [selectedClassId, setSelectedClassId] = useState("");
  const [selectedStudentId, setSelectedStudentId] = useState("");
  const [standaloneStudentName, setStandaloneStudentName] = useState("");

  const loadCatalog = async () => {
    const [loadedStudents, loadedSchools, loadedYears, loadedClasses] = await Promise.all([
      getStudents(),
      getSchools(),
      getSchoolYears(),
      getClasses(),
    ]);
    setStudents(loadedStudents);
    setSchools(loadedSchools);
    setSchoolYears(loadedYears);
    setClasses(loadedClasses);
    setNewClassSchoolId((current) => current || String(loadedSchools[0]?.id ?? ""));
    setNewClassYearId((current) => current || String(loadedYears[0]?.id ?? ""));
    setFilterYearId((current) => current || String(loadedYears.find((item) => item.ativo)?.id ?? loadedYears[0]?.id ?? ""));
    setFilterSchoolId((current) => current || String(loadedSchools.find((item) => item.ativo)?.id ?? loadedSchools[0]?.id ?? ""));
    const firstClass = loadedClasses.find((item) => item.ativa) ?? loadedClasses[0];
    setWorkspaceClassId((current) => {
      if (current && loadedClasses.some((item) => item.id === Number(current))) return current;
      return firstClass ? String(firstClass.id) : "";
    });
    setMessage("Escolha uma turma para gerenciar os alunos.");
  };

  const loadTurmaAlunos = async (turmaId: number) => {
    const loaded = await getClassStudents(turmaId);
    setTurmaAlunos(loaded);
  };

  const loadMatriculasAtivas = async (anoLetivoId?: number) => {
    if (!anoLetivoId) {
      setMatriculasAtivas([]);
      return;
    }
    setMatriculasAtivas(await getActiveEnrollments(anoLetivoId));
  };

  useEffect(() => {
    void loadCatalog().catch((error) => setMessage(messageFrom(error, "Falha ao carregar cadastros.")));
  }, []);

  useEffect(() => {
    if (initialAlunoId == null) return;
    setAba("completo");
    setFocusAlunoId(initialAlunoId);
    onFocusConsumed?.();
  }, [initialAlunoId]);

  useEffect(() => {
    if (!workspaceClassId) {
      setTurmaAlunos([]);
      return;
    }
    void loadTurmaAlunos(Number(workspaceClassId)).catch((error) => {
      setTurmaAlunos([]);
      setMessage(messageFrom(error, "Não foi possível carregar os alunos da turma."));
    });
  }, [workspaceClassId]);

  useEffect(() => {
    const turma = classes.find((item) => item.id === Number(workspaceClassId));
    const anoId = turma?.ano_letivo_id ?? (filterYearId ? Number(filterYearId) : undefined);
    void loadMatriculasAtivas(anoId).catch(() => setMatriculasAtivas([]));
  }, [workspaceClassId, filterYearId, classes]);

  const filteredClasses = useMemo(() => {
    return classes.filter((item) => {
      if (filterSchoolId && item.escola_id !== Number(filterSchoolId)) return false;
      if (filterYearId && item.ano_letivo_id !== Number(filterYearId)) return false;
      return true;
    });
  }, [classes, filterSchoolId, filterYearId]);

  const workspaceClass = classes.find((item) => item.id === Number(workspaceClassId));
  const schoolNameOf = (escolaId: number) => schools.find((item) => item.id === escolaId)?.nome ?? `Escola ${escolaId}`;
  const yearNameOf = (anoId: number) => schoolYears.find((item) => item.id === anoId)?.nome ?? `Ano ${anoId}`;

  const enrollmentByAluno = useMemo(() => {
    const map = new Map<number, MatriculaAtiva>();
    for (const item of matriculasAtivas) map.set(item.aluno_id, item);
    return map;
  }, [matriculasAtivas]);

  const enrolledIds = useMemo(() => new Set(turmaAlunos.map((item) => item.aluno_id)), [turmaAlunos]);
  const availableStudents = useMemo(
    () => students.filter((item) => item.ativo && !enrolledIds.has(item.id)),
    [students, enrolledIds],
  );
  const filteredAvailable = useMemo(() => {
    const term = studentSearch.trim().toLowerCase();
    if (!term) return availableStudents;
    return availableStudents.filter((item) => item.nome.toLowerCase().includes(term));
  }, [availableStudents, studentSearch]);

  const selectedEnrollment = matricularAlunoId ? enrollmentByAluno.get(Number(matricularAlunoId)) : undefined;
  const willTransfer =
    Boolean(selectedEnrollment) &&
    selectedEnrollment!.turma_id !== Number(workspaceClassId);

  const transferTargets = useMemo(
    () => classes.filter((item) => item.ativa && item.id !== Number(workspaceClassId) && (!filterYearId || item.ano_letivo_id === Number(filterYearId))),
    [classes, workspaceClassId, filterYearId],
  );

  async function run(action: () => Promise<void>, fallback: string) {
    if (busy) return;
    setBusy(true);
    try {
      await action();
    } catch (error) {
      setMessage(messageFrom(error, fallback));
    } finally {
      setBusy(false);
    }
  }

  async function createAndEnroll(event: FormEvent) {
    event.preventDefault();
    if (!workspaceClass || !novoAlunoNome.trim()) return;
    await run(async () => {
      const student = await createStudent({ nome: novoAlunoNome.trim() });
      await enrollStudent(student.id, workspaceClass.id, workspaceClass.ano_letivo_id);
      setStudents((current) => [...current, student]);
      setNovoAlunoNome("");
      await loadTurmaAlunos(workspaceClass.id);
      await loadMatriculasAtivas(workspaceClass.ano_letivo_id);
      setMessage(`${student.nome} cadastrado e matriculado em ${workspaceClass.nome}.`);
    }, "Não foi possível cadastrar e matricular o aluno.");
  }

  async function enrollExisting(event: FormEvent) {
    event.preventDefault();
    if (!workspaceClass || !matricularAlunoId) return;
    const alunoId = Number(matricularAlunoId);
    const nome = students.find((item) => item.id === alunoId)?.nome ?? "Aluno";
    const existente = enrollmentByAluno.get(alunoId);

    await run(async () => {
      if (existente && existente.turma_id === workspaceClass.id) {
        setMessage(`${nome} já está matriculado nesta turma.`);
        return;
      }

      if (existente) {
        const ok = window.confirm(
          `${nome} já está em «${existente.turma_nome}». Transferir para «${workspaceClass.nome}»?`,
        );
        if (!ok) return;
        await transferEnrollment(existente.matricula_id, workspaceClass.id, `Transferência para ${workspaceClass.nome}`);
        setMatricularAlunoId("");
        setStudentSearch("");
        await loadTurmaAlunos(workspaceClass.id);
        await loadMatriculasAtivas(workspaceClass.ano_letivo_id);
        setMessage(`${nome} transferido de «${existente.turma_nome}» para «${workspaceClass.nome}».`);
        return;
      }

      try {
        await enrollStudent(alunoId, workspaceClass.id, workspaceClass.ano_letivo_id);
      } catch (error) {
        const msg = messageFrom(error, "");
        if (msg.toLowerCase().includes("matrícula ativa")) {
          const atuais = await getActiveEnrollments(workspaceClass.ano_letivo_id);
          setMatriculasAtivas(atuais);
          const ativa = atuais.find((item) => item.aluno_id === alunoId);
          if (ativa) {
            const ok = window.confirm(
              `${nome} já está em «${ativa.turma_nome}». Transferir para «${workspaceClass.nome}»?`,
            );
            if (!ok) throw error;
            await transferEnrollment(ativa.matricula_id, workspaceClass.id, `Transferência para ${workspaceClass.nome}`);
            setMatricularAlunoId("");
            setStudentSearch("");
            await loadTurmaAlunos(workspaceClass.id);
            await loadMatriculasAtivas(workspaceClass.ano_letivo_id);
            setMessage(`${nome} transferido para «${workspaceClass.nome}».`);
            return;
          }
        }
        throw error;
      }

      setMatricularAlunoId("");
      setStudentSearch("");
      await loadTurmaAlunos(workspaceClass.id);
      await loadMatriculasAtivas(workspaceClass.ano_letivo_id);
      setMessage(`${nome} matriculado em ${workspaceClass.nome}.`);
    }, "Não foi possível matricular o aluno.");
  }

  async function saveInlineStudent() {
    if (!editingAlunoId || !editingNome.trim()) return;
    await run(async () => {
      const updated = await updateStudent(editingAlunoId, { nome: editingNome.trim() });
      setStudents((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      setTurmaAlunos((items) => items.map((item) => (item.aluno_id === updated.id ? { ...item, nome: updated.nome } : item)));
      setEditingAlunoId(null);
      setEditingNome("");
      setMessage(`Aluno ${updated.nome} atualizado.`);
    }, "Não foi possível atualizar o aluno.");
  }

  async function inactivateStudent(alunoId: number, nome: string) {
    if (!window.confirm(`Inativar ${nome}? O histórico acadêmico será preservado.`)) return;
    await run(async () => {
      const updated = await updateStudent(alunoId, { ativo: false });
      setStudents((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      setMessage(`${nome} inativado.`);
    }, "Não foi possível inativar o aluno.");
  }

  async function removeFromClass(item: AlunoTurma) {
    const motivo = window.prompt(`Encerrar matrícula de ${item.nome}? Informe o motivo:`, "Encerramento administrativo");
    if (!motivo || motivo.trim().length < 3) return;
    await run(async () => {
      await endEnrollment(item.matricula_id, motivo.trim());
      if (workspaceClassId) await loadTurmaAlunos(Number(workspaceClassId));
      if (workspaceClass) await loadMatriculasAtivas(workspaceClass.ano_letivo_id);
      setMessage(`Matrícula de ${item.nome} encerrada.`);
    }, "Não foi possível encerrar a matrícula.");
  }

  async function transferStudent(item: AlunoTurma) {
    if (!transferTargetId) {
      setMessage("Selecione a turma de destino antes de transferir.");
      return;
    }
    await run(async () => {
      await transferEnrollment(item.matricula_id, Number(transferTargetId), `Transferência de ${workspaceClass?.nome ?? "turma"}`);
      if (workspaceClassId) await loadTurmaAlunos(Number(workspaceClassId));
      if (workspaceClass) await loadMatriculasAtivas(workspaceClass.ano_letivo_id);
      setMessage(`${item.nome} transferido.`);
    }, "Não foi possível transferir o aluno.");
  }

  async function submitSchool(event: FormEvent) {
    event.preventDefault();
    if (!schoolName.trim()) return;
    await run(async () => {
      const school = await createSchool({
        nome: schoolName.trim(),
        codigo_inep: schoolInep.trim() || null,
        dependencia_administrativa: "municipal",
        bairro: schoolBairro.trim() || null,
        cidade: schoolCidade.trim() || null,
        uf: schoolUf.trim().toUpperCase() || null,
        latitude: schoolLat ? Number(schoolLat) : null,
        longitude: schoolLng ? Number(schoolLng) : null,
      });
      setSchools((current) => [...current, school]);
      setNewClassSchoolId(String(school.id));
      setFilterSchoolId(String(school.id));
      setSelectedSchoolId(String(school.id));
      setSchoolName("");
      setSchoolInep("");
      setMessage(`${school.nome} cadastrada.`);
    }, "Não foi possível cadastrar a escola.");
  }

  async function submitYear(event: FormEvent) {
    event.preventDefault();
    if (!yearName.trim()) return;
    await run(async () => {
      const year = await createSchoolYear(yearName.trim());
      setSchoolYears((current) => [...current, year]);
      setNewClassYearId(String(year.id));
      setFilterYearId(String(year.id));
      setYearName("");
      setMessage(`Ano letivo ${year.nome} cadastrado.`);
    }, "Não foi possível cadastrar o ano letivo.");
  }

  async function submitClass(event: FormEvent) {
    event.preventDefault();
    if (!className.trim() || !newClassSchoolId || !newClassYearId) return;
    await run(async () => {
      const schoolClass = await createClass({
        nome: className.trim(),
        serie: classSerie.trim(),
        turno: classShift.trim(),
        escola_id: Number(newClassSchoolId),
        ano_letivo_id: Number(newClassYearId),
        oferece_merenda: classMerenda,
        apoio_pedagogico: classApoio,
      });
      setClasses((current) => [...current, schoolClass]);
      setWorkspaceClassId(String(schoolClass.id));
      setFilterSchoolId(String(schoolClass.escola_id));
      setFilterYearId(String(schoolClass.ano_letivo_id));
      setAba("turmas");
      setClassName("");
      setClassSerie("");
      setClassShift("");
      setMessage(`${schoolClass.nome} cadastrada. Agora matricule os alunos.`);
    }, "Não foi possível cadastrar a turma.");
  }

  async function saveSchool(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const current = schools.find((item) => item.id === Number(selectedSchoolId));
    if (!current) return;
    if (!confirmInactivation(!current.ativo)) return;
    await run(async () => {
      const updated = await updateSchool(current.id, { nome: current.nome, codigo_inep: current.codigo_inep, ativo: current.ativo });
      setSchools((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      setMessage(`Escola ${updated.ativo ? "atualizada" : "inativada"}.`);
    }, "Não foi possível atualizar a escola.");
  }

  async function saveYear(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const current = schoolYears.find((item) => item.id === Number(selectedYearId));
    if (!current) return;
    if (!confirmInactivation(!current.ativo)) return;
    await run(async () => {
      const updated = await updateSchoolYear(current.id, { nome: current.nome, ativo: current.ativo });
      setSchoolYears((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      setMessage(`Ano letivo ${updated.ativo ? "atualizado" : "inativado"}.`);
    }, "Não foi possível atualizar o ano letivo.");
  }

  async function saveClass(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const current = classes.find((item) => item.id === Number(selectedClassId));
    if (!current) return;
    if (!confirmInactivation(!current.ativa)) return;
    await run(async () => {
      const updated = await updateClass(current.id, { nome: current.nome, serie: current.serie, turno: current.turno, ativa: current.ativa });
      setClasses((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      setMessage(`Turma ${updated.ativa ? "atualizada" : "inativada"}.`);
    }, "Não foi possível atualizar a turma.");
  }

  async function submitStandaloneStudent(event: FormEvent) {
    event.preventDefault();
    if (!standaloneStudentName.trim()) return;
    await run(async () => {
      const student = await createStudent({ nome: standaloneStudentName.trim() });
      setStudents((current) => [...current, student]);
      setSelectedStudentId(String(student.id));
      setStandaloneStudentName("");
      setMessage(`${student.nome} cadastrado. Use a aba Completo para enriquecer os dados.`);
    }, "Não foi possível cadastrar o aluno.");
  }

  async function saveStandaloneStudent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const current = students.find((item) => item.id === Number(selectedStudentId));
    if (!current) return;
    if (!confirmInactivation(!current.ativo)) return;
    await run(async () => {
      const updated = await updateStudent(current.id, { nome: current.nome, ativo: current.ativo });
      setStudents((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      setTurmaAlunos((items) => items.map((item) => (item.aluno_id === updated.id ? { ...item, nome: updated.nome } : item)));
      setMessage(`Aluno ${updated.ativo ? "atualizado" : "inativado"}.`);
    }, "Não foi possível atualizar o aluno.");
  }

  const selectedSchool = schools.find((item) => item.id === Number(selectedSchoolId));
  const selectedYear = schoolYears.find((item) => item.id === Number(selectedYearId));
  const selectedClass = classes.find((item) => item.id === Number(selectedClassId));
  const selectedStudent = students.find((item) => item.id === Number(selectedStudentId));

  return (
    <section className="workspace cadastro-workspace">
      <div className="section-heading">
        <div>
          <span className="eyebrow">SECRETARIA ESCOLAR</span>
          <h2>Cadastros</h2>
          <p>Comece pela turma: veja os alunos, edite nomes, matricule e transfira sem sair da tela.</p>
        </div>
      </div>

      <nav className="cadastro-tabs" aria-label="Seções de cadastro">
        <button className={aba === "turmas" ? "active" : ""} onClick={() => setAba("turmas")}>Turmas e alunos</button>
        <button className={aba === "estrutura" ? "active" : ""} onClick={() => setAba("estrutura")}>Escolas e turmas</button>
        <button className={aba === "alunos" ? "active" : ""} onClick={() => setAba("alunos")}>Alunos da rede</button>
        <button className={aba === "completo" ? "active" : ""} onClick={() => setAba("completo")}>Cadastro completo</button>
      </nav>

      <p className="feedback" role="status">{message}</p>

      {aba === "completo" && (
        <AlunoCompleto
          initialAlunoId={focusAlunoId}
          onChanged={() => void loadCatalog()}
          onInitialConsumed={() => setFocusAlunoId(null)}
        />
      )}

      {aba === "turmas" && (
        <div className="turma-workspace">
          <div className="turma-filters">
            <label>Escola
              <select value={filterSchoolId} onChange={(event) => setFilterSchoolId(event.target.value)}>
                <option value="">Todas</option>
                {schools.map((school) => <option key={school.id} value={school.id}>{school.nome}</option>)}
              </select>
            </label>
            <label>Ano letivo
              <select value={filterYearId} onChange={(event) => setFilterYearId(event.target.value)}>
                <option value="">Todos</option>
                {schoolYears.map((year) => <option key={year.id} value={year.id}>{year.nome}</option>)}
              </select>
            </label>
            <label>Turma
              <select value={workspaceClassId} onChange={(event) => { setWorkspaceClassId(event.target.value); setEditingAlunoId(null); setTransferTargetId(""); }}>
                <option value="">Selecione uma turma</option>
                {filteredClasses.map((schoolClass) => (
                  <option key={schoolClass.id} value={schoolClass.id}>
                    {schoolClass.nome}{schoolClass.serie ? ` · ${schoolClass.serie}` : ""}{schoolClass.ativa ? "" : " (inativa)"}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {!workspaceClass ? (
            <p className="empty">Selecione uma turma para ver e editar os alunos matriculados.</p>
          ) : (
            <>
              <div className="turma-summary">
                <div>
                  <h3>{workspaceClass.nome}</h3>
                  <p>
                    {schoolNameOf(workspaceClass.escola_id)} · {yearNameOf(workspaceClass.ano_letivo_id)}
                    {workspaceClass.turno ? ` · ${workspaceClass.turno}` : ""}
                  </p>
                </div>
                <strong>{turmaAlunos.length} aluno(s)</strong>
              </div>

              <div className="turma-actions-grid">
                <form className="form-panel" onSubmit={createAndEnroll}>
                  <h3>Novo aluno nesta turma</h3>
                  <label>Nome completo
                    <input value={novoAlunoNome} onChange={(event) => setNovoAlunoNome(event.target.value)} placeholder="Ex.: Maria Oliveira" />
                  </label>
                  <button className="primary" type="submit" disabled={busy || novoAlunoNome.trim().length < 2}>Cadastrar e matricular</button>
                </form>

                <form className="form-panel" onSubmit={enrollExisting}>
                  <h3>Matricular aluno existente</h3>
                  <p className="form-hint">
                    Alunos já matriculados em outra turma neste ano podem ser transferidos para esta turma.
                  </p>
                  <label>Buscar
                    <input value={studentSearch} onChange={(event) => setStudentSearch(event.target.value)} placeholder="Digite parte do nome" />
                  </label>
                  <label>Aluno
                    <select value={matricularAlunoId} onChange={(event) => setMatricularAlunoId(event.target.value)}>
                      <option value="">Selecione</option>
                      {filteredAvailable.map((student) => {
                        const ativa = enrollmentByAluno.get(student.id);
                        const suffix = ativa ? ` · já em ${ativa.turma_nome}` : "";
                        return (
                          <option key={student.id} value={student.id}>
                            {student.nome}{suffix}
                          </option>
                        );
                      })}
                    </select>
                  </label>
                  {willTransfer && selectedEnrollment && (
                    <p className="form-hint">
                      Ao confirmar, {selectedEnrollment.aluno_nome} sairá de «{selectedEnrollment.turma_nome}» e entrará nesta turma.
                    </p>
                  )}
                  <button className="primary" type="submit" disabled={busy || !matricularAlunoId}>
                    {willTransfer ? "Transferir para esta turma" : "Matricular"}
                  </button>
                </form>
              </div>

              <div className="form-panel turma-roster">
                <div className="roster-heading">
                  <h3>Alunos da turma</h3>
                  <label className="transfer-target">
                    Destino para transferência
                    <select value={transferTargetId} onChange={(event) => setTransferTargetId(event.target.value)}>
                      <option value="">Selecione outra turma</option>
                      {transferTargets.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.nome}{item.serie ? ` · ${item.serie}` : ""}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                {turmaAlunos.length === 0 ? (
                  <p className="empty">Nenhum aluno matriculado nesta turma.</p>
                ) : (
                  <ul className="roster-list">
                    {turmaAlunos.map((item, index) => (
                      <li key={item.matricula_id} className="roster-row">
                        <span className="number">{String(index + 1).padStart(2, "0")}</span>
                        {editingAlunoId === item.aluno_id ? (
                          <div className="roster-edit">
                            <input value={editingNome} onChange={(event) => setEditingNome(event.target.value)} autoFocus />
                            <button className="primary" type="button" disabled={busy} onClick={() => void saveInlineStudent()}>Salvar</button>
                            <button className="quiet" type="button" onClick={() => { setEditingAlunoId(null); setEditingNome(""); }}>Cancelar</button>
                          </div>
                        ) : (
                          <>
                            <span className="student-name">{item.nome}</span>
                            <div className="roster-buttons">
                              <button className="quiet" type="button" onClick={() => { setEditingAlunoId(item.aluno_id); setEditingNome(item.nome); }}>Editar</button>
                              <button className="quiet" type="button" disabled={busy || !transferTargetId} onClick={() => void transferStudent(item)}>Transferir</button>
                              <button className="quiet danger-quiet" type="button" disabled={busy} onClick={() => void removeFromClass(item)}>Encerrar</button>
                              <button className="quiet danger-quiet" type="button" disabled={busy} onClick={() => void inactivateStudent(item.aluno_id, item.nome)}>Inativar</button>
                            </div>
                          </>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {aba === "estrutura" && (
        <div className="forms-grid">
          <form className="form-panel" onSubmit={submitSchool}>
            <h3>Nova escola</h3>
            <label>Nome<input value={schoolName} onChange={(event) => setSchoolName(event.target.value)} placeholder="Ex.: Escola Municipal Centro" /></label>
            <label>Código INEP<input value={schoolInep} onChange={(event) => setSchoolInep(event.target.value)} placeholder="Opcional" /></label>
            <label>Bairro<input value={schoolBairro} onChange={(event) => setSchoolBairro(event.target.value)} /></label>
            <label>Cidade<input value={schoolCidade} onChange={(event) => setSchoolCidade(event.target.value)} /></label>
            <label>UF<input value={schoolUf} onChange={(event) => setSchoolUf(event.target.value)} maxLength={2} /></label>
            <label>Latitude<input value={schoolLat} onChange={(event) => setSchoolLat(event.target.value)} /></label>
            <label>Longitude<input value={schoolLng} onChange={(event) => setSchoolLng(event.target.value)} /></label>
            <button className="primary" type="submit" disabled={busy || !schoolName.trim()}>Cadastrar escola</button>
          </form>

          <form className="form-panel" onSubmit={submitYear}>
            <h3>Novo ano letivo</h3>
            <label>Nome<input value={yearName} onChange={(event) => setYearName(event.target.value)} placeholder="Ex.: 2026" /></label>
            <p className="form-hint">Use pelo menos 4 caracteres. O nome precisa ser único na rede.</p>
            <button className="primary" type="submit" disabled={busy || yearName.trim().length < 4}>Cadastrar ano letivo</button>
          </form>

          <form className="form-panel" onSubmit={submitClass}>
            <h3>Nova turma</h3>
            <label>Escola
              <select value={newClassSchoolId} onChange={(event) => setNewClassSchoolId(event.target.value)}>
                <option value="">Selecione uma escola</option>
                {schools.filter((item) => item.ativo).map((school) => <option key={school.id} value={school.id}>{school.nome}</option>)}
              </select>
            </label>
            <label>Ano letivo
              <select value={newClassYearId} onChange={(event) => setNewClassYearId(event.target.value)}>
                <option value="">Selecione um ano</option>
                {schoolYears.filter((item) => item.ativo).map((year) => <option key={year.id} value={year.id}>{year.nome}</option>)}
              </select>
            </label>
            <label>Nome<input value={className} onChange={(event) => setClassName(event.target.value)} placeholder="Ex.: 1º Ano A" /></label>
            <label>Série<input value={classSerie} onChange={(event) => setClassSerie(event.target.value)} placeholder="Ex.: 1° Ano" /></label>
            <label>Turno<input value={classShift} onChange={(event) => setClassShift(event.target.value)} placeholder="Ex.: manhã" /></label>
            <label className="checkbox-label"><input type="checkbox" checked={classMerenda} onChange={(event) => setClassMerenda(event.target.checked)} />Oferece merenda</label>
            <label className="checkbox-label"><input type="checkbox" checked={classApoio} onChange={(event) => setClassApoio(event.target.checked)} />Apoio pedagógico</label>
            <button className="primary" type="submit" disabled={busy || !className.trim() || !newClassSchoolId || !newClassYearId}>Cadastrar turma</button>
          </form>

          <form className="form-panel management-panel" onSubmit={saveSchool}>
            <h3>Editar escola</h3>
            <label>Registro
              <select value={selectedSchoolId} onChange={(event) => setSelectedSchoolId(event.target.value)}>
                <option value="">Selecione uma escola</option>
                {schools.map((school) => <option key={school.id} value={school.id}>{school.nome}{school.ativo ? "" : " (inativa)"}</option>)}
              </select>
            </label>
            {selectedSchool && (
              <>
                <label>Nome<input value={selectedSchool.nome} onChange={(event) => setSchools((items) => items.map((item) => item.id === selectedSchool.id ? { ...item, nome: event.target.value } : item))} /></label>
                <label>Código INEP<input value={selectedSchool.codigo_inep ?? ""} onChange={(event) => setSchools((items) => items.map((item) => item.id === selectedSchool.id ? { ...item, codigo_inep: event.target.value || null } : item))} /></label>
                <label className="checkbox-label">
                  <input type="checkbox" checked={selectedSchool.ativo} onChange={(event) => setSchools((items) => items.map((item) => item.id === selectedSchool.id ? { ...item, ativo: event.target.checked } : item))} />
                  Registro ativo
                </label>
                <button className="primary" type="submit" disabled={busy}>Salvar escola</button>
              </>
            )}
          </form>

          <form className="form-panel management-panel" onSubmit={saveYear}>
            <h3>Editar ano letivo</h3>
            <label>Registro
              <select value={selectedYearId} onChange={(event) => setSelectedYearId(event.target.value)}>
                <option value="">Selecione um ano</option>
                {schoolYears.map((year) => <option key={year.id} value={year.id}>{year.nome}{year.ativo ? "" : " (inativo)"}</option>)}
              </select>
            </label>
            {selectedYear && (
              <>
                <label>Nome<input value={selectedYear.nome} onChange={(event) => setSchoolYears((items) => items.map((item) => item.id === selectedYear.id ? { ...item, nome: event.target.value } : item))} /></label>
                <label className="checkbox-label">
                  <input type="checkbox" checked={selectedYear.ativo} onChange={(event) => setSchoolYears((items) => items.map((item) => item.id === selectedYear.id ? { ...item, ativo: event.target.checked } : item))} />
                  Registro ativo
                </label>
                <button className="primary" type="submit" disabled={busy}>Salvar ano letivo</button>
              </>
            )}
          </form>

          <form className="form-panel management-panel" onSubmit={saveClass}>
            <h3>Editar turma</h3>
            <label>Registro
              <select value={selectedClassId} onChange={(event) => setSelectedClassId(event.target.value)}>
                <option value="">Selecione uma turma</option>
                {classes.map((schoolClass) => <option key={schoolClass.id} value={schoolClass.id}>{schoolClass.nome}{schoolClass.ativa ? "" : " (inativa)"}</option>)}
              </select>
            </label>
            {selectedClass && (
              <>
                <label>Nome<input value={selectedClass.nome} onChange={(event) => setClasses((items) => items.map((item) => item.id === selectedClass.id ? { ...item, nome: event.target.value } : item))} /></label>
                <label>Série<input value={selectedClass.serie ?? ""} onChange={(event) => setClasses((items) => items.map((item) => item.id === selectedClass.id ? { ...item, serie: event.target.value || null } : item))} /></label>
                <label>Turno<input value={selectedClass.turno ?? ""} onChange={(event) => setClasses((items) => items.map((item) => item.id === selectedClass.id ? { ...item, turno: event.target.value || null } : item))} /></label>
                <label className="checkbox-label">
                  <input type="checkbox" checked={selectedClass.ativa} onChange={(event) => setClasses((items) => items.map((item) => item.id === selectedClass.id ? { ...item, ativa: event.target.checked } : item))} />
                  Turma ativa
                </label>
                <button className="primary" type="submit" disabled={busy}>Salvar turma</button>
                <button className="quiet" type="button" onClick={() => { setWorkspaceClassId(String(selectedClass.id)); setAba("turmas"); }}>Abrir alunos desta turma</button>
              </>
            )}
          </form>
        </div>
      )}

      {aba === "alunos" && (
        <div className="forms-grid">
          <form className="form-panel" onSubmit={submitStandaloneStudent}>
            <h3>Novo aluno da rede</h3>
            <label>Nome completo<input value={standaloneStudentName} onChange={(event) => setStandaloneStudentName(event.target.value)} placeholder="Ex.: João Silva" /></label>
            <p className="form-hint">Depois de criar, use a aba Turmas e alunos para matricular.</p>
            <button className="primary" type="submit" disabled={busy || standaloneStudentName.trim().length < 2}>Cadastrar aluno</button>
          </form>

          <form className="form-panel management-panel" onSubmit={saveStandaloneStudent}>
            <h3>Editar aluno</h3>
            <label>Registro
              <select value={selectedStudentId} onChange={(event) => setSelectedStudentId(event.target.value)}>
                <option value="">Selecione um aluno</option>
                {students.map((student) => <option key={student.id} value={student.id}>{student.nome}{student.ativo ? "" : " (inativo)"}</option>)}
              </select>
            </label>
            {selectedStudent && (
              <>
                <label>Nome<input value={selectedStudent.nome} onChange={(event) => setStudents((items) => items.map((item) => item.id === selectedStudent.id ? { ...item, nome: event.target.value } : item))} /></label>
                <label className="checkbox-label">
                  <input type="checkbox" checked={selectedStudent.ativo} onChange={(event) => setStudents((items) => items.map((item) => item.id === selectedStudent.id ? { ...item, ativo: event.target.checked } : item))} />
                  Aluno ativo
                </label>
                <button className="primary" type="submit" disabled={busy}>Salvar aluno</button>
              </>
            )}
          </form>
        </div>
      )}
    </section>
  );
}
