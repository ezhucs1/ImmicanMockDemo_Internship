import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_URL || "http://localhost:5001";

export default function ServiceProviderDashboard({ user, onLogout }) {
  const [serviceRequests, setServiceRequests] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showAcceptModal, setShowAcceptModal] = useState(false);
  const [acceptNotes, setAcceptNotes] = useState("");
  const [providerProfile, setProviderProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (!user || user.user_type !== "ServiceProvider") {
      navigate("/service-provider-login");
      return;
    }
    loadDashboardData();
  }, [user, navigate]);

  async function loadDashboardData() {
    try {
      setLoading(true);
      
      // First, get the provider profile for this user
      const profileRes = await fetch(`${API}/api/users/${user.id}/provider-profile`);
      const profileData = await profileRes.json();
      if (profileData.ok) {
        setProviderProfile(profileData.provider);
        
        // Load service requests using the actual provider ID
        const requestsRes = await fetch(`${API}/api/service-providers/${profileData.provider.id}/requests`);
        const requestsData = await requestsRes.json();
        if (requestsData.ok) {
          setServiceRequests(requestsData.requests);
        }

        // Load conversations using the actual provider ID
        const conversationsRes = await fetch(`${API}/api/service-providers/${profileData.provider.id}/conversations`);
        const conversationsData = await conversationsRes.json();
        if (conversationsData.ok) {
          setConversations(conversationsData.conversations);
        }
      } else {
        setError("Provider profile not found. Please contact support.");
      }
    } catch (err) {
      setError(`Failed to load dashboard data: ${String(err)}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleAcceptRequest(requestId) {
    try {
      const res = await fetch(`${API}/api/service-requests/${requestId}/accept`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider_id: providerProfile?.id,
          notes: acceptNotes
        })
      });

      const data = await res.json();
      if (data.ok) {
        setShowAcceptModal(false);
        setSelectedRequest(null);
        setAcceptNotes("");
        loadDashboardData(); // Refresh data
        alert("Service request accepted! A conversation has been created for messaging.");
      } else {
        setError(data.msg || "Failed to accept request");
      }
    } catch (err) {
      setError(`Network error: ${String(err)}`);
    }
  }

  function handleLogout() {
    localStorage.removeItem("user");
    localStorage.removeItem("isAuthenticated");
    onLogout();
    navigate("/service-provider-login");
  }

  function getStatusColor(status) {
    switch (status) {
      case 'PENDING': return 'bg-yellow-100 text-yellow-800';
      case 'ACCEPTED': return 'bg-green-100 text-green-800';
      case 'IN_PROGRESS': return 'bg-blue-100 text-blue-800';
      case 'COMPLETED': return 'bg-gray-100 text-gray-800';
      case 'CANCELLED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
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
              <span className="ml-4 text-gray-500">Service Provider Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {providerProfile?.name || user.email}
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
          {/* Service Requests */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Service Requests</h2>
              
              {serviceRequests.length > 0 ? (
                <div className="space-y-4">
                  {serviceRequests.map((request) => (
                    <div key={request.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-medium text-gray-900">{request.title}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                          {request.status}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-2">{request.description}</p>
                      <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
                        <span>Client: {request.client.name}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          request.priority === 'URGENT' ? 'bg-red-100 text-red-800' :
                          request.priority === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                          request.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {request.priority}
                        </span>
                        <span>Requested: {new Date(request.requested_date).toLocaleDateString()}</span>
                      </div>
                      {request.status === 'PENDING' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setShowAcceptModal(true);
                            }}
                            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                          >
                            Accept Request
                          </button>
                          <button
                            onClick={() => navigate(`/conversation/${request.id}`)}
                            className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                          >
                            View Details
                          </button>
                        </div>
                      )}
                      {request.status === 'ACCEPTED' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => navigate(`/conversation/${request.id}`)}
                            className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                          >
                            Open Conversation
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No service requests yet.</p>
              )}
            </div>
          </div>

          {/* Conversations */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Conversations</h2>
              
              {conversations.length > 0 ? (
                <div className="space-y-3">
                  {conversations.map((conversation) => (
                    <div key={conversation.id} className="border rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer"
                         onClick={() => navigate(`/conversation/${conversation.service_request_id}`)}>
                      <h4 className="font-medium text-gray-900 text-sm">{conversation.request_title}</h4>
                      <p className="text-gray-600 text-xs mb-1">Client: {conversation.client.name}</p>
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span className={`px-2 py-1 rounded-full ${getStatusColor(conversation.request_status)}`}>
                          {conversation.request_status}
                        </span>
                        <span>{new Date(conversation.updated_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No active conversations.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Accept Request Modal */}
      {showAcceptModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Accept Service Request
            </h3>
            <p className="text-gray-600 mb-4">
              You are about to accept the request: <strong>{selectedRequest.title}</strong>
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (optional)
              </label>
              <textarea
                value={acceptNotes}
                onChange={(e) => setAcceptNotes(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                rows="3"
                placeholder="Add any notes about accepting this request..."
              />
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowAcceptModal(false);
                  setSelectedRequest(null);
                  setAcceptNotes("");
                }}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={() => handleAcceptRequest(selectedRequest.id)}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700"
              >
                Accept Request
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
