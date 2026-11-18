
import { useState, useRef, useEffect } from 'react';
import './App.css';
const API_BASE_URL = import.meta.env.VITE_API_URL;
import { FiUploadCloud, FiPlus, FiSearch, FiSettings, FiPaperclip, FiFileText, FiMoreVertical, FiX } from 'react-icons/fi';
import Login from './Login'; 

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'ai', text: "Hello, I am your AI document assistant. Please upload a PDF to get started." }
  ]);
  const [input, setInput] = useState('');
  const [fileUploaded, setFileUploaded] = useState(false);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  
  // State for Menu & Modals
  const [showMenu, setShowMenu] = useState(false);
  const [activeModal, setActiveModal] = useState(null); // 'settings' | 'credentials' | 'help' | 'privacy'
  
  const menuRef = useRef(null);
  const fileInputRef = useRef(null);

  // Close dropdown if clicked outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuRef]);

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  // --- HELPER: GET JWT TOKEN ---
  const getToken = () => localStorage.getItem('access_token');

  


 const handleNewConversation = async () => {
   try {
    // Tell backend to clear memory
     await fetch(`${API_BASE_URL}/api/clear/`, {
       method: 'POST',
       headers: { 'Authorization': `Bearer ${getToken()}` }
     });
    
    // Reset frontend state
     setFileUploaded(false);
     setFileName('');
     setMessages([{ type: 'ai', text: "New session started. Please upload a PDF to get started." }]);
     setInput('');
   } catch (err) {
     console.error("Failed to clear memory", err);
   }
  };


  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
  };

  const handlePaperclipClick = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  // --- FILE UPLOAD LOGIC (Now sends Token) ---
  const handleFileUpload = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  setLoading(true);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE_URL}/api/upload/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
      body: formData,
    });

    const data = await res.json();

    if (res.ok) {
      setFileUploaded(true);
      setFileName(file.name);

      setMessages((prev) => [
        ...prev,
        {
          type: 'ai',
          text: `Document "${file.name}" processed successfully! What would you like to know?`
        }
      ]);
    } else {
      setMessages((prev) => [
        ...prev,
        {
          type: 'ai',
          text: `Error: ${data.detail || data.error || 'Upload failed'}`
        }
      ]);
    }

  } catch (err) {
    console.error("UPLOAD ERROR:", err);

    setMessages((prev) => [
      ...prev,
      {
        type: 'ai',
        text: `Upload failed: ${err.message}
        | API URL: ${API_BASE_URL}`
      }
    ]);

  } finally {
    setLoading(false);
  }
};


  // --- SEND CHAT LOGIC (Now sends Token) ---
  const handleSend = async () => {
    if (!input.trim() || !fileUploaded) return;

    const userMsg = { type: 'user', text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/ask/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}` // <--- JWT TOKEN ADDED
        },
        body: JSON.stringify({ question: userMsg.text }),
      });
      const data = await res.json();
      
      if (res.ok) {
        setMessages((prev) => [...prev, { type: 'ai', text: data.answer }]);
      } else {
        setMessages((prev) => [...prev, { type: 'ai', text: `Error: ${data.detail || data.error}` }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { type: 'ai', text: "Failed to get an answer. Check backend connection." }]);
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      
      {/* SIDEBAR */}
      <div className="sidebar">
        <div className="sidebar-header">
          <FiFileText color="#2563eb" size={24} /> AskYourPDF
        </div>
        
        <button className="new-chat-btn" onClick={handleNewConversation}>
          <FiPlus /> New Conversation
        </button>
        
        <div className="history-list">
          {fileUploaded ? (
            <>
              <p className="history-title">Current Document</p>
              <button className="history-item">{fileName}</button> 
            </>
          ) : (
            <p className="history-title" style={{ textAlign: 'center', marginTop: '20px' }}>No documents yet.</p>
          )}
        </div>

        <button className="sidebar-footer" onClick={() => setActiveModal('settings')}>
          <FiSettings size={18} /> Settings
        </button>
      </div>

      {/* MAIN CONTENT */}
      <div className="main-content">
        
        {/* TOPBAR */}
        <div className="topbar">
          <div className="topbar-title">Document Analysis</div>
          <div className="topbar-actions">
            
            <button className="btn-logout" onClick={handleLogout}>Logout</button>
            <button className="btn-credentials" onClick={() => setActiveModal('credentials')}>My Credentials</button>
            
            {/* THREE DOTS MENU */}
            <div className="menu-container" ref={menuRef} style={{ position: 'relative' }}>
              <button className="icon-btn" onClick={() => setShowMenu(!showMenu)}>
                <FiMoreVertical size={20} />
              </button>
              
              {showMenu && (
                <div className="dropdown-menu">
                  <button className="dropdown-item" onClick={() => { setActiveModal('help'); setShowMenu(false); }}>Help Center</button>
                  <button className="dropdown-item" onClick={() => { setActiveModal('privacy'); setShowMenu(false); }}>Privacy Policy</button>
                </div>
              )}
            </div>

          </div>
        </div>

        {/* WORKSPACE */}
        <div className="workspace">
          
          <div className="pdf-panel">
             <div className="upload-area">
                <FiUploadCloud size={50} color="#9ca3af" style={{ marginBottom: '15px' }} />
                <h2>{fileUploaded ? "Document Ready" : "Upload a PDF"}</h2>
                <p>{fileUploaded ? fileName : "Select a document to analyze"}</p>
                
                <input type="file" id="fileUpload" ref={fileInputRef} className="hidden-file-input" accept=".pdf" onChange={handleFileUpload} />

                {!fileUploaded && (
                  <div className="upload-wrapper">
         1          <button
                      className="upload-btn"
                      onClick={() => fileInputRef.current.click()}
                    >
                      Select PDF
                    </button>
                  </div>
                )}
             </div>
             {loading && !fileUploaded && <div className="loading-text">Processing document...</div>}
          </div>

          <div className="chat-panel">
            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.type}`}>
                  <div className="message-content">{msg.text}</div>
                </div>
              ))}
              {loading && <div className="loading-text">AI is thinking...</div>}
            </div>

            <div className="chat-input-container">
              <div className="chat-input-wrapper">
                <button className="icon-btn" onClick={handlePaperclipClick} title="Upload PDF">
                <FiPaperclip size={18} />                </button>
                <input 
                  type="text" 
                  placeholder={fileUploaded ? "Ask a question..." : "Upload a PDF first..."} 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  disabled={!fileUploaded || loading}
                />
                <button className="send-btn" onClick={handleSend} disabled={!fileUploaded || loading || !input.trim()}>
                  <FiSearch size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* =========================================
          UNIVERSAL MODAL (Popups)
          ========================================= */}
      {activeModal && (
        <div className="modal-overlay" onClick={() => setActiveModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {activeModal === 'settings' && 'Settings'}
                {activeModal === 'credentials' && 'My Credentials'}
                {activeModal === 'help' && 'Help Center'}
                {activeModal === 'privacy' && 'Privacy Policy'}
              </h3>
              <button className="icon-btn" onClick={() => setActiveModal(null)}><FiX size={20} /></button>
            </div>
            
            <div className="modal-body">
              {activeModal === 'settings' && (
                <div>
                  <p style={{ marginBottom: '15px', color: '#94a3b8' }}>Manage your application preferences here.</p>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'white', marginBottom: '10px' }}>
                    <input type="checkbox" defaultChecked /> Enable Notifications
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'white' }}>
                    <input type="checkbox" defaultChecked /> Dark Theme
                  </label>
                </div>
              )}

              {activeModal === 'credentials' && (
                <div>
                  <p style={{ color: '#94a3b8', marginBottom: '15px' }}>
                    You are currently on the <strong style={{ color: 'white' }}>Free Tier</strong>.
                  </p>
                  <p style={{ color: '#94a3b8' }}>
                    Enjoy basic access to AI document analysis.
                  </p>
                </div>
              )}

              {activeModal === 'help' && (
                <div>
                  <p style={{ color: '#94a3b8' }}>Need assistance? Check out our FAQs or contact support.</p>
                  <p style={{ marginTop: '10px', color: '#94a3b8' }}>Email: support@askyourpdf.com</p>
                </div>
              )}

              {activeModal === 'privacy' && (
                <div>
                  <p style={{ color: '#94a3b8' }}>Your documents are processed securely and are not stored permanently on our servers.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
