import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_URL || "http://localhost:5001";

const HERO = "https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1920&auto=format&fit=crop";

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

const LANGS = ["English", "Français", "Español", "中文"];

// Language translations
const translations = {
  English: {
    title: "Welcome to immiCan",
    subtitle: "Your gateway to Canadian immigration services",
    signIn: "Sign In",
    createAccount: "Create Account",
    firstName: "First Name",
    lastName: "Last Name",
    email: "Email Address",
    password: "Password",
    confirmPassword: "Confirm Password",
    country: "Country of Origin",
    preferredLanguage: "Preferred Language",
    agreeTerms: "I agree to the Terms and Conditions and Privacy Policy",
    registerButton: "Create Account",
    alreadyHaveAccount: "Already have an account?",
    signInHere: "Sign in here",
    serviceProvider: "Are you a service provider?",
    registerAsProvider: "Register as Service Provider",
    features: {
      title: "Why Choose immiCan?",
      feature1: "Expert guidance through your immigration journey",
      feature2: "Connect with certified immigration professionals",
      feature3: "Multilingual support—choose your preferred language",
      feature4: "24/7 access to resources and updates"
    }
  },
  Français: {
    title: "Bienvenue sur immiCan",
    subtitle: "Votre passerelle vers les services d'immigration canadienne",
    signIn: "Se Connecter",
    createAccount: "Créer un Compte",
    firstName: "Prénom",
    lastName: "Nom de Famille",
    email: "Adresse E-mail",
    password: "Mot de Passe",
    confirmPassword: "Confirmer le Mot de Passe",
    country: "Pays d'Origine",
    preferredLanguage: "Langue Préférée",
    agreeTerms: "J'accepte les Conditions d'Utilisation et la Politique de Confidentialité",
    registerButton: "Créer un Compte",
    alreadyHaveAccount: "Vous avez déjà un compte?",
    signInHere: "Connectez-vous ici",
    serviceProvider: "Êtes-vous un prestataire de services?",
    registerAsProvider: "S'inscrire comme Prestataire de Services",
    features: {
      title: "Pourquoi Choisir immiCan?",
      feature1: "Conseils d'experts pour votre parcours d'immigration",
      feature2: "Connectez-vous avec des professionnels certifiés",
      feature3: "Support multilingue—choisissez votre langue préférée",
      feature4: "Accès 24/7 aux ressources et mises à jour"
    }
  },
  Español: {
    title: "Bienvenido a immiCan",
    subtitle: "Tu puerta de entrada a los servicios de inmigración canadiense",
    signIn: "Iniciar Sesión",
    createAccount: "Crear Cuenta",
    firstName: "Nombre",
    lastName: "Apellido",
    email: "Dirección de Correo",
    password: "Contraseña",
    confirmPassword: "Confirmar Contraseña",
    country: "País de Origen",
    preferredLanguage: "Idioma Preferido",
    agreeTerms: "Acepto los Términos y Condiciones y la Política de Privacidad",
    registerButton: "Crear Cuenta",
    alreadyHaveAccount: "¿Ya tienes una cuenta?",
    signInHere: "Inicia sesión aquí",
    serviceProvider: "¿Eres un proveedor de servicios?",
    registerAsProvider: "Registrarse como Proveedor de Servicios",
    features: {
      title: "¿Por Qué Elegir immiCan?",
      feature1: "Orientación experta en tu viaje de inmigración",
      feature2: "Conéctate con profesionales certificados",
      feature3: "Soporte multilingüe—elige tu idioma preferido",
      feature4: "Acceso 24/7 a recursos y actualizaciones"
    }
  },
  中文: {
    title: "欢迎来到 immiCan",
    subtitle: "您通往加拿大移民服务的门户",
    signIn: "登录",
    createAccount: "创建账户",
    firstName: "名字",
    lastName: "姓氏",
    email: "邮箱地址",
    password: "密码",
    confirmPassword: "确认密码",
    country: "原籍国家",
    preferredLanguage: "首选语言",
    agreeTerms: "我同意服务条款和隐私政策",
    registerButton: "创建账户",
    alreadyHaveAccount: "已有账户？",
    signInHere: "在此登录",
    serviceProvider: "您是服务提供商吗？",
    registerAsProvider: "注册为服务提供商",
    features: {
      title: "为什么选择 immiCan？",
      feature1: "专家指导您的移民之旅",
      feature2: "与认证的移民专业人士联系",
      feature3: "多语言支持—选择您的首选语言",
      feature4: "24/7 访问资源和更新"
    }
  }
};

export default function Register() {
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
  const navigate = useNavigate();

  // Get current translation
  const t = translations[lang] || translations.English;

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
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate("/login")}
                className="bg-white/20 text-white px-4 py-2 rounded-lg text-sm hover:bg-white/30 transition-colors"
              >
                Sign In
              </button>
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
          </div>
        </header>

        <div className="relative z-10 mx-auto max-w-7xl px-5 pt-16 pb-20">
          <h1 className="text-white text-[clamp(1.8rem,5.6vw,3.4rem)] font-semibold leading-tight max-w-3xl">
            {t.title} 👋 {lang === "English" ? "Let's set up your account" : 
                        lang === "Français" ? "Créons votre compte" :
                        lang === "Español" ? "Configuremos tu cuenta" :
                        lang === "中文" ? "让我们设置您的账户" : "Let's set up your account"}
          </h1>
          <p className="mt-3 text-white/85 max-w-2xl">
            {t.subtitle}
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
                It's free and takes less than 2 minutes.
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <Field label={t.firstName}>
                    <input
                      value={firstName}
                      onChange={(e) => setFirst(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 hover:border-slate-400 focus:shadow-sm text-slate-900 placeholder:text-slate-500"
                      autoComplete="given-name"
                      placeholder={lang === "English" ? "Enter your first name" : 
                                lang === "Français" ? "Entrez votre prénom" :
                                lang === "Español" ? "Ingresa tu nombre" :
                                lang === "中文" ? "输入您的名字" : "Enter your first name"}
                      required
                    />
                  </Field>
                  <Field label={t.lastName}>
                    <input
                      value={lastName}
                      onChange={(e) => setLast(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 hover:border-slate-400 focus:shadow-sm text-slate-900 placeholder:text-slate-500"
                      autoComplete="family-name"
                      placeholder={lang === "English" ? "Enter your last name" : 
                                lang === "Français" ? "Entrez votre nom de famille" :
                                lang === "Español" ? "Ingresa tu apellido" :
                                lang === "中文" ? "输入您的姓氏" : "Enter your last name"}
                    />
                  </Field>
                </div>

                <Field label={t.email}>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 hover:border-slate-400 focus:shadow-sm text-slate-900 placeholder:text-slate-500"
                    autoComplete="email"
                    inputMode="email"
                    placeholder={lang === "English" ? "Enter your email" : 
                              lang === "Français" ? "Entrez votre e-mail" :
                              lang === "Español" ? "Ingresa tu correo" :
                              lang === "中文" ? "输入您的邮箱" : "Enter your email"}
                    required
                  />
                  <Help>{lang === "English" ? "We'll send a verification email." : 
                        lang === "Français" ? "Nous enverrons un e-mail de vérification." :
                        lang === "Español" ? "Enviaremos un correo de verificación." :
                        lang === "中文" ? "我们将发送验证邮件。" : "We'll send a verification email."}</Help>
                </Field>

                <Field label={t.password}>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 hover:border-slate-400 focus:shadow-sm text-slate-900 placeholder:text-slate-500"
                    autoComplete="new-password"
                    placeholder={lang === "English" ? "Enter your password" : 
                              lang === "Français" ? "Entrez votre mot de passe" :
                              lang === "Español" ? "Ingresa tu contraseña" :
                              lang === "中文" ? "输入您的密码" : "Enter your password"}
                    required
                  />
                  <Help>{lang === "English" ? "At least 8 characters is best." : 
                        lang === "Français" ? "Au moins 8 caractères est préférable." :
                        lang === "Español" ? "Al menos 8 caracteres es mejor." :
                        lang === "中文" ? "至少8个字符最好。" : "At least 8 characters is best."}</Help>
                </Field>

                <div className="grid sm:grid-cols-2 gap-4">
                  <Field label={t.country}>
                    <select
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 hover:border-slate-400 focus:shadow-sm text-slate-900"
                    >
                      {COUNTRIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </Field>

                  <Field label={t.preferredLanguage}>
                    <select
                      value={prefLang}
                      onChange={(e) => setPrefLang(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 hover:border-slate-400 focus:shadow-sm text-slate-900"
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
                    {lang === "English" ? "I agree to the" : 
                     lang === "Français" ? "J'accepte les" :
                     lang === "Español" ? "Acepto los" :
                     lang === "中文" ? "我同意" : "I agree to the"}{" "}
                    <a className="text-indigo-600 hover:underline" href="#">
                      {lang === "English" ? "Terms" : 
                       lang === "Français" ? "Conditions" :
                       lang === "Español" ? "Términos" :
                       lang === "中文" ? "服务条款" : "Terms"}
                    </a>{" "}
                    {lang === "English" ? "and" : 
                     lang === "Français" ? "et la" :
                     lang === "Español" ? "y la" :
                     lang === "中文" ? "和" : "and"}{" "}
                    <a className="text-indigo-600 hover:underline" href="#">
                      {lang === "English" ? "Privacy Policy" : 
                       lang === "Français" ? "Politique de Confidentialité" :
                       lang === "Español" ? "Política de Privacidad" :
                       lang === "中文" ? "隐私政策" : "Privacy Policy"}
                    </a>.
                  </span>
                </label>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-lg bg-indigo-600 text-white font-medium py-2.5 hover:bg-indigo-700 transition shadow hover:shadow-lg disabled:opacity-60"
                >
                  {loading ? (lang === "English" ? "Creating your account…" : 
                             lang === "Français" ? "Création de votre compte…" :
                             lang === "Español" ? "Creando tu cuenta…" :
                             lang === "中文" ? "正在创建您的账户…" : "Creating your account…") : 
                            t.registerButton}
                </button>

                {result && (
                  <p className="mt-2 text-slate-700 whitespace-pre-wrap">{result}</p>
                )}
              </form>

              {/* Login Link */}
              <div className="mt-6 text-center">
                <p className="text-sm text-slate-600">
                  {t.alreadyHaveAccount}{" "}
                  <button
                    onClick={() => navigate("/login")}
                    className="text-indigo-600 hover:text-indigo-700 font-medium cursor-pointer hover:underline transition-colors"
                  >
                    {t.signInHere}
                  </button>
                </p>
                <p className="text-sm text-slate-600 mt-2">
                  {t.serviceProvider}{" "}
                  <button
                    onClick={() => navigate("/service-provider-register")}
                    className="text-green-600 hover:text-green-700 font-medium cursor-pointer hover:underline transition-colors"
                  >
                    {t.registerAsProvider}
                  </button>
                </p>
              </div>
            </div>

            {/* Reassurance / Help */}
            <aside className="rounded-2xl bg-white/70 backdrop-blur shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-2">We're here to help</h3>
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
  return <p className="mt-1 text-xs text-slate-400">{children}</p>;
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
