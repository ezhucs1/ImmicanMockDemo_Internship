import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_URL || "http://localhost:5001";

// Helper function to get auth headers
function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token && { "Authorization": `Bearer ${token}` })
  };
}

export default function Dashboard({ user, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [serviceRequests, setServiceRequests] = useState([]);
  const [serviceProviders, setServiceProviders] = useState([]);
  const [showServiceRequestForm, setShowServiceRequestForm] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [requestForm, setRequestForm] = useState({
    title: "",
    description: "",
    priority: "MEDIUM"
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    loadDashboardData();
  }, [user, navigate]);

  async function loadDashboardData() {
    try {
      setLoading(true);
      
      // Load user profile
      const profileRes = await fetch(`${API}/api/users/${user.id}/profile`, {
        headers: getAuthHeaders()
      });
      const profileData = await profileRes.json();
      if (profileData.ok) {
        setProfile(profileData.profile);
      }

      // Load service requests
      const requestsRes = await fetch(`${API}/api/users/${user.id}/service-requests`, {
        headers: getAuthHeaders()
      });
      const requestsData = await requestsRes.json();
      if (requestsData.ok) {
        setServiceRequests(requestsData.requests);
      }

      // Load service providers
      const providersRes = await fetch(`${API}/api/service-providers`, {
        headers: getAuthHeaders()
      });
      const providersData = await providersRes.json();
      if (providersData.ok) {
        setServiceProviders(providersData.providers);
      }
    } catch (err) {
      setError(`Failed to load dashboard data: ${String(err)}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleServiceRequest(e) {
    e.preventDefault();
    if (!selectedProvider) return;

    try {
      const res = await fetch(`${API}/api/service-requests`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          user_id: user.id,
          provider_id: selectedProvider.id,
          service_type: selectedProvider.service_type,
          title: requestForm.title,
          description: requestForm.description,
          priority: requestForm.priority
        })
      });

      const data = await res.json();
      if (data.ok) {
        setShowServiceRequestForm(false);
        setSelectedProvider(null);
        setRequestForm({ title: "", description: "", priority: "MEDIUM" });
        loadDashboardData(); // Refresh data
        alert("Service request submitted successfully!");
      } else {
        setError(data.msg || "Failed to submit service request");
      }
    } catch (err) {
      setError(`Network error: ${String(err)}`);
    }
  }

  async function handleConfirmCompletion(requestId) {
    console.log("handleConfirmCompletion called with:", { requestId, rating, userId: user.id });
    
    if (rating === 0) {
      setError("Please provide a rating before confirming completion");
      return;
    }

    try {
      console.log("Making API call to confirm completion...");
      const res = await fetch(`${API}/api/service-requests/${requestId}/confirm`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          user_id: user.id,
          rating: rating
        })
      });

      console.log("API response status:", res.status);
      const data = await res.json();
      console.log("API response data:", data);
      
      if (data.ok) {
        setShowConfirmModal(false);
        setSelectedRequest(null);
        setRating(0);
        setHoverRating(0);
        loadDashboardData(); // Refresh data
        alert("Thank you for confirming! Your rating has been recorded.");
      } else {
        setError(data.msg || "Failed to confirm completion");
      }
    } catch (err) {
      console.error("Error in handleConfirmCompletion:", err);
      setError(`Network error: ${String(err)}`);
    }
  }

  function handleLogout() {
    localStorage.removeItem("user");
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    onLogout();
    navigate("/");
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">immiCan</h1>
              <span className="ml-4 text-gray-500">Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {profile?.first_name || (user.full_name ? user.full_name.split(' ')[0] : user.email)}
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Profile</h2>
              {profile ? (
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Name:</span>
                    <p className="text-gray-900">
                      {profile.first_name} {profile.last_name}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Email:</span>
                    <p className="text-gray-900">{profile.email}</p>
                  </div>
                  {profile.phone && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Phone:</span>
                      <p className="text-gray-900">{profile.phone}</p>
                    </div>
                  )}
                  {profile.country_residence && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Country:</span>
                      <p className="text-gray-900">{profile.country_residence}</p>
                    </div>
                  )}
                  {profile.desired_destination && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Destination:</span>
                      <p className="text-gray-900">{profile.desired_destination}</p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">Profile information not available</p>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Service Requests */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Your Service Requests</h2>
              </div>

              {serviceRequests.length > 0 ? (
                <div className="space-y-4">
                  {serviceRequests.map((request) => (
                    <div key={request.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-medium text-gray-900">{request.title}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          request.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                          request.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                          request.status === 'ACCEPTED' ? 'bg-green-100 text-green-800' :
                          request.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {request.status}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-2">{request.description}</p>
                      <div className="flex justify-between items-center text-sm text-gray-500">
                        <span>Provider: {request.provider.name}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          request.priority === 'URGENT' ? 'bg-red-100 text-red-800' :
                          request.priority === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                          request.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          Priority: {request.priority}
                        </span>
                        <span>Requested: {new Date(request.requested_date).toLocaleDateString()}</span>
                      </div>
                      {request.status === 'ACCEPTED' && (
                        <div className="mt-3">
                          <button
                            onClick={() => navigate(`/conversation/${request.id}`)}
                            className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                          >
                            Open Conversation
                          </button>
                        </div>
                      )}
                      {request.status === 'COMPLETED' && (
                        <div className="mt-3">
                          <div className="flex space-x-2 mb-2">
                            <button
                              onClick={() => navigate(`/conversation/${request.id}`)}
                              className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                            >
                              View Conversation
                            </button>
                            <button
                              onClick={() => {
                                setSelectedRequest(request);
                                setError(""); // Clear any previous errors
                                setShowConfirmModal(true);
                              }}
                              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                            >
                              Confirm Completion
                            </button>
                          </div>
                          <p className="text-sm text-gray-500">
                            Service completed on {new Date(request.completed_date).toLocaleDateString()}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No service requests yet. Click "Request Service" to get started.</p>
              )}
            </div>

            {/* Available Services */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Service Providers</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {serviceProviders.map((provider) => (
                  <div key={provider.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <h3 className="font-medium text-gray-900 mb-2">{provider.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{provider.description}</p>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-indigo-600 font-medium">{provider.service_type}</span>
                      <div className="flex items-center">
                        <span className="text-yellow-500" style={{color: '#eab308 !important'}}>★</span>
                        <span className="ml-1 text-gray-600">{provider.rating.toFixed(1)}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedProvider(provider);
                        setShowServiceRequestForm(true);
                      }}
                      className="mt-3 w-full bg-indigo-600 text-white py-2 px-3 rounded text-sm hover:bg-indigo-700"
                    >
                      Request Service
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Service Request Modal */}
      {showServiceRequestForm && selectedProvider && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Request Service from {selectedProvider.name}
            </h3>
            <form onSubmit={handleServiceRequest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Service Type
                </label>
                <p className="text-gray-900">{selectedProvider.service_type}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={requestForm.title}
                  onChange={(e) => setRequestForm({...requestForm, title: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Brief description of your request"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={requestForm.description}
                  onChange={(e) => setRequestForm({...requestForm, description: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows="3"
                  placeholder="Provide more details about your request"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  value={requestForm.priority}
                  onChange={(e) => setRequestForm({...requestForm, priority: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="LOW">Priority: Low</option>
                  <option value="MEDIUM">Priority: Medium</option>
                  <option value="HIGH">Priority: High</option>
                  <option value="URGENT">Priority: Urgent</option>
                </select>
              </div>
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowServiceRequestForm(false);
                    setSelectedProvider(null);
                    setRequestForm({ title: "", description: "", priority: "MEDIUM" });
                  }}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirm Completion Modal */}
      {showConfirmModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Confirm Service Completion
            </h3>
            <p className="text-gray-600 mb-4">
              Please confirm that the service "<strong>{selectedRequest.title}</strong>" has been completed to your satisfaction.
            </p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Rate your experience with {selectedRequest.provider?.name}:
              </label>
              <div className="flex items-center space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    className="text-2xl focus:outline-none"
                  >
                    <span className={`${(hoverRating >= star || rating >= star) ? 'text-yellow-500' : 'text-gray-300'}`}>
                      ★
                    </span>
                  </button>
                ))}
                <span className="ml-2 text-sm text-gray-600">
                  {rating > 0 && `${rating} star${rating > 1 ? 's' : ''}`}
                </span>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowConfirmModal(false);
                  setSelectedRequest(null);
                  setRating(0);
                  setHoverRating(0);
                  setError(""); // Clear error when closing modal
                }}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  console.log("Confirm & Rate button clicked");
                  handleConfirmCompletion(selectedRequest.id);
                }}
                disabled={rating === 0}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Confirm & Rate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
