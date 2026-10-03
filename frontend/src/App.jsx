import React, { useState, useRef, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Search, Mic, Menu, X, ArrowRight, BookOpen, Users, Leaf, Briefcase, Heart, GraduationCap, Building2, HelpCircle, ChevronDown, ChevronUp, MapPin, Volume2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './index.css';
import schemesData from '../../data/schemes.json';
import tnLogo from '../../images/tn_logo.png';
import breakfastImg from '../../images/Breakfast_scheme.jpg';
import manninImg from '../../images/mannin_magal_thittam.jpg';
import naanImg from '../../images/naan_mudhalvan.jpg';
import needsImg from '../../images/NEEDS_scheme.png';
import pudhumaiImg from '../../images/Pudhumai_pen.png';
import tamilImg from '../../images/tamil_pudhalvan.jpg';
import farmerImg from '../../images/farmer_scheme.jpg';
import handloomImg from '../../images/Handloom_scheme.jpg';

// Helper for image mapping based on requirements
const getImageForScheme = (schemeName) => {
  if (!schemeName) return null;
  const name = schemeName.toLowerCase();
  if (name.includes("breakfast")) return breakfastImg;
  if (name.includes("mannin magal")) return manninImg;
  if (name.includes("naan mudhalvan")) return naanImg;
  if (name.includes("needs")) return needsImg;
  if (name.includes("pudhumai penn")) return pudhumaiImg;
  if (name.includes("tamil pudhalvan")) return tamilImg;
  if (name.includes("annal ambedkar agricultural")) return farmerImg;
  if (name.includes("handloom old age pension")) return handloomImg;
  return null; // Fallback
};

// Data Normalization
const allDepartmentsMap = new Map();
const allCategoriesMap = new Map();

schemesData.forEach(s => {
  const dept = s.department?.trim();
  if (dept) {
    const key = dept.toLowerCase().replace(/\s+/g, ' ');
    if (!allDepartmentsMap.has(key)) allDepartmentsMap.set(key, dept);
  }
  
  const cat = s.category?.trim();
  if (cat) {
    const key = cat.toLowerCase().replace(/\s+/g, ' ');
    if (!allCategoriesMap.has(key)) allCategoriesMap.set(key, cat);
  }
});

const sortedDepartments = Array.from(allDepartmentsMap.values()).sort();
const sortedCategories = Array.from(allCategoriesMap.values()).sort();

// ----------------------------------------------------
// COMPONENTS
// ----------------------------------------------------

const Header = ({ language, setLanguage }) => {
  const location = useLocation();
  const isActive = (path) => location.pathname === path ? 'active' : '';
  
  return (
    <header className="header-top">
      <Link to="/" style={{textDecoration: 'none', color: 'inherit'}}>
        <div className="header-brand">
          <img src={tnLogo} alt="Tamil Nadu Government" className="header-logo" />
          <div className="header-title">
            Tamil Nadu Government<br/>Schemes
          </div>
        </div>
      </Link>
      <nav className="header-nav">
        <Link to="/" className={`nav-link ${isActive('/')}`}>Home</Link>
        <Link to="/schemes" className={`nav-link ${isActive('/schemes')}`}>Schemes</Link>
        <Link to="/departments" className={`nav-link ${isActive('/departments')}`}>Departments</Link>
        <Link to="/services" className={`nav-link ${isActive('/services')}`}>Services</Link>
        <Link to="/about" className={`nav-link ${isActive('/about')}`}>About</Link>
        <div className="lang-toggle">
          <button className={`lang-btn ${language === 'en' ? 'active' : ''}`} onClick={() => setLanguage('en')}>English</button>
          <span className="lang-sep">|</span>
          <button className={`lang-btn ${language === 'ta' ? 'active' : ''}`} onClick={() => setLanguage('ta')}>தமிழ்</button>
        </div>
      </nav>
    </header>
  );
};

const Footer = () => (
  <footer className="footer">
    <div className="footer-top">
      <div className="footer-brand">
        <div className="footer-brand-logo">
          <img src={tnLogo} alt="Tamil Nadu Government" />
          <span>TAMIL NADU GOVERNMENT<br/>SCHEMES</span>
        </div>
        <p>Explore schemes, understand eligibility and find application information for services across Tamil Nadu.</p>
      </div>
      <div className="footer-links">
        <div className="footer-column">
          <h5>Explore</h5>
          <Link to="/schemes">All schemes</Link>
          <Link to="/">Citizen categories</Link>
          <Link to="/departments">Departments</Link>
          <Link to="/services">Services</Link>
        </div>
        <div className="footer-column">
          <h5>Get support</h5>
          <Link to="/services">Application guide</Link>
          <Link to="/about">Help centre</Link>
          <Link to="/">Frequently asked questions</Link>
          <Link to="/departments">Department contacts</Link>
        </div>
        <div className="footer-column">
          <h5>About this portal</h5>
          <Link to="/about">About</Link>
          <Link to="/">Accessibility</Link>
          <Link to="/">Privacy policy</Link>
          <Link to="/">Terms of use</Link>
        </div>
      </div>
    </div>
    <div className="footer-bottom">
      <div>For information and guidance. Confirm current scheme requirements and application instructions with the relevant department.</div>
      <div>English | தமிழ்</div>
    </div>
  </footer>
);

// ----------------------------------------------------
// PAGES
// ----------------------------------------------------

const HomePage = () => {
  const navigate = useNavigate();
  
  const [q, setQ] = useState('');
  const [cat, setCat] = useState('');
  const [dept, setDept] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    
    if (dept) params.set('dept', dept);
    navigate(`/schemes?${params.toString()}`);
  };

  const featuredSchemes = [
    schemesData.find(s => s.scheme_id === "TN004"), // Breakfast
    schemesData.find(s => s.scheme_id === "TN001"), // Pudhumai Penn
    schemesData.find(s => s.scheme_id === "TN002"), // Tamil Pudhalvan
    schemesData.find(s => s.scheme_id === "TN003"), // Naan Mudhalvan
    schemesData.find(s => s.scheme_id === "TN073"), // Mannin Magal
    schemesData.find(s => s.scheme_id === "TN008"), // NEEDS
    schemesData.find(s => s.scheme_id === "TN055"), // Farmer Scheme
    schemesData.find(s => s.scheme_id === "TN112")  // Handloom Pension
  ].filter(Boolean);

  const [faqOpen, setFaqOpen] = useState(0);

  return (
    <div>
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-tag">Information for every citizen</div>
          <h1 className="hero-title">Tamil Nadu Government Schemes</h1>
          <p className="hero-subtitle">Discover government schemes, benefits, eligibility and application information.</p>
          <div className="hero-buttons">
            <Link to="/schemes" className="btn-primary">Explore Schemes <ArrowRight size={18} /></Link>
            <Link to="/assistant" className="btn-outline">Ask Government Assistant</Link>
          </div>
        </div>
        <div className="hero-image-wrapper">
          <img src={breakfastImg} alt="Breakfast Scheme" className="hero-image" />
          <div className="hero-image-caption">
            <h4>Supporting everyday lives</h4>
            <p>Education, wellbeing and opportunity in Tamil Nadu.</p>
          </div>
        </div>
      </section>

      <section className="search-section">
        <div className="search-header">
          <h2>Find the right scheme for you</h2>
        </div>
        <div className="search-controls">
          <div style={{ alignSelf: 'flex-end', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Search by scheme name, benefit or keyword.
          </div>
          <form className="search-bar-row" onSubmit={handleSearch}>
            <div className="search-input-wrapper">
              <Search className="search-icon" size={20} />
              <input type="text" placeholder="Search government schemes" className="search-input" value={q} onChange={e => setQ(e.target.value)} />
            </div>
            
            <select className="search-select" value={dept} onChange={e => setDept(e.target.value)}>
              <option value="">All departments</option>
              {sortedDepartments.map((d, i) => <option key={i} value={d}>{d}</option>)}
            </select>
            <button type="submit" className="btn-primary">Search Schemes</button>
          </form>
          <div className="popular-topics">
            <span>Popular topics</span>
            <div className="topic-pill" onClick={() => navigate('/schemes?cat=Education')}>Education</div>
            <div className="topic-pill" onClick={() => navigate('/schemes?q=women')}>Women's welfare</div>
            <div className="topic-pill" onClick={() => navigate('/schemes?q=skill')}>Skills & employment</div>
            <div className="topic-pill" onClick={() => navigate('/schemes?q=entrepreneur')}>Entrepreneurship</div>
          </div>
        </div>
      </section>

      <section className="category-section">
        <div className="section-header">
          <div>
            <h2>Browse by citizen category</h2>
            <p>Start with the support that matters to you and your family.</p>
          </div>
          <Link to="/schemes" className="link-action">View all categories <ArrowRight size={16} /></Link>
        </div>
        <div className="category-grid">
          <div className="category-card" onClick={() => navigate('/schemes?q=student')}>
            <GraduationCap className="category-icon" size={32} />
            <h3>Students</h3>
            <p>Learning & education</p>
          </div>
          <div className="category-card" onClick={() => navigate('/schemes?q=women')}>
            <Users className="category-icon" size={32} />
            <h3>Women</h3>
            <p>Education & welfare</p>
          </div>
          <div className="category-card" onClick={() => navigate('/schemes?q=farmer')}>
            <Leaf className="category-icon" size={32} />
            <h3>Farmers</h3>
            <p>Agriculture & livelihoods</p>
          </div>
          <div className="category-card" onClick={() => navigate('/schemes?q=youth')}>
            <Briefcase className="category-icon" size={32} />
            <h3>Young people</h3>
            <p>Skills & employment</p>
          </div>
          <div className="category-card" onClick={() => navigate('/schemes?q=entrepreneur')}>
            <Building2 className="category-icon" size={32} />
            <h3>Entrepreneurs</h3>
            <p>Enterprise & industry</p>
          </div>
          <div className="category-card" onClick={() => navigate('/schemes?q=senior')}>
            <Heart className="category-icon" size={32} />
            <h3>Senior citizens</h3>
            <p>Care & social support</p>
          </div>
        </div>
      </section>

      <section className="featured-section">
        <div className="section-pretitle">Explore Programmes</div>
        <div className="section-header">
          <div>
            <h2>Featured government schemes</h2>
            <p>A starting point for education, wellbeing, skills and enterprise support.</p>
          </div>
          <Link to="/schemes" className="link-action">Browse all schemes <ArrowRight size={16} /></Link>
        </div>
        
        <div className="schemes-grid">
          {featuredSchemes.map((scheme, idx) => (
            <div key={idx} className="scheme-card" onClick={() => navigate(`/schemes/${scheme.scheme_id}`)}>
              <img src={getImageForScheme(scheme.scheme_name)} alt={scheme.scheme_name} className="scheme-card-image" />
              <div className="scheme-card-content">
                <span className="scheme-tag">{scheme.category?.split('/')[0] || 'Scheme'}</span>
                <h3>{scheme.scheme_name}</h3>
                <div className="scheme-target">For {scheme.target_beneficiaries?.split(' ')[1] || 'citizens'}</div>
                <div className="scheme-desc">{scheme.objective || scheme.benefits?.substring(0, 100) + '...'}</div>
                <div className="scheme-card-footer">
                  <div className="link-action" style={{fontSize: '0.85rem'}}>View scheme details <ArrowRight size={14} /></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="department-section">
        <div className="section-header">
          <div>
            <h2>Explore by department</h2>
            <p>Find schemes and information organised by the department responsible.</p>
          </div>
          <Link to="/departments" className="link-action">View all departments <ArrowRight size={16} /></Link>
        </div>
        <div className="department-grid">
          {sortedDepartments.slice(0, 6).map((dept, idx) => (
            <div key={idx} className="dept-card" onClick={() => navigate(`/schemes?dept=${encodeURIComponent(dept)}`)}>
              <Building2 className="dept-icon" size={24} />
              <div className="dept-info">
                <h4>{dept}</h4>
                <p>{schemesData.filter(s => s.department === dept).length} Schemes</p>
              </div>
              <ArrowRight className="dept-arrow" size={20} />
            </div>
          ))}
        </div>
      </section>

      <section className="application-steps-section">
        <div className="section-pretitle">Before you apply</div>
        <div className="section-header">
          <div>
            <h2>A clear path from discovery to application</h2>
            <p>Understand the process before you take the next step.</p>
          </div>
        </div>
        
        <div className="steps-container">
          <div className="step-line"></div>
          <div className="step">
            <div className="step-number">01</div>
            <h4>Find a scheme</h4>
            <p>Browse by category or department and read the scheme overview.</p>
          </div>
          <div className="step">
            <div className="step-number">02</div>
            <h4>Check eligibility</h4>
            <p>Review who can apply, the conditions and the documents required.</p>
          </div>
          <div className="step">
            <div className="step-number">03</div>
            <h4>Prepare your documents</h4>
            <p>Keep the documents listed for the scheme ready before applying.</p>
          </div>
          <div className="step">
            <div className="step-number">04</div>
            <h4>Follow the application route</h4>
            <p>Use the application link or contact the office named in the scheme details.</p>
          </div>
        </div>
        <Link to="/services" className="link-action">Read the application guide <ArrowRight size={16} /></Link>
      </section>

      <section className="services-section">
        <div className="section-header">
          <div>
            <h2>Useful services and resources</h2>
            <p>Practical information to help you move forward with confidence.</p>
          </div>
        </div>
        <div className="services-grid">
          <div className="service-card">
            <BookOpen className="icon" size={28} />
            <h4>Application information</h4>
            <p>Understand online and office-based application routes for each scheme.</p>
            <Link to="/services" className="link-action">View application guidance <ArrowRight size={16}/></Link>
          </div>
          <div className="service-card">
            <BookOpen className="icon" size={28} />
            <h4>Documents & certificates</h4>
            <p>Find out which supporting documents a scheme may ask you to provide.</p>
            <Link to="/services" className="link-action">Read document guidance <ArrowRight size={16}/></Link>
          </div>
          <div className="service-card">
            <Building2 className="icon" size={28} />
            <h4>Department assistance</h4>
            <p>Know where to seek clarification about a scheme or your application.</p>
            <Link to="/departments" className="link-action">Find department contacts <ArrowRight size={16}/></Link>
          </div>
        </div>
      </section>

      <section className="faq-section">
        <div className="faq-left">
          <div className="section-pretitle">Help & Guidance</div>
          <h2>Questions about schemes?</h2>
          <p>Start with these common questions about finding support and applying for it.</p>
          <Link to="/about" className="link-action">Visit the help centre <ArrowRight size={16} /></Link>
          
          <div className="info-box">
            <HelpCircle className="icon" size={24} />
            <p>Requirements can differ by scheme. Read the scheme details and check with the relevant department before applying.</p>
          </div>
        </div>
        <div className="faq-right">
          {[
            { q: "How do I check whether I am eligible?", a: "Open the scheme details and read the eligibility section. It explains who the scheme is intended for and any conditions to meet. If you are unsure, contact the department listed for the scheme." },
            { q: "What documents do I need to apply?", a: "Required documents vary per scheme. Common documents include Aadhaar, Income Certificate, and Community Certificate." },
            { q: "Can I apply for every scheme online?", a: "Not all schemes have an online application. Check the 'Application Mode' section of the specific scheme." },
            { q: "Where can I get help with an application?", a: "You can visit the e-Sevai centres or contact the respective department's helpline." }
          ].map((faq, idx) => (
            <div className="faq-item" key={idx}>
              <div className={`faq-question ${faqOpen === idx ? 'active' : ''}`} onClick={() => setFaqOpen(faqOpen === idx ? -1 : idx)}>
                {faq.q}
                {faqOpen === idx ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </div>
              {faqOpen === idx && (
                <div className="faq-answer">{faq.a}</div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

const SchemesPage = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const query = searchParams.get('q') || '';
  const deptFilter = searchParams.get('dept') || '';
  

  const handleUpdate = (k, v) => {
    const p = new URLSearchParams(searchParams);
    if (v) p.set(k, v); else p.delete(k);
    setSearchParams(p);
  };

  const handleClear = () => {
    setSearchParams(new URLSearchParams());
  };

  const filteredSchemes = useMemo(() => {
    return schemesData.filter(s => {
      if (query) {
        const q = query.toLowerCase();
        const text = `${s.scheme_name} ${s.aliases?.join(' ')} ${s.department} ${s.category} ${s.objective} ${s.target_beneficiaries}`.toLowerCase();
        if (!text.includes(q)) return false;
      }
      if (deptFilter) {
        if (!s.department || s.department.trim().toLowerCase().replace(/\s+/g, ' ') !== deptFilter.toLowerCase().replace(/\s+/g, ' ')) return false;
      }
      
      return true;
    });
  }, [query, deptFilter]);

  return (
    <div className="page-container">
      <h1 className="page-title">All Schemes</h1>
      <p className="page-subtitle">Showing {filteredSchemes.length} schemes</p>
      
      
      
      <div className="search-section" style={{padding: '1.5rem', marginBottom: '2rem', borderRadius: '8px', border: '1px solid var(--border-light)'}}>
        <div className="search-controls" style={{width: '100%', flex: 'none'}}>
          <div className="search-bar-row">
            <div className="search-input-wrapper">
              <Search className="search-icon" size={20} />
              <input type="text" placeholder="Search schemes..." className="search-input" value={query} onChange={e => handleUpdate('q', e.target.value)} />
            </div>
            
            <select className="search-select" value={deptFilter} onChange={e => handleUpdate('dept', e.target.value)}>
              <option value="">All Departments</option>
              {sortedDepartments.map((d, i) => <option key={i} value={d}>{d}</option>)}
            </select>
            <button onClick={handleClear} className="btn-outline">Clear Filters</button>
          </div>
        </div>
      </div>

      {filteredSchemes.length === 0 ? (
        <div style={{textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)'}}>
          <BookOpen size={48} style={{margin: '0 auto 1rem', opacity: 0.5}} />
          <h3>No schemes found</h3>
          <p style={{marginTop: '0.5rem'}}>Try adjusting your filters or search terms.</p>
          <button onClick={handleClear} className="btn-primary" style={{margin: '1rem auto 0'}}>Clear all filters</button>
        </div>
      ) : (
        <div className="schemes-grid">
          {filteredSchemes.map((scheme, idx) => (
            <div key={idx} className="scheme-card" onClick={() => navigate(`/schemes/${scheme.scheme_id}`)}>
              
              <div className="scheme-card-content" style={{borderTop: '4px solid var(--primary-red)'}}>
                <span className="scheme-tag">{scheme.category?.split('/')[0] || 'Scheme'}</span>
                <h3>{scheme.scheme_name}</h3>
                <div className="scheme-target">For {scheme.target_beneficiaries?.substring(0, 50) || 'citizens'}</div>
                <div className="scheme-desc">{scheme.objective || scheme.benefits?.substring(0, 100) + '...'}</div>
                <div className="scheme-card-footer">
                  <div className="link-action" style={{fontSize: '0.85rem'}}>View scheme details <ArrowRight size={14} /></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const SchemeDetailPage = () => {
  const { pathname } = useLocation();
  const schemeId = pathname.split('/').pop();
  const scheme = schemesData.find(s => s.scheme_id === schemeId);
  
  if (!scheme) {
    return (
      <div className="page-container" style={{textAlign: 'center', padding: '4rem 0'}}>
        <h2>Scheme not found</h2>
        <Link to="/schemes" className="btn-primary" style={{display: 'inline-flex', marginTop: '1rem'}}>Browse all schemes</Link>
      </div>
    );
  }

  return (
    <div className="page-container" style={{maxWidth: '900px'}}>
      <Link to="/schemes" className="link-action" style={{marginBottom: '2rem'}}>&larr; Back to Schemes</Link>
      
      <span className="scheme-tag" style={{display: 'inline-block', backgroundColor: 'var(--bg-cream)', color: 'var(--primary-red)', padding: '0.25rem 0.75rem', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, marginBottom: '1rem'}}>{scheme.category || 'Scheme'}</span>
      <h1 className="page-title" style={{marginTop: '0'}}>{scheme.scheme_name}</h1>
      <p className="page-subtitle" style={{fontWeight: 600, color: 'var(--primary-red)'}}>{scheme.department}</p>
      
      {getImageForScheme(scheme.scheme_name) && (
        <img src={getImageForScheme(scheme.scheme_name)} alt={scheme.scheme_name} style={{width: '100%', height: '350px', objectFit: 'cover', borderRadius: '8px', marginBottom: '2.5rem', border: '1px solid var(--border-light)'}} />
      )}
      
      <div style={{display: 'grid', gridTemplateColumns: '1fr', gap: '2rem', backgroundColor: 'white', padding: '2.5rem', borderRadius: '8px', border: '1px solid var(--border-light)'}}>
        
        {scheme.objective && (
          <div>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '0.5rem', fontSize: '1.1rem'}}>Objective</h3>
            <p style={{lineHeight: 1.6}}>{scheme.objective}</p>
          </div>
        )}

        {scheme.target_beneficiaries && (
          <div>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '0.5rem', fontSize: '1.1rem'}}>Target Beneficiaries</h3>
            <p style={{lineHeight: 1.6}}>{scheme.target_beneficiaries}</p>
          </div>
        )}

        {scheme.eligibility && (
          <div>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '0.5rem', fontSize: '1.1rem'}}>Eligibility Criteria</h3>
            <p style={{lineHeight: 1.6}}>{scheme.eligibility}</p>
          </div>
        )}

        {scheme.benefits && (
          <div>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '0.5rem', fontSize: '1.1rem'}}>Benefits</h3>
            <p style={{lineHeight: 1.6}}>{scheme.benefits}</p>
          </div>
        )}

        {scheme.benefit_amount && (
          <div>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '0.5rem', fontSize: '1.1rem'}}>Benefit Amount</h3>
            <p style={{lineHeight: 1.6}}>{scheme.benefit_amount}</p>
          </div>
        )}

        {scheme.documents_required && (
          <div>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '0.5rem', fontSize: '1.1rem'}}>Documents Required</h3>
            <p style={{lineHeight: 1.6}}>{Array.isArray(scheme.documents_required) ? scheme.documents_required.join(', ') : scheme.documents_required}</p>
          </div>
        )}

        {(scheme.application_process || scheme.application_mode) && (
          <div style={{backgroundColor: 'var(--bg-cream)', padding: '1.5rem', borderRadius: '8px', marginTop: '1rem'}}>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '1rem', fontSize: '1.1rem'}}>Application Information</h3>
            {scheme.application_mode && <p style={{marginBottom: '0.5rem'}}><strong>Mode:</strong> {scheme.application_mode}</p>}
            {scheme.application_process && <p style={{marginBottom: '1rem'}}><strong>Process:</strong> {scheme.application_process}</p>}
            
            <div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '1.5rem'}}>
              {scheme.official_application_url && (
                <a href={scheme.official_application_url} target="_blank" rel="noreferrer" className="btn-primary" style={{textDecoration: 'none'}}>
                  Official Application Link <ArrowRight size={16} />
                </a>
              )}
              {scheme.official_source_url && (
                <a href={scheme.official_source_url} target="_blank" rel="noreferrer" className="btn-outline" style={{textDecoration: 'none'}}>
                  Official Source Document
                </a>
              )}
            </div>
          </div>
        )}
        
        {scheme.important_conditions && (
          <div style={{marginTop: '1rem'}}>
            <h3 style={{color: 'var(--primary-red)', marginBottom: '0.5rem', fontSize: '1.1rem'}}>Important Conditions</h3>
            <p style={{lineHeight: 1.6, color: 'var(--text-muted)'}}>{scheme.important_conditions}</p>
          </div>
        )}

      </div>
    </div>
  );
};

const DepartmentsPage = () => {
  const navigate = useNavigate();
  return (
    <div className="page-container">
      <h1 className="page-title">Departments</h1>
      <p className="page-subtitle">Schemes organized by Government Departments ({sortedDepartments.length} departments)</p>
      
      <div className="department-grid">
        {sortedDepartments.map((dept, idx) => (
          <div key={idx} className="dept-card" onClick={() => navigate(`/schemes?dept=${encodeURIComponent(dept)}`)}>
            <Building2 className="dept-icon" size={24} />
            <div className="dept-info">
              <h4>{dept}</h4>
              <p>{schemesData.filter(s => s.department === dept).length} Schemes</p>
            </div>
            <ArrowRight className="dept-arrow" size={20} />
          </div>
        ))}
      </div>
    </div>
  );
};

const ServicesPage = () => (
  <div className="page-container">
    <h1 className="page-title">Useful Services</h1>
    <p className="page-subtitle">Resources to help you apply for schemes</p>
    <div className="services-grid">
      <div className="service-card">
        <BookOpen className="icon" size={28} />
        <h4>Application information</h4>
        <p>Understand online and office-based application routes for each scheme.</p>
      </div>
      <div className="service-card">
        <BookOpen className="icon" size={28} />
        <h4>Documents & certificates</h4>
        <p>Find out which supporting documents a scheme may ask you to provide.</p>
      </div>
    </div>
  </div>
);

const AboutPage = () => (
  <div className="page-container">
    <h1 className="page-title">About</h1>
    <p className="page-subtitle">Tamil Nadu Government Schemes - AI Assistant</p>
    <div style={{backgroundColor: '#fff3cd', padding: '1rem', borderLeft: '4px solid #ffc107', color: '#856404'}}>
      <strong>IMPORTANT:</strong> This is an academic project designed to help users discover information about Tamil Nadu Government schemes. It is not an official Government of Tamil Nadu website or service.
    </div>
  </div>
);

// ----------------------------------------------------
// ASSISTANT PAGE (Preserved RAG / STT / TTS Logic)
// ----------------------------------------------------

const AssistantPage = ({ language }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // STT / TTS state
  const [isListening, setIsListening] = useState(false);
  const [speakingMsgIdx, setSpeakingMsgIdx] = useState(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        question: userMsg.content,
        language: language
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
        content: backendError || "We are currently unable to process your request."
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMicClick = () => {
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    if (isListening) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsListening(false);
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = language === 'ta' ? 'ta-IN' : 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(prev => prev ? prev + ' ' + transcript : transcript);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    try { recognition.start(); } catch (e) { setIsListening(false); }
  };

  const getVoiceForLanguage = (langCode) => {
    const voices = window.speechSynthesis.getVoices();
    if (langCode === 'ta') {
      let voice = voices.find(v => v.lang === 'ta-IN');
      if (!voice) voice = voices.find(v => v.lang.startsWith('ta'));
      return voice;
    } else {
      let voice = voices.find(v => v.lang === 'en-IN');
      if (!voice) voice = voices.find(v => v.lang.startsWith('en'));
      return voice || voices[0];
    }
  };

  const handleSpeakerClick = (text, idx) => {
    if (speakingMsgIdx === idx) {
      window.speechSynthesis.cancel();
      setSpeakingMsgIdx(null);
      return;
    }
    window.speechSynthesis.cancel();
    
    // Markdown strip for TTS
    let cleanText = text;
    cleanText = cleanText.replace(/###?\s+Sources?:.*$/im, '');
    cleanText = cleanText.replace(/^\s*(#+)\s+/gm, '');
    cleanText = cleanText.replace(/^[-=*]{3,}\s*$/gm, '');
    cleanText = cleanText.replace(/^\s*[-*+]\s+/gm, '');
    cleanText = cleanText.replace(/[*_~`]{1,3}/g, '');
    cleanText = cleanText.replace(/\s+/g, ' ').trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = language === 'ta' ? 'ta-IN' : 'en-IN';

    const setVoiceAndSpeak = () => {
      const voice = getVoiceForLanguage(language);
      if (voice) {
        utterance.voice = voice;
        window.speechSynthesis.speak(utterance);
        setSpeakingMsgIdx(idx);
      } else {
        alert(language === 'ta' ? "No Tamil speech voice is available in this browser." : "No English speech voice is available in this browser.");
      }
    };

    if (window.speechSynthesis.getVoices().length > 0) {
      setVoiceAndSpeak();
    } else {
      window.speechSynthesis.onvoiceschanged = () => setVoiceAndSpeak();
    }

    utterance.onend = () => setSpeakingMsgIdx(null);
    utterance.onerror = () => setSpeakingMsgIdx(null);
  };

  return (
    <div className="chat-container-page">
      <div className="chat-panel">
        <div className="chat-header">
          <img src={tnLogo} alt="Logo" style={{height: '30px'}} />
          Government Scheme Assistant
        </div>
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div style={{textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem'}}>
              Start a conversation to get detailed answers powered by AI.
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}>
                {msg.role === 'assistant' && (
                  <button 
                    onClick={() => handleSpeakerClick(msg.content, idx)}
                    style={{float: 'right', background: 'none', border: 'none', cursor: 'pointer', color: speakingMsgIdx === idx ? 'var(--primary-red)' : 'var(--text-muted)'}}
                    title="Listen to response"
                  >
                    <Volume2 size={20} />
                  </button>
                )}
                {msg.role === 'user' ? msg.content : (
                  <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources">
                        <strong>Sources: </strong>
                        {msg.sources.join(', ')}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="message message-assistant" style={{fontStyle: 'italic', opacity: 0.7}}>
              Typing...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form className="input-area" onSubmit={handleSearch}>
          <input
            type="text"
            className="chat-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={language === 'ta' ? "உதவிக்கு கேளுங்கள்..." : "Ask a question about government schemes..."}
            disabled={isLoading}
          />
          <button type="button" className="btn-mic" onClick={handleMicClick} style={{color: isListening ? 'var(--primary-red)' : 'var(--text-muted)'}}>
            <Mic size={24} />
          </button>
          <button type="submit" className="btn-send" disabled={isLoading || !query.trim()}>
            Send <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

// ----------------------------------------------------
// MAIN APP COMPONENT
// ----------------------------------------------------

export default function App() {
  const [language, setLanguage] = useState('en');

  // Load voices proactively for TTS (matches existing logic)
  useEffect(() => {
    window.speechSynthesis.getVoices();
  }, []);

  return (
    <Router>
      <div className="app-container">
        <Header language={language} setLanguage={setLanguage} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/schemes" element={<SchemesPage />} />
            <Route path="/schemes/:schemeId" element={<SchemeDetailPage />} />
            <Route path="/departments" element={<DepartmentsPage />} />
            <Route path="/services" element={<ServicesPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/assistant" element={<AssistantPage language={language} />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}
