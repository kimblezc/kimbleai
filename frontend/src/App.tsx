import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'https://kimbleai-production.up.railway.app';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
}

interface Project {
  id: string;
  name: string;
  description: string;
  color: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState('');

  // Check for existing token
  useEffect(() => {
    const token = localStorage.getItem('kimbleai_token');
    if (token) {
      setIsLoggedIn(true);
      loadProjects();
    }
  }, []);

  const login = async () => {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, { email });
      localStorage.setItem('kimbleai_token', response.data.access_token);
      setIsLoggedIn(true);
      loadProjects();
    } catch (error) {
      alert('Login failed - please try again');
    }
  };

  const loadProjects = async () => {
    try {
      const token = localStorage.getItem('kimbleai_token');
      const response = await axios.get(`${API_URL}/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to load projects');
    }
  };

  const createProject = async () => {
    const name = prompt('Project name:');
    const description = prompt('Project description (optional):');
    if (!name) return;

    try {
      const token = localStorage.getItem('kimbleai_token');
      await axios.post(`${API_URL}/projects`, {
        name,
        description: description || '',
        color: '#3b82f6'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadProjects();
    } catch (error) {
      alert('Failed to create project');
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setInput('');

    try {
      const token = localStorage.getItem('kimbleai_token');
      const response = await axios.post(`${API_URL}/chat`, {
        message: input,
        project_id: selectedProject || null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        sources: response.data.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-form">
          <h1>🧠 KimbleAI</h1>
          <p>Permanent Family AI Memory System</p>
          <p>Cross-platform • Permanent retention • AI intelligence</p>
          <input
            type="email"
            placeholder="Enter your email (zach@kimbleai.com or family@kimbleai.com)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && login()}
          />
          <button onClick={login}>Sign In</button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-left">
          <h1>🧠 KimbleAI</h1>
          <span className="subtitle">Family AI Memory System</span>
        </div>
        <div className="header-controls">
          <select 
            value={selectedProject} 
            onChange={(e) => setSelectedProject(e.target.value)}
          >
            <option value="">All Projects</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
          <button onClick={createProject} className="create-btn">+ Project</button>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to KimbleAI! 🧠</h2>
              <p>Your permanent family AI memory system is ready.</p>
              <p>Upload documents, ask questions, and I'll remember everything!</p>
              <p>Features: Permanent memory • Cross-platform • AI intelligence</p>
            </div>
          )}
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">{message.content}</div>
              {message.sources && message.sources.length > 0 && (
                <div className="sources">
                  Sources: {message.sources.join(', ')}
                </div>
              )}
              <div className="timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          {loading && <div className="message assistant loading">🧠 Thinking...</div>}
        </div>

        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything about your family documents..."
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;