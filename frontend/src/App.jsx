import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Mic, Search, BookOpen, Heart, Leaf, Briefcase, Stethoscope, Baby, Menu, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './index.css';
import schemesData from '../../data/schemes.json';

function App() {
  const [activeTab, setActiveTab] = useState('HOME');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [schemes, setSchemes] = useState(schemesData);
  const [schemesLoaded, setSchemesLoaded] = useState(true);
  
  // Chat state
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Search/Filter state for schemes page
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedUiCategory, setSelectedUiCategory] = useState('');



  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (activeTab === 'HOME') {
      scrollToBottom();
    }
  }, [messages, activeTab]);

  const handleNavClick = (tab) => {
    setActiveTab(tab);
    setIsMenuOpen(false);
    window.scrollTo(0, 0);
  };

  const handleSearch = async (textQuery) => {
    const activeQuery = textQuery || query;
    if (!activeQuery.trim()) return;

    // Add user message
    const userMsg = { role: 'user', content: activeQuery };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setIsLoading(true);
    setActiveTab('HOME'); // Ensure we are on HOME tab

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        question: activeQuery
      });
      
      const assistantMsg = { 
        role: 'assistant', 
        content: response.data.answer,
        sources: response.data.sources
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (error) {
      console.error("API Error:", error);
      const backendError = error.response?.data?.error;
      const errorMsg = { 
        role: 'assistant', 
        content: backendError || "We are currently unable to process your request. Please try again later or check if the backend service is running." 
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMicClick = () => {
    alert("Voice input will be available soon.");
  };

  
  const getUiCategory = (scheme) => {
    const cat = (scheme.category || '').toLowerCase();
    const dept = (scheme.department || '').toLowerCase();
    
    if (cat.includes('education') || dept.includes('education')) return 'Education';
    if (cat.includes('agriculture') || dept.includes('agriculture') || dept.includes('animal') || dept.includes('fisher')) return 'Agriculture';
    if (cat.includes('health') || dept.includes('health') || cat.includes('maternity') || cat.includes('medical')) return 'Health';
    if (cat.includes('women') || cat.includes('child') || cat.includes('girl') || cat.includes('newborn') || cat.includes('marriage')) return 'Women & Child Welfare';
    if (cat.includes('employment') || cat.includes('labour') || cat.includes('skill') || cat.includes('entrepreneur') || cat.includes('worker') || dept.includes('labour') || dept.includes('worker')) return 'Employment';
    if (cat.includes('social welfare') || cat.includes('social security') || cat.includes('differently abled') || cat.includes('elderly') || cat.includes('minority') || cat.includes('pension') || dept.includes('social welfare')) return 'Social Welfare';
    
    return 'Other';
  };


  const handleCategoryClick = (uiCat) => {
    setSelectedUiCategory(uiCat);
    setSelectedDept('');
    setSearchTerm('');
    handleNavClick('SCHEMES');
  };

  const handleDeptClick = (dept) => {
    setSelectedDept(dept);
    setSelectedUiCategory('');
    setSearchTerm('');
    handleNavClick('SCHEMES');
  };

  // Derive departments
  const departments = [...new Set(schemes.map(s => s.department).filter(Boolean))];
  const deptCounts = departments.reduce((acc, dept) => {
    acc[dept] = schemes.filter(s => s.department === dept).length;
    return acc;
  }, {});

  // Render components based on tab
  const renderContent = () => {
    switch (activeTab) {
      case 'HOME':
        return (
          <>
            {messages.length === 0 && (
              <div className="hero">
                <h2>TAMIL NADU GOVERNMENT SCHEMES</h2>
                <h3>Citizen Scheme Assistant</h3>
                <p>Find information about Tamil Nadu Government schemes, eligibility, benefits and application procedures.</p>
              </div>
            )}

            <div className="chat-panel">
              <div className="chat-panel-header">
                Ask About Government Schemes
              </div>
              
              {messages.length > 0 && (
                <div className="chat-messages">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}>
                      <div className="sender">{msg.role === 'user' ? 'You' : 'Government Scheme Assistant'}</div>
                      <div className="content">
                        {msg.role === 'user' ? (
                          msg.content
                        ) : (
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {msg.content}
                          </ReactMarkdown>
                        )}
                      </div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="sources">
                          <strong>Sources:</strong> {msg.sources.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="message message-assistant">
                      <div className="sender">Government Scheme Assistant</div>
                      <div className="content">Fetching information...</div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}

              <div className="input-area">
                <input
                  type="text"
                  className="chat-input"
                  placeholder="Ask your question about a Tamil Nadu Government scheme..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  disabled={isLoading}
                />
                <button className="btn-search" onClick={() => handleSearch()} disabled={isLoading}>
                  SEARCH &rarr;
                </button>
                <button className="btn-mic" onClick={handleMicClick} title="Voice Input">
                  <Mic size={24} />
                </button>
              </div>
            </div>

            {messages.length === 0 && (
              <div className="quick-questions">
                <h3>Popular Scheme Questions</h3>
                <div className="questions-grid">
                  <button className="btn-quick" onClick={() => handleSearch("What is the objective of Naan Mudhalvan?")}>
                    What is the objective of Naan Mudhalvan?
                  </button>
                  <button className="btn-quick" onClick={() => handleSearch("Pudhumai Penn thittathula monthly evlo amount kidaikkum?")}>
                    Pudhumai Penn thittathula monthly evlo amount kidaikkum?
                  </button>
                  <button className="btn-quick" onClick={() => handleSearch("What are the benefits of Naan Mudhalvan?")}>
                    What are the benefits of Naan Mudhalvan?
                  </button>
                  <button className="btn-quick" onClick={() => handleSearch("Who is eligible for Tamil Pudhalvan?")}>
                    Who is eligible for Tamil Pudhalvan?
                  </button>
                </div>
              </div>
            )}

            {messages.length === 0 && (
              <div className="categories">
                <h3>Explore Government Schemes</h3>
                <div className="category-grid">
                  <div className="category-card" onClick={() => handleCategoryClick('Education')}>
                    <BookOpen className="category-icon" size={48} />
                    <span>Education</span>
                  </div>
                  <div className="category-card" onClick={() => handleCategoryClick('Social Welfare')}>
                    <Heart className="category-icon" size={48} />
                    <span>Social Welfare</span>
                  </div>
                  <div className="category-card" onClick={() => handleCategoryClick('Agriculture')}>
                    <Leaf className="category-icon" size={48} />
                    <span>Agriculture</span>
                  </div>
                  <div className="category-card" onClick={() => handleCategoryClick('Employment')}>
                    <Briefcase className="category-icon" size={48} />
                    <span>Employment</span>
                  </div>
                  <div className="category-card" onClick={() => handleCategoryClick('Health')}>
                    <Stethoscope className="category-icon" size={48} />
                    <span>Health</span>
                  </div>
                  <div className="category-card" onClick={() => handleCategoryClick('Women & Child Welfare')}>
                    <Baby className="category-icon" size={48} />
                    <span>Women & Child Welfare</span>
                  </div>
                </div>
              </div>
            )}
          </>
        );
      case 'SCHEMES':
const filteredSchemes = schemes.filter(s => {
          const searchLower = searchTerm.toLowerCase();
          const matchesSearch = !searchTerm || 
                                (s.scheme_name || '').toLowerCase().includes(searchLower) || 
                                (s.objective || '').toLowerCase().includes(searchLower) ||
                                (s.aliases || []).some(a => (a || '').toLowerCase().includes(searchLower));
          const matchesDept = selectedDept ? s.department === selectedDept : true;
          const matchesUiCat = selectedUiCategory ? getUiCategory(s) === selectedUiCategory : true;
          return matchesSearch && matchesDept && matchesUiCat;
        });

        return (
          <div>
            <h2 className="section-title">Government Schemes Directory</h2>
            <div className="search-box">
              <input 
                type="text" 
                placeholder="Search schemes..." 
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setSelectedUiCategory(''); setSelectedDept(''); }}
              />
              <select style={{padding: '0.8rem', marginLeft: '0.5rem', borderRadius: '4px', border: '1px solid #ccc'}} 
                      value={selectedDept} 
                      onChange={(e) => { setSelectedDept(e.target.value); setSelectedUiCategory(''); }}>
                <option value="">All Departments</option>
                {departments.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            
            <div className="grid-container">
{filteredSchemes.map((scheme, idx) => (
                <details className="card" key={idx} style={{cursor: 'pointer'}}>
                  <summary style={{listStyle: 'none', fontWeight: 'bold', fontSize: '1.2rem'}}>{scheme.scheme_name}</summary>
                  <div style={{marginTop: '1rem'}}>
                    {scheme.department && <div className="tag">{scheme.department}</div>}
                    {scheme.category && <div className="tag">{scheme.category}</div>}
                    {scheme.status && <div className="tag">{scheme.status}</div>}
                    <p style={{marginTop: '1rem'}}><strong>Objective:</strong> {scheme.objective || 'Not specified in cited source'}</p>
                    <p><strong>Target Beneficiaries:</strong> {scheme.target_beneficiaries || 'Not specified in cited source'}</p>
                    <p><strong>Eligibility:</strong> {scheme.eligibility || 'Not specified in cited source'}</p>
                    <p><strong>Benefits:</strong> {scheme.benefits || 'Not specified in cited source'}</p>
                    <p><strong>Application Process:</strong> {scheme.application_process || 'Not specified in cited source'}</p>
                    <p><strong>Application Mode:</strong> {scheme.application_mode || 'Not specified in cited source'}</p>
                    {scheme.official_application_url && <p><strong>Official URL:</strong> <a href={scheme.official_application_url} target="_blank">{scheme.official_application_url}</a></p>}
                    {scheme.official_source_url && <p><strong>Source URL:</strong> <a href={scheme.official_source_url} target="_blank">{scheme.official_source_url}</a></p>}
                  </div>
                </details>
              ))}
              {filteredSchemes.length === 0 && <p>No schemes found.</p>}
            </div>
          </div>
        );
      case 'DEPARTMENTS':
        return (
          <div>
            <h2 className="section-title">Government Departments</h2>
            <div className="grid-container">
              {Object.entries(deptCounts).map(([dept, count]) => (
                <div className="card" key={dept}>
                  <h4>{dept}</h4>
                  <p>{count} Scheme{count !== 1 ? 's' : ''} Available</p>
                  <button className="btn-search" style={{marginTop: '1rem', width: 'auto'}} onClick={() => handleDeptClick(dept)}>
                    View Schemes
                  </button>
                </div>
              ))}
            </div>
          </div>
        );
      case 'SERVICES':
        const serviceSchemes = schemes.filter(s => s.application_process || s.official_application_url || s.documents_required);
        return (
          <div>
            <h2 className="section-title">Application Services</h2>
            <div className="grid-container">
              {serviceSchemes.map((scheme, idx) => (
                <div className="card" key={idx}>
                  <h4>{scheme.scheme_name}</h4>
                  {scheme.application_mode && <div className="tag">Mode: {scheme.application_mode}</div>}
                  {scheme.application_process && <p style={{marginTop: '1rem'}}><strong>Process:</strong> {scheme.application_process}</p>}
                  {scheme.documents_required && (
                    <p><strong>Documents:</strong> {Array.isArray(scheme.documents_required) ? scheme.documents_required.join(', ') : scheme.documents_required}</p>
                  )}
                  {scheme.official_application_url && (
                    <a href={scheme.official_application_url} target="_blank" rel="noreferrer" className="btn-link">
                      Apply / Official Application
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      case 'ABOUT':
        return (
          <div>
            <h2 className="section-title">About the Project</h2>
            <div className="about-section">
              <h3>Tamil Nadu Government Schemes - AI Assistant</h3>
              <p style={{marginTop: '1rem'}}>An academic project designed to help users discover information about Tamil Nadu Government schemes, including benefits, eligibility, application procedures and related details.</p>
              
              <h4>Technology Stack:</h4>
              <ul>
                <li>FastAPI</li>
                <li>FAISS</li>
                <li>Sentence Transformers</li>
                <li>Llama 3.2 1B</li>
                <li>React</li>
              </ul>

              <div style={{marginTop: '2rem', padding: '1rem', backgroundColor: '#fff3cd', borderLeft: '4px solid #ffc107', color: '#856404'}}>
                <strong>IMPORTANT:</strong> This is an academic project and is not an official Government of Tamil Nadu website or service.
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="app-container">
      {/* HEADER */}
      <header className="header">
        <img src="/tn_logo.png" alt="Tamil Nadu Government Logo" className="header-logo" />
        <div className="header-text">
          <h1>TAMIL NADU GOVERNMENT</h1>
          <h2>Tamil Nadu Government Schemes - AI Assistant</h2>
        </div>
      </header>

      {/* NAVBAR */}
      <nav className="navbar" style={{backgroundColor: 'var(--primary-red)'}}>
        <button className="hamburger" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          {isMenuOpen ? <X size={32} /> : <Menu size={32} />}
        </button>
        <div className={`nav-menu ${isMenuOpen ? 'open' : ''}`}>
          <button className={`nav-link ${activeTab === 'HOME' ? 'active' : ''}`} onClick={() => handleNavClick('HOME')}>HOME</button>
          <button className={`nav-link ${activeTab === 'SCHEMES' ? 'active' : ''}`} onClick={() => handleNavClick('SCHEMES')}>SCHEMES</button>
          <button className={`nav-link ${activeTab === 'DEPARTMENTS' ? 'active' : ''}`} onClick={() => handleNavClick('DEPARTMENTS')}>DEPARTMENTS</button>
          <button className={`nav-link ${activeTab === 'SERVICES' ? 'active' : ''}`} onClick={() => handleNavClick('SERVICES')}>SERVICES</button>
          <button className={`nav-link ${activeTab === 'ABOUT' ? 'active' : ''}`} onClick={() => handleNavClick('ABOUT')}>ABOUT</button>
        </div>
      </nav>

      {/* ANNOUNCEMENT */}
      <div className="announcement">
        <span role="img" aria-label="announcement">📢</span>
        Explore Tamil Nadu Government Schemes and discover eligibility, benefits and application information.
      </div>

      <main className="main-content">
        {renderContent()}
      </main>

      {/* SILHOUETTE */}
      <div className="silhouette-container"></div>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-curve"></div>
        <div className="footer-content">
          <h3>Tamil Nadu Government Schemes</h3>
          <p>Government Scheme Information Assistant</p>
          
          <div className="footer-links">
            <a href="#" onClick={(e) => { e.preventDefault(); handleNavClick('ABOUT'); }}>About</a>
            <a href="#">Accessibility</a>
            <a href="#">Important Links</a>
            <a href="#">Contact</a>
          </div>
          
          <div className="disclaimer">
            This is an academic project developed as a Government Scheme Information Assistant. It is not an official Government of Tamil Nadu service.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
