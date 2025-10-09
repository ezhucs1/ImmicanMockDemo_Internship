import { useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:5001";

const HERO =
  //"/welcome.jpg"; // place your own image in public/welcome.jpg
  // If you don't have one yet, you can replace with:
  "https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1920&auto=format&fit=crop";

const COUNTRIES = [
  "Canada",
  "United States",
  "United Kingdom",
  "Australia",
  "India",
  "Philippines",
  "Nigeria",
  "Pakistan",
  "Bangladesh",
  "China",
  "Brazil",
  "Mexico",
  "Other",
];

const LANGS = ["English", "Français", "Español", "العربية", "中文", "فارسی", "हिन्दी", "اردو", "Tagalog"];

export default function App() {
  const [lang, setLang] = useState("English");
  const [firstName, setFirst] = useState("");
  const [lastName, setLast] = useState("");
  const [email, setEmail] = useState("");
  const [country, setCountry] = useState("Canada");
  const [prefLang, setPrefLang] = useState("English");
  const [password, setPassword] = useState("");
  const [agree, setAgree] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [userId, setUserId] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setResult("");
    if (!agree) {
      setResult("Please agree to the terms to continue.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // backend expects: email, full_name, password
        body: JSON.stringify({
          email,
          full_name: [firstName, lastName].filter(Boolean).join(" ").trim(),
          password,
        }),
      });
      const data = await res.json();
      if (data.ok) {
        setUserId(data.user.id);
        setResult("✅ Thanks! Please check your email to verify your account.");
        setFirst(""); setLast(""); setEmail(""); setPassword(""); setAgree(false);
      } else {
        setResult(`❌ ${data.msg || "Could not create account"}`);
      }
    } catch (err) {
      setResult(`❌ Network error: ${String(err)}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full text-slate-900">
      {/* HERO */}
      <section className="relative min-h-[52svh]">
        <img
          src={HERO}
          alt="Welcome"
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-black/50" />
        <header className="relative z-10">
          <div className="mx-auto max-w-7xl px-5 pt-5 flex items-center justify-between">
            <div className="text-white/90 font-semibold">immiCan</div>
            {/* Language switch (UI only for now) */}
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="rounded-lg bg-white/90 text-slate-900 px-3 py-2 text-sm"
            >
              {LANGS.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>
        </header>

        <div className="relative z-10 mx-auto max-w-7xl px-5 pt-16 pb-20">
          <h1 className="text-white text-[clamp(1.8rem,5.6vw,3.4rem)] font-semibold leading-tight max-w-3xl">
            Welcome 👋 Let’s set up your account
          </h1>
          <p className="mt-3 text-white/85 max-w-2xl">
            Create your profile so we can share helpful services and next steps for your Canadian journey.
          </p>

          {/* Steps */}
          <div className="mt-6 flex flex-wrap items-center gap-4 text-white/85">
            <StepBadge num="1" label="Create account" active />
            <StepBadge num="2" label="Verify email" />
            <StepBadge num="3" label="Start" />
          </div>
        </div>
      </section>

      {/* FORM CARD */}
      <main className="-mt-24 relative z-20">
        <div className="mx-auto max-w-5xl px-5">
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="rounded-2xl bg-white shadow-xl p-6">
              <h2 className="text-xl font-semibold mb-1">Immigrant Sign Up</h2>
              <p className="text-slate-600 mb-5">
                It’s free and takes less than 2 minutes.
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <Field label="First name">
                    <input
                      value={firstName}
                      onChange={(e) => setFirst(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500"
                      autoComplete="given-name"
                      required
                    />
                  </Field>
                  <Field label="Last name">
                    <input
                      value={lastName}
                      onChange={(e) => setLast(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500"
                      autoComplete="family-name"
                    />
                  </Field>
                </div>

                <Field label="Email">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500"
                    autoComplete="email"
                    inputMode="email"
                    required
                  />
                  <Help>We’ll send a verification email.</Help>
                </Field>

                <Field label="Password">
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500"
                    autoComplete="new-password"
                    required
                  />
                  <Help>At least 8 characters is best.</Help>
                </Field>

                <div className="grid sm:grid-cols-2 gap-4">
                  <Field label="Country of residence">
                    <select
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500"
                    >
                      {COUNTRIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </Field>

                  <Field label="Preferred language">
                    <select
                      value={prefLang}
                      onChange={(e) => setPrefLang(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500"
                    >
                      {LANGS.map((l) => (
                        <option key={l} value={l}>{l}</option>
                      ))}
                    </select>
                  </Field>
                </div>

                <label className="flex items-start gap-3 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={agree}
                    onChange={(e) => setAgree(e.target.checked)}
                    className="mt-1 size-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span>
                    I agree to the <a className="text-indigo-600 hover:underline" href="#">Terms</a> and{" "}
                    <a className="text-indigo-600 hover:underline" href="#">Privacy Policy</a>.
                  </span>
                </label>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-lg bg-indigo-600 text-white font-medium py-2.5 hover:bg-indigo-700 transition shadow hover:shadow-lg disabled:opacity-60"
                >
                  {loading ? "Creating your account…" : "Create account"}
                </button>

                {result && (
                  <p className="mt-2 text-slate-700 whitespace-pre-wrap">{result}</p>
                )}
              </form>
            </div>

            {/* Reassurance / Help */}
            <aside className="rounded-2xl bg-white/70 backdrop-blur shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-2">We’re here to help</h3>
              <ul className="space-y-3 text-slate-700">
                <li className="flex gap-3">
                  <span className="mt-0.5 inline-flex size-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">✓</span>
                  Your information is private and secure.
                </li>
                <li className="flex gap-3">
                  <span className="mt-0.5 inline-flex size-6 items-center justify-center rounded-full bg-blue-100 text-blue-700">🌍</span>
                  Multilingual support—choose your preferred language.
                </li>
                <li className="flex gap-3">
                  <span className="mt-0.5 inline-flex size-6 items-center justify-center rounded-full bg-amber-100 text-amber-700">⏱</span>
                  Sign up in under 2 minutes.
                </li>
              </ul>

              {userId ? (
                <div className="mt-6 rounded-xl border border-slate-200 p-4">
                  <p className="font-medium">Next step</p>
                  <p className="text-slate-600 mt-1">
                    Check your email to verify your account. Once verified, you can start your onboarding.
                  </p>
                  <p className="text-xs text-slate-500 mt-2">Your user ID: {userId}</p>
                </div>
              ) : (
                <div className="mt-6 rounded-xl border border-slate-200 p-4">
                  <p className="font-medium">Need help?</p>
                  <p className="text-slate-600 mt-1">Email us at <a className="text-indigo-600 hover:underline" href="mailto:NotRealEmail@Don't.send.anything">NotRealEmail@Don't.send.anything</a></p>
                </div>
              )}
            </aside>
          </div>

          {/* Friendly small print */}
          <p className="text-xs text-slate-600 mt-6 mb-10">
            By creating an account you agree that immiCan may contact you about services relevant to your journey.
            You can change your preferences anytime.
          </p>
        </div>
      </main>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="block text-sm text-slate-600 mb-1">{label}</span>
      {children}
    </label>
  );
}

function Help({ children }) {
  return <p className="mt-1 text-xs text-slate-500">{children}</p>;
}

function StepBadge({ num, label, active }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={
          "inline-flex size-7 items-center justify-center rounded-full border " +
          (active
            ? "bg-white text-slate-900 border-white"
            : "bg-white/10 text-white/90 border-white/30")
        }
      >
        {num}
      </span>
      <span className="text-white/85">{label}</span>
    </div>
  );
}
