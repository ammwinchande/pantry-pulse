import React, { useMemo, useState } from 'react';
import {
    HeartHandshake,
    Mail,
    Lock,
    User,
    LogIn,
    UserPlus,
    KeyRound,
    CheckCircle2,
    AlertCircle,
    Loader2,
    ArrowLeft,
    ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../api/useAuth';
import type { UserRole } from '../types';

type Mode = 'login' | 'register' | 'forgot';

const ROLE_OPTIONS: { value: UserRole; label: string }[] = [
    { value: 'COORDINATOR', label: 'Coordinator' },
    { value: 'INTAKE_WORKER', label: 'Dock Intake Staff' },
    { value: 'VOLUNTEER', label: 'Volunteer Driver' },
    { value: 'DONOR', label: 'Food Donor Partner' },
];

function extractToken(): string | null {
    return new URLSearchParams(window.location.search).get('token');
}

function errorMessage(err: unknown): string {
    if (err instanceof Error) {
        // The API returns the detail string directly.
        return err.message.replace(/^"|"$/g, '') || 'Something went wrong. Please try again.';
    }
    return 'Something went wrong. Please try again.';
}

const inputClass =
    'w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition';
const labelClass = 'block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide';
const primaryBtn =
    'w-full inline-flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-sm font-semibold px-4 py-2.5 rounded-lg shadow-md shadow-emerald-600/30 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed';

const AuthShell: React.FC<{ children: React.ReactNode; title: string; subtitle?: string }> = ({
    children,
    title,
    subtitle,
}) => (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">
            <div className="flex items-center gap-3 mb-6 justify-center">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white">
                    <HeartHandshake className="w-7 h-7" />
                </div>
                <div>
                    <div className="text-2xl font-black tracking-tight text-white">PantryPulse</div>
                    <div className="text-xs text-slate-400">Autonomous Food Rescue & Volunteer Dispatch</div>
                </div>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl">
                <h1 className="text-lg font-bold text-white mb-1">{title}</h1>
                {subtitle && <p className="text-sm text-slate-400 mb-6">{subtitle}</p>}
                {!subtitle && <div className="mb-6" />}
                {children}
            </div>

            <p className="text-center text-[11px] text-slate-600 mt-6">
                Agents for Humans Hackathon • Good Neighbor Track • Powered by AWS Strands Agents SDK
            </p>
        </div>
    </div>
);

const Alert: React.FC<{ kind: 'error' | 'success'; children: React.ReactNode }> = ({
    kind,
    children,
}) => (
    <div
        className={`flex items-start gap-2 text-xs rounded-lg px-3 py-2.5 mb-4 border ${kind === 'error'
                ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            }`}
    >
        {kind === 'error' ? (
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
        ) : (
            <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
        )}
        <span>{children}</span>
    </div>
);

// --- Login ---
const LoginForm: React.FC<{ onSwitch: (m: Mode) => void }> = ({ onSwitch }) => {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [pending, setPending] = useState(false);

    async function submit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setPending(true);
        try {
            await login({ email, password });
            // isAuthenticated flips; App re-renders to the dashboard.
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setPending(false);
        }
    }

    return (
        <form onSubmit={submit} className="space-y-4">
            {error && <Alert kind="error">{error}</Alert>}
            <div>
                <label className={labelClass}>Email</label>
                <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@pantrypulse.org"
                    className={inputClass}
                />
            </div>
            <div>
                <label className={labelClass}>Password</label>
                <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className={inputClass}
                />
            </div>
            <button type="submit" disabled={pending} className={primaryBtn}>
                {pending ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
                {pending ? 'Signing in…' : 'Sign in'}
            </button>

            <div className="flex items-center justify-between text-xs">
                <button
                    type="button"
                    onClick={() => onSwitch('forgot')}
                    className="text-slate-400 hover:text-emerald-400 cursor-pointer"
                >
                    Forgot password?
                </button>
                <button
                    type="button"
                    onClick={() => onSwitch('register')}
                    className="text-slate-400 hover:text-emerald-400 cursor-pointer"
                >
                    Create account
                </button>
            </div>

            <div className="rounded-lg bg-slate-950/60 border border-slate-800 px-3 py-2.5 text-[11px] text-slate-500">
                <div className="font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" /> Demo coordinator
                </div>
                <div>
                    Email: <span className="text-slate-300">coordinator@pantrypulse.org</span>
                </div>
                <div>
                    Password: <span className="text-slate-300">Coordinator123!</span>
                </div>
            </div>
        </form>
    );
};

// --- Register ---
const RegisterForm: React.FC<{ onSwitch: (m: Mode) => void }> = ({ onSwitch }) => {
    const { register } = useAuth();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState<UserRole>('VOLUNTEER');
    const [error, setError] = useState<string | null>(null);
    const [pending, setPending] = useState(false);
    const [activationUrl, setActivationUrl] = useState<string | null>(null);

    async function submit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setPending(true);
        try {
            const res = await register({ name, email, password, role });
            setActivationUrl(res.activation_url ?? null);
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setPending(false);
        }
    }

    if (activationUrl) {
        return (
            <div>
                <Alert kind="success">
                    Account created! We sent an activation link to <b>{email}</b>.
                </Alert>
                <p className="text-xs text-slate-400 mb-3">
                    In this demo the activation link is shown below (in production it arrives by email via
                    Mailtrap). Click it to activate, then sign in.
                </p>
                <a href={activationUrl} className={primaryBtn}>
                    <Mail className="w-4 h-4" /> Open activation link
                </a>
                <button
                    type="button"
                    onClick={() => onSwitch('login')}
                    className="mt-3 w-full text-xs text-slate-400 hover:text-emerald-400 cursor-pointer"
                >
                    Back to sign in
                </button>
            </div>
        );
    }

    return (
        <form onSubmit={submit} className="space-y-4">
            {error && <Alert kind="error">{error}</Alert>}
            <div>
                <label className={labelClass}>Full name</label>
                <div className="relative">
                    <User className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        required
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Jordan Rivera"
                        className={`${inputClass} pl-9`}
                    />
                </div>
            </div>
            <div>
                <label className={labelClass}>Email</label>
                <div className="relative">
                    <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        className={`${inputClass} pl-9`}
                    />
                </div>
            </div>
            <div>
                <label className={labelClass}>Password</label>
                <div className="relative">
                    <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="password"
                        required
                        minLength={8}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="At least 8 characters"
                        className={`${inputClass} pl-9`}
                    />
                </div>
            </div>
            <div>
                <label className={labelClass}>Role</label>
                <select
                    value={role}
                    onChange={(e) => setRole(e.target.value as UserRole)}
                    className={inputClass}
                >
                    {ROLE_OPTIONS.map((o) => (
                        <option key={o.value} value={o.value}>
                            {o.label}
                        </option>
                    ))}
                </select>
            </div>
            <button type="submit" disabled={pending} className={primaryBtn}>
                {pending ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserPlus className="w-4 h-4" />}
                {pending ? 'Creating account…' : 'Create account'}
            </button>
            <button
                type="button"
                onClick={() => onSwitch('login')}
                className="w-full text-xs text-slate-400 hover:text-emerald-400 cursor-pointer"
            >
                Already have an account? Sign in
            </button>
        </form>
    );
};

// --- Forgot password ---
const ForgotForm: React.FC<{ onSwitch: (m: Mode) => void }> = ({ onSwitch }) => {
    const { requestPasswordReset } = useAuth();
    const [email, setEmail] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [pending, setPending] = useState(false);
    const [sent, setSent] = useState(false);
    const [resetUrl, setResetUrl] = useState<string | null>(null);

    async function submit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setPending(true);
        try {
            const res = await requestPasswordReset(email);
            setResetUrl(res.reset_url ?? null);
            setSent(true);
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setPending(false);
        }
    }

    if (sent) {
        return (
            <div>
                <Alert kind="success">
                    If <b>{email}</b> is registered, a reset link has been sent.
                </Alert>
                {resetUrl && (
                    <>
                        <p className="text-xs text-slate-400 mb-3">
                            Demo aid: the reset link is shown below (in production it arrives by email via
                            Mailtrap).
                        </p>
                        <a href={resetUrl} className={primaryBtn}>
                            <KeyRound className="w-4 h-4" /> Open reset link
                        </a>
                    </>
                )}
                <button
                    type="button"
                    onClick={() => onSwitch('login')}
                    className="mt-3 w-full text-xs text-slate-400 hover:text-emerald-400 cursor-pointer"
                >
                    Back to sign in
                </button>
            </div>
        );
    }

    return (
        <form onSubmit={submit} className="space-y-4">
            {error && <Alert kind="error">{error}</Alert>}
            <p className="text-sm text-slate-400">
                Enter your account email and we&apos;ll send you a link to reset your password.
            </p>
            <div>
                <label className={labelClass}>Email</label>
                <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className={inputClass}
                />
            </div>
            <button type="submit" disabled={pending} className={primaryBtn}>
                {pending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
                {pending ? 'Sending…' : 'Send reset link'}
            </button>
            <button
                type="button"
                onClick={() => onSwitch('login')}
                className="w-full text-xs text-slate-400 hover:text-emerald-400 cursor-pointer"
            >
                Back to sign in
            </button>
        </form>
    );
};

// --- Activation (from /activate?token=) ---
const ActivationView: React.FC = () => {
    const { verifyEmail } = useAuth();
    const token = useMemo(() => extractToken(), []);
    const [state, setState] = useState<'loading' | 'success' | 'error'>('loading');
    const [error, setError] = useState<string | null>(null);

    React.useEffect(() => {
        if (!token) {
            setState('error');
            setError('Missing activation token. Please use the link from your email.');
            return;
        }
        let cancelled = false;
        (async () => {
            try {
                await verifyEmail(token);
                if (!cancelled) setState('success');
            } catch (err) {
                if (!cancelled) {
                    setState('error');
                    setError(errorMessage(err));
                }
            }
        })();
        return () => {
            cancelled = true;
        };
    }, [token, verifyEmail]);

    return (
        <AuthShell
            title="Activate your account"
            subtitle="Confirming your email address…"
        >
            {state === 'loading' && (
                <div className="flex items-center justify-center gap-2 text-sm text-slate-400 py-8">
                    <Loader2 className="w-5 h-5 animate-spin text-emerald-500" /> Verifying link…
                </div>
            )}
            {state === 'success' && (
                <div>
                    <Alert kind="success">Your email is verified and your account is now active.</Alert>
                    <a href="/" className={primaryBtn}>
                        <LogIn className="w-4 h-4" /> Go to sign in
                    </a>
                </div>
            )}
            {state === 'error' && (
                <div>
                    <Alert kind="error">{error}</Alert>
                    <a href="/" className={primaryBtn}>
                        <ArrowLeft className="w-4 h-4" /> Back to sign in
                    </a>
                </div>
            )}
        </AuthShell>
    );
};

// --- Reset password (from /reset-password?token=) ---
const ResetPasswordView: React.FC = () => {
    const { confirmPasswordReset } = useAuth();
    const token = useMemo(() => extractToken(), []);
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [pending, setPending] = useState(false);
    const [done, setDone] = useState(false);

    async function submit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        if (password !== confirm) {
            setError('Passwords do not match.');
            return;
        }
        if (!token) {
            setError('Missing reset token. Please use the link from your email.');
            return;
        }
        setPending(true);
        try {
            await confirmPasswordReset(token, password);
            setDone(true);
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setPending(false);
        }
    }

    return (
        <AuthShell title="Set a new password" subtitle="Choose a new password for your account.">
            {done ? (
                <div>
                    <Alert kind="success">Password updated. You can now sign in with your new password.</Alert>
                    <a href="/" className={primaryBtn}>
                        <LogIn className="w-4 h-4" /> Go to sign in
                    </a>
                </div>
            ) : (
                <form onSubmit={submit} className="space-y-4">
                    {error && <Alert kind="error">{error}</Alert>}
                    <div>
                        <label className={labelClass}>New password</label>
                        <div className="relative">
                            <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                            <input
                                type="password"
                                required
                                minLength={8}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="At least 8 characters"
                                className={`${inputClass} pl-9`}
                            />
                        </div>
                    </div>
                    <div>
                        <label className={labelClass}>Confirm new password</label>
                        <div className="relative">
                            <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                            <input
                                type="password"
                                required
                                minLength={8}
                                value={confirm}
                                onChange={(e) => setConfirm(e.target.value)}
                                placeholder="Re-enter new password"
                                className={`${inputClass} pl-9`}
                            />
                        </div>
                    </div>
                    <button type="submit" disabled={pending} className={primaryBtn}>
                        {pending ? <Loader2 className="w-4 h-4 animate-spin" /> : <KeyRound className="w-4 h-4" />}
                        {pending ? 'Updating…' : 'Update password'}
                    </button>
                </form>
            )}
        </AuthShell>
    );
};

// --- Main auth card (login / register / forgot) ---
const AuthCard: React.FC = () => {
    const [mode, setMode] = useState<Mode>('login');
    const titles: Record<Mode, { title: string; subtitle: string }> = {
        login: { title: 'Welcome back', subtitle: 'Sign in to your PantryPulse account.' },
        register: { title: 'Create your account', subtitle: 'Join the food rescue network.' },
        forgot: { title: 'Reset your password', subtitle: 'We\'ll email you a secure reset link.' },
    };

    return (
        <AuthShell title={titles[mode].title} subtitle={titles[mode].subtitle}>
            {mode === 'login' && <LoginForm onSwitch={setMode} />}
            {mode === 'register' && <RegisterForm onSwitch={setMode} />}
            {mode === 'forgot' && <ForgotForm onSwitch={setMode} />}
        </AuthShell>
    );
};

/**
 * Top-level auth entry. Routes to the activation / reset-password views based
 * on the current URL path, otherwise shows the login/register/forgot card.
 */
export const AuthView: React.FC = () => {
    const path = window.location.pathname;
    if (path === '/activate') return <ActivationView />;
    if (path === '/reset-password') return <ResetPasswordView />;
    return <AuthCard />;
};
