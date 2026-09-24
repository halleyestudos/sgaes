import { useState, type FormEvent } from "react";
import { login } from "./api";
import { setSession, type Sessao } from "./auth";

type Props = { onSuccess: (session: Sessao) => void };

export default function Login({ onSuccess }: Props) {
  const [email, setEmail] = useState("gestor@sga.local");
  const [senha, setSenha] = useState("");
  const [message, setMessage] = useState("Entre com o usuário da secretaria ou da escola.");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const session = await login(email.trim().toLowerCase(), senha);
      setSession(session);
      onSuccess(session);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível entrar.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-shell">
      <form className="form-panel login-panel" onSubmit={submit}>
        <span className="eyebrow">SGA-EDU</span>
        <h1>Entrar</h1>
        <p>O acesso usa a rede e o perfil gravados no token. A tela não escolhe a prefeitura.</p>
        <label>E-mail<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" /></label>
        <label>Senha<input type="password" value={senha} onChange={(event) => setSenha(event.target.value)} autoComplete="current-password" /></label>
        <button className="primary" type="submit" disabled={busy || !email || senha.length < 6}>Entrar</button>
        <p className="feedback" role="status">{message}</p>
        <p className="form-hint">Demo: gestor@sga.local / Gestor@123 · professor@sga.local / Professor@123 · secretaria@sga.local / Secretaria@123</p>
      </form>
    </div>
  );
}
