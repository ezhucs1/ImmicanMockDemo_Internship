import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { io } from "socket.io-client";

const API = import.meta.env.VITE_API_URL || "http://localhost:5001";

export default function Conversation({ user }) {
  const { requestId } = useParams();
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [socket, setSocket] = useState(null);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    loadConversation();
    
    // Initialize WebSocket connection
    const newSocket = io(API);
    setSocket(newSocket);
    
    return () => {
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, [user, requestId, navigate]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle WebSocket events
  useEffect(() => {
    if (!socket || !conversation) return;

    // Join conversation room when conversation is loaded
    socket.emit('join_conversation', {
      conversation_id: conversation.id,
      user_id: user.id
    });

    // Listen for new messages
    socket.on('new_message', (message) => {
      setMessages(prev => [...prev, message]);
      // Mark message as read if it's not from current user
      if (message.sender_id !== user.id) {
        markMessageAsRead(message.id);
      }
    });

    // Listen for errors
    socket.on('error', (error) => {
      setError(error.message);
    });

    // Listen for successful join
    socket.on('joined_conversation', (data) => {
      console.log('Joined conversation:', data.conversation_id);
    });

    return () => {
      if (conversation) {
        socket.emit('leave_conversation', {
          conversation_id: conversation.id
        });
      }
      socket.off('new_message');
      socket.off('error');
      socket.off('joined_conversation');
    };
  }, [socket, conversation, user.id]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  async function loadConversation() {
    try {
      setLoading(true);
      
      // First, get the conversation ID for this service request
      const conversationRes = await fetch(`${API}/api/service-requests/${requestId}/conversation`);
      const conversationData = await conversationRes.json();
      
      if (conversationData.ok) {
        setConversation(conversationData.conversation);
        
        // Load messages using the real conversation ID
        const messagesRes = await fetch(`${API}/api/conversations/${conversationData.conversation.id}/messages`);
        const messagesData = await messagesRes.json();
        if (messagesData.ok) {
          setMessages(messagesData.messages);
          
          // Mark unread messages as read
          const unreadMessages = messagesData.messages.filter(msg => 
            !msg.is_read && msg.sender_id !== user.id
          );
          
          for (const message of unreadMessages) {
            try {
              await fetch(`${API}/api/conversations/${conversationData.conversation.id}/messages/${message.id}/read`, {
                method: "PUT"
              });
            } catch (err) {
              console.warn("Failed to mark message as read:", err);
            }
          }
        } else {
          setError("Failed to load messages");
        }
      } else {
        setError("Conversation not found. The service request may not have been accepted yet.");
      }
    } catch (err) {
      setError(`Failed to load conversation: ${String(err)}`);
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage() {
    if (!newMessage.trim() || !conversation || !socket) return;

    try {
      setSending(true);
      
      // Send message via WebSocket
      socket.emit('send_message', {
        conversation_id: conversation.id,
        sender_id: user.id,
        sender_type: user.user_type === "ServiceProvider" ? "PROVIDER" : "CLIENT",
        message_text: newMessage.trim()
      });
      
      setNewMessage("");
    } catch (err) {
      setError(`Network error: ${String(err)}`);
    } finally {
      setSending(false);
    }
  }

  function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center">
              <button
                onClick={() => navigate(-1)}
                className="mr-4 text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
              <h1 className="text-xl font-semibold text-gray-900">Conversation</h1>
            </div>
            <div className="text-sm text-gray-500">
              Service Request #{requestId}
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length > 0 ? (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender_id === user.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-900 border border-gray-200'
                  } ${!message.is_read && message.sender_id !== user.id ? 'ring-2 ring-blue-300' : ''}`}
                >
                  <p className="text-sm">{message.message_text}</p>
                  <p className={`text-xs mt-1 ${
                    message.sender_id === user.id ? 'text-indigo-200' : 'text-gray-500'
                  }`}>
                    {new Date(message.created_date).toLocaleString()}
                    {!message.is_read && message.sender_id !== user.id && (
                      <span className="ml-2 text-blue-500">●</span>
                    )}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center text-gray-500 py-8">
              <p>No messages yet. Start the conversation!</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="bg-white border-t p-4">
          <div className="flex space-x-4">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
              rows="2"
              disabled={sending}
            />
            <button
              onClick={sendMessage}
              disabled={sending || !newMessage.trim()}
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sending ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
