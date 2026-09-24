import { useEffect, useMemo, useState } from "react";
import { db } from "./db";
import { getClassSummary, getClasses, getDayAttendance, sendAttendance, type Student, type Turma } from "./api";
import Cadastro from "./Cadastro";
import Login from "./Login";
import PainelGestao from "./PainelGestao";
import { canManageRecords, clearSession, getSession, type Sessao } from "./auth";

const today = new Date().toISOString().slice(0, 10);

function App() {
  const [session, setSessionState] = useState<Sessao | null>(() => getSession());
  const [mode, setMode] = useState<"professor" | "gestor" | "cadastro">("professor");
  const [focusAlunoId, setFocusAlunoId] = useState<number | null>(null);
  const [classes, setClasses] = useState<Turma[]>([]);
  const [classId, setClassId] = useState<number | "">("");
  const [date, setDate] = useState(today);
  const [students, setStudents] = useState<Student[]>([]);
  const [presence, setPresence] = useState<Record<number, boolean>>({});
  const [pending, setPending] = useState(0);
  const [online, setOnline] = useState(navigator.onLine);
  const [message, setMessage] = useState("Carregando diário...");

  const selectedClass = classes.find((item) => item.id === classId);
  const refreshPending = async () => setPending(await db.pendingCalls.count());

  const loadClasses = async () => {
    try {
      const loaded = await getClasses();
      const active = loaded.filter((item) => item.ativa);
      setClasses(active);
      setClassId((current) => {
        if (typeof current === "number" && active.some((item) => item.id === current)) return current;
        return active[0]?.id ?? "";
      });
      if (!active.length) setMessage("Nenhuma turma ativa. Cadastre uma turma na aba Cadastros.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao carregar as turmas.");
    }
  };

  const loadSummary = async (turmaId: number, dataChamada: string) => {
    try {
      const [summary, day] = await Promise.all([getClassSummary(turmaId), getDayAttendance(turmaId, dataChamada)]);
      setStudents(summary);
      setPresence(Object.fromEntries(day.map((student) => [student.aluno_id, student.presente])));
      const registered = day.some((student) => student.registrada);
      const faltas = day.filter((student) => !student.presente).length;
      if (!summary.length) {
        setMessage("Esta turma ainda não possui alunos matriculados.");
      } else if (registered) {
        setMessage(`Chamada de ${dataChamada} carregada · ${faltas} falta(s) registrada(s).`);
      } else {
        setMessage("Diário pronto para registrar.");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao carregar a turma.");
    }
  };

  const syncQueue = async () => {
    const items = await db.pendingCalls.toArray();
    for (const item of items) {
      try {
        await sendAttendance(item.payload);
        await db.pendingCalls.delete(item.id!);
      } catch {
        break;
      }
    }
    await refreshPending();
  };

  useEffect(() => {
    const onUnauthorized = () => setSessionState(null);
    window.addEventListener("sga:unauthorized", onUnauthorized);
    return () => window.removeEventListener("sga:unauthorized", onUnauthorized);
  }, []);

  useEffect(() => {
    if (!session) return;
    void refreshPending();
    void loadClasses();
    const onlineHandler = () => {
      setOnline(true);
      void syncQueue();
    };
    const offlineHandler = () => setOnline(false);
    window.addEventListener("online", onlineHandler);
    window.addEventListener("offline", offlineHandler);
    return () => {
      window.removeEventListener("online", onlineHandler);
      window.removeEventListener("offline", offlineHandler);
    };
  }, [session]);

  useEffect(() => {
    if (typeof classId !== "number") return;
    void loadSummary(classId, date);
  }, [classId, date]);

  const payload = useMemo(
    () => ({
      turma_id: classId,
      data: date,
      ordem: 1,
      itens: students.map((student) => ({ aluno_id: student.aluno_id, presente: presence[student.aluno_id] ?? true })),
    }),
    [classId, date, students, presence],
  );

  const saveAttendance = async () => {
    if (typeof classId !== "number" || !students.length) return;
    try {
      if (!navigator.onLine) {
        await db.pendingCalls.put({
          key: `${classId}-${date}-1`,
          payload,
          createdAt: Date.now(),
        });
        await refreshPending();
        setMessage("Chamada salva offline. Será sincronizada quando houver conexão.");
        return;
      }
      await sendAttendance(payload);
      await loadSummary(classId, date);
      setMessage("Chamada salva com sucesso.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar a chamada.");
    }
  };

  const markAllPresent = () => {
    setPresence(Object.fromEntries(students.map((student) => [student.aluno_id, true])));
  };

  if (!session) {
    return <Login onSuccess={(next) => setSessionState(next)} />;
  }

  const canCadastro = canManageRecords(session.usuario.perfil);
  const absentCount = students.filter((student) => !presence[student.aluno_id]).length;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">{session.usuario.perfil.toUpperCase()} · {session.usuario.nome}</span>
          <h1>Diário de bordo</h1>
        </div>
        <div className="status">
          <span className={online ? "dot online" : "dot"} />
          {online ? "Conectado" : "Sem conexão"}
          <span className="pending">{pending} pendentes</span>
          <button className="quiet header-logout" onClick={() => { clearSession(); setSessionState(null); }}>Sair</button>
        </div>
      </header>
      <main>
        <nav className="mode-switch" aria-label="Modo do sistema">
          <button className={mode === "professor" ? "active" : ""} onClick={() => setMode("professor")}>Chamada</button>
          <button className={mode === "gestor" ? "active" : ""} onClick={() => setMode("gestor")}>Painel gestor</button>
          {canCadastro && (
            <button
              className={mode === "cadastro" ? "active" : ""}
              onClick={() => {
                setFocusAlunoId(null);
                setMode("cadastro");
              }}
            >
              Cadastros
            </button>
          )}
        </nav>
        {mode === "cadastro" && canCadastro ? (
          <Cadastro
            initialAba={focusAlunoId != null ? "completo" : undefined}
            initialAlunoId={focusAlunoId}
            onFocusConsumed={() => setFocusAlunoId(null)}
          />
        ) : mode === "professor" ? (
          <section className="workspace">
            <div className="section-heading">
              <div>
                <span className="eyebrow">DIÁRIO ELETRÔNICO</span>
                <h2>{selectedClass ? selectedClass.nome : "Turma"}</h2>
                <p>{students.length} estudantes vinculados · {absentCount} faltas nesta chamada</p>
              </div>
              <div className="controls">
                <label>Turma
                  <select value={classId} onChange={(event) => setClassId(event.target.value ? Number(event.target.value) : "")}>
                    {!classes.length && <option value="">Nenhuma turma cadastrada</option>}
                    {classes.map((schoolClass) => (
                      <option key={schoolClass.id} value={schoolClass.id}>
                        {schoolClass.nome}{schoolClass.serie ? ` · ${schoolClass.serie}` : ""}{schoolClass.turno ? ` · ${schoolClass.turno}` : ""}
                      </option>
                    ))}
                  </select>
                </label>
                <label>Data<input type="date" value={date} onChange={(event) => setDate(event.target.value)} /></label>
              </div>
            </div>
            <div className="action-row">
              <button className="quiet" onClick={markAllPresent} disabled={!students.length}>Todos presentes</button>
              <button className="primary" onClick={() => void saveAttendance()} disabled={!students.length}>Salvar chamada</button>
            </div>
            <p className="feedback" role="status">{message}</p>
            <div className="student-list">
              {students.map((student, index) => (
                <button
                  className={`student-row ${presence[student.aluno_id] ? "present" : "absent"}`}
                  key={student.aluno_id}
                  onClick={() => setPresence((current) => ({ ...current, [student.aluno_id]: !current[student.aluno_id] }))}
                >
                  <span className="number">{String(index + 1).padStart(2, "0")}</span>
                  <span className="student-name">{student.nome}</span>
                  <span className="attendance-label">{presence[student.aluno_id] ? "Presente" : "Falta"}</span>
                  <span className="check">{presence[student.aluno_id] ? "✓" : "×"}</span>
                </button>
              ))}
            </div>
          </section>
        ) : (
          <PainelGestao
            students={students}
            onToast={setMessage}
            onOpenAlunoCadastro={
              canCadastro
                ? (alunoId) => {
                    setFocusAlunoId(alunoId);
                    setMode("cadastro");
                  }
                : undefined
            }
          />
        )}
      </main>
      <footer>
        <span>SGA-EDU · dados protegidos no dispositivo</span>
        <button onClick={() => void syncQueue()}>Sincronizar agora</button>
      </footer>
    </div>
  );
}

export default App;
