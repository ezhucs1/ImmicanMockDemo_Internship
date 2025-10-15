import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_URL || "http://localhost:5001";

export default function ServiceProviderRegister() {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    name: "",
    email: "",
    password: "",
    phone: "",
    address: "",
    service_type: "",
    description: "",
    website: ""
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const navigate = useNavigate();
  
  // Password strength checker
  const [passwordChecks, setPasswordChecks] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false
  });

  const serviceTypes = [
    "Legal",
    "Medical", 
    "Education",
    "Employment",
    "Housing",
    "Other"
  ];
  
  // Password validation function
  const validatePassword = (pwd) => {
    const checks = {
      length: pwd.length >= 8,
      uppercase: /[A-Z]/.test(pwd),
      lowercase: /[a-z]/.test(pwd),
      number: /\d/.test(pwd),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(pwd)
    };
    setPasswordChecks(checks);
    return checks;
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setResult("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/api/service-providers/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (data.ok) {
        setResult("✅ Service provider account created successfully! You can now login.");
        setFormData({
          first_name: "",
          last_name: "",
          name: "",
          email: "",
          password: "",
          phone: "",
          address: "",
          service_type: "",
          description: "",
          website: ""
        });
        setTimeout(() => {
          navigate("/service-provider-login");
        }, 2000);
      } else {
        setResult(`❌ ${data.msg || "Could not create service provider account"}`);
      }
    } catch (err) {
      setResult(`❌ Network error: ${String(err)}`);
    } finally {
      setLoading(false);
    }
  }

  function handleChange(e) {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  }

  return (
    <div className="min-h-screen w-full text-slate-900">
      <div className="flex min-h-screen">
        {/* Left side - Form */}
        <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-20 xl:px-24">
          <div className="max-w-md w-full space-y-8">
            <div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
                Register as Service Provider
              </h2>
              <p className="mt-2 text-center text-sm text-gray-200">
                Join our platform to help newcomers
              </p>
            </div>
            
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      First Name *
                    </label>
                    <input
                      name="first_name"
                      type="text"
                      required
                      value={formData.first_name}
                      onChange={handleChange}
                      className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                      placeholder="Your first name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Last Name *
                    </label>
                    <input
                      name="last_name"
                      type="text"
                      required
                      value={formData.last_name}
                      onChange={handleChange}
                      className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                      placeholder="Your last name"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Business Name *
                  </label>
                  <input
                    name="name"
                    type="text"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="Your business or organization name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Email Address *
                  </label>
                  <input
                    name="email"
                    type="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="your@email.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Password *
                  </label>
                  <input
                    name="password"
                    type="password"
                    required
                    value={formData.password}
                    onChange={(e) => {
                      handleChange(e);
                      validatePassword(e.target.value);
                    }}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="Create a secure password"
                  />
                  
                  {/* Password Requirements Checklist */}
                  <div className="mt-2 space-y-1">
                    <div className={`flex items-center text-xs ${passwordChecks.length ? 'text-green-600' : 'text-slate-500'}`}>
                      <span className="mr-2">{passwordChecks.length ? '✓' : '○'}</span>
                      At least 8 characters
                    </div>
                    <div className={`flex items-center text-xs ${passwordChecks.uppercase ? 'text-green-600' : 'text-slate-500'}`}>
                      <span className="mr-2">{passwordChecks.uppercase ? '✓' : '○'}</span>
                      One uppercase letter
                    </div>
                    <div className={`flex items-center text-xs ${passwordChecks.lowercase ? 'text-green-600' : 'text-slate-500'}`}>
                      <span className="mr-2">{passwordChecks.lowercase ? '✓' : '○'}</span>
                      One lowercase letter
                    </div>
                    <div className={`flex items-center text-xs ${passwordChecks.number ? 'text-green-600' : 'text-slate-500'}`}>
                      <span className="mr-2">{passwordChecks.number ? '✓' : '○'}</span>
                      One number
                    </div>
                    <div className={`flex items-center text-xs ${passwordChecks.special ? 'text-green-600' : 'text-slate-500'}`}>
                      <span className="mr-2">{passwordChecks.special ? '✓' : '○'}</span>
                      One special character
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Service Type *
                  </label>
                  <select
                    name="service_type"
                    required
                    value={formData.service_type}
                    onChange={handleChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    <option value="">Select a service type</option>
                    {serviceTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <input
                    name="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={handleChange}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Address
                  </label>
                  <input
                    name="address"
                    type="text"
                    value={formData.address}
                    onChange={handleChange}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="123 Main St, City, Province"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Website
                  </label>
                  <input
                    name="website"
                    type="url"
                    value={formData.website}
                    onChange={handleChange}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="https://yourwebsite.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    name="description"
                    rows="3"
                    value={formData.description}
                    onChange={handleChange}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="Describe your services and expertise..."
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {loading ? "Creating Account..." : "Register as Service Provider"}
                </button>
              </div>

              {result && (
                <div className={`text-center text-sm ${result.includes("✅") ? "text-green-600" : "text-red-600"}`}>
                  {result}
                </div>
              )}

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => navigate("/service-provider-login")}
                  className="text-indigo-600 hover:text-indigo-700 font-medium cursor-pointer hover:underline transition-colors text-sm"
                >
                  Already have an account? Sign in
                </button>
              </div>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => navigate("/")}
                  className="text-gray-200 hover:text-white font-medium cursor-pointer hover:underline transition-colors text-sm"
                >
                  Back to Client Registration
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right side - Image/Info */}
        <div className="hidden lg:block relative w-0 flex-1">
          <div className="absolute inset-0 h-full w-full bg-gradient-to-br from-indigo-500 to-purple-600">
            <div className="flex items-center justify-center h-full p-12">
              <div className="text-center text-white">
                <h1 className="text-4xl font-bold mb-4">immiCan</h1>
                <p className="text-xl mb-8">Connecting Newcomers with Service Providers</p>
                <div className="space-y-4 text-left max-w-md">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                      <span className="text-white font-bold">1</span>
                    </div>
                    <span>Register your service business</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                      <span className="text-white font-bold">2</span>
                    </div>
                    <span>Receive service requests from clients</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                      <span className="text-white font-bold">3</span>
                    </div>
                    <span>Communicate and provide services</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
