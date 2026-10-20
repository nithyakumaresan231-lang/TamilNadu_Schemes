import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  ExternalLink,
  RotateCcw,
  Sparkles,
  Info
} from 'lucide-react';
import './recommendations.css';

const INITIAL_PROFILE = {
  age: '',
  gender: '',
  category: '',
  annual_income: '',
  occupation: '',
  education_level: '',
  government_school: 'unknown',
  current_student_status: 'unknown',
  district: '',
  marital_status: '',
  disability_status: 'unknown',
  farmer_status: 'unknown',
};

export default function RecommendationsPage({ language = 'en' }) {
  const [profile, setProfile] = useState(INITIAL_PROFILE);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [activeTab, setActiveTab] = useState('ALL'); // ALL, LIKELY_MATCH, NEEDS_VERIFICATION, DOES_NOT_MATCH
  const [apiError, setApiError] = useState(null);

  const handleChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
    // Clear field-specific error on edit
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (profile.age !== '') {
      const ageNum = Number(profile.age);
      if (isNaN(ageNum) || ageNum < 0 || ageNum > 120) {
        newErrors.age = 'Please enter a valid age between 0 and 120.';
      }
    }
    if (profile.annual_income !== '') {
      const incNum = Number(profile.annual_income);
      if (isNaN(incNum) || incNum < 0) {
        newErrors.annual_income = 'Income cannot be negative.';
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;

    setLoading(true);
    try {
      // Build payload, converting empty strings to null or expected types
      const payload = {
        age: profile.age !== '' ? Number(profile.age) : null,
        gender: profile.gender || null,
        category: profile.category || null,
        annual_income: profile.annual_income !== '' ? Number(profile.annual_income) : null,
        occupation: profile.occupation || null,
        education_level: profile.education_level || null,
        government_school: profile.government_school,
        current_student_status: profile.current_student_status,
        district: profile.district || null,
        marital_status: profile.marital_status || null,
        disability_status: profile.disability_status,
        farmer_status: profile.farmer_status,
      };

      const res = await axios.post('http://localhost:8000/api/recommendations', payload);
      setResponse(res.data);
      // Auto-select tab to LIKELY_MATCH if any exist, otherwise ALL
      if (res.data.likely_matches_count > 0) {
        setActiveTab('LIKELY_MATCH');
      } else {
        setActiveTab('ALL');
      }
    } catch (err) {
      console.error('Recommendation API error:', err);
      const detail = err.response?.data?.detail || 'Unable to connect to the recommendation service. Please try again.';
      setApiError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setProfile(INITIAL_PROFILE);
    setErrors({});
    setResponse(null);
    setApiError(null);
    setActiveTab('ALL');
  };

  const filteredRecommendations = response?.recommendations.filter(rec => {
    if (activeTab === 'ALL') return true;
    return rec.status === activeTab;
  }) || [];

  return (
    <div className="recommendations-container">
      {/* Header */}
      <div className="recommendations-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary-red)', fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          <Sparkles size={18} />
          {language === 'ta' ? 'தனிப்பயனாக்கப்பட்ட திட்ட பரிந்துரைகள்' : 'Personalized Scheme Finder'}
        </div>
        <h1 className="recommendations-title">
          {language === 'ta' ? 'உங்களுக்கான அரசு திட்டங்களை கண்டறியவும்' : 'Find Government Schemes for Me'}
        </h1>
        <p className="recommendations-subtitle">
          {language === 'ta'
            ? 'உங்கள் சுயவிவரத்தை உள்ளிட்டு, தகுதியான தமிழ்நாடு அரசு திட்டங்களை சரிபார்த்து அறிந்து கொள்ளுங்கள்.'
            : 'Enter your basic profile details below. Our explainable eligibility engine checks each criteria transparently and explains why each scheme matches, needs verification, or does not match.'}
        </p>

        <div className="recommendation-disclaimer-box">
          <Info size={20} color="var(--primary-red)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Preliminary Guidance Only:</strong> Recommendations are derived from available government records and guidelines. Official sanction is determined by the respective government department upon verification of original certificates.
          </div>
        </div>
      </div>

      {/* User Profile Form */}
      <div className="profile-card">
        <form onSubmit={handleSubmit}>
          <div className="profile-form-grid">
            {/* Age */}
            <div className="form-group">
              <label>Age (Years)</label>
              <input
                type="number"
                placeholder="e.g. 21"
                min="0"
                max="120"
                className="form-input"
                value={profile.age}
                onChange={e => handleChange('age', e.target.value)}
              />
              {errors.age && <div className="form-error-msg">{errors.age}</div>}
            </div>

            {/* Gender */}
            <div className="form-group">
              <label>Gender</label>
              <select
                className="form-select"
                value={profile.gender}
                onChange={e => handleChange('gender', e.target.value)}
              >
                <option value="">Prefer not to say / Any</option>
                <option value="female">Female / Women / Girl</option>
                <option value="male">Male / Boy</option>
                <option value="transgender">Transgender</option>
              </select>
            </div>

            {/* Social Category */}
            <div className="form-group">
              <label>Social Category (Community)</label>
              <select
                className="form-select"
                value={profile.category}
                onChange={e => handleChange('category', e.target.value)}
              >
                <option value="">Prefer not to say / Any</option>
                <option value="SC">Scheduled Caste (SC / SCA)</option>
                <option value="ST">Scheduled Tribe (ST)</option>
                <option value="BC">Backward Class (BC)</option>
                <option value="MBC">Most Backward Class (MBC / DNC)</option>
                <option value="General">General / OC</option>
                <option value="Minority">Religious / Linguistic Minority</option>
              </select>
            </div>

            {/* Annual Income */}
            <div className="form-group">
              <label>Annual Family Income (₹)</label>
              <input
                type="number"
                placeholder="e.g. 150000"
                min="0"
                className="form-input"
                value={profile.annual_income}
                onChange={e => handleChange('annual_income', e.target.value)}
              />
              {errors.annual_income && <div className="form-error-msg">{errors.annual_income}</div>}
            </div>

            {/* Occupation */}
            <div className="form-group">
              <label>Occupation / Employment</label>
              <select
                className="form-select"
                value={profile.occupation}
                onChange={e => handleChange('occupation', e.target.value)}
              >
                <option value="">Any / Unspecified</option>
                <option value="student">Student / College Learner</option>
                <option value="farmer">Farmer / Agricultural Worker</option>
                <option value="unemployed">Educated Unemployed Youth</option>
                <option value="entrepreneur">Aspiring Entrepreneur / MSME</option>
                <option value="weaver">Handloom / Textile Weaver</option>
                <option value="construction">Construction Worker</option>
                <option value="driver">Driver / Transport Worker</option>
                <option value="employed">Employed / Salaried</option>
                <option value="other">Other / Self-employed</option>
              </select>
            </div>

            {/* Education Level */}
            <div className="form-group">
              <label>Education Level</label>
              <select
                className="form-select"
                value={profile.education_level}
                onChange={e => handleChange('education_level', e.target.value)}
              >
                <option value="">Any / Unspecified</option>
                <option value="below_10th">Below 10th Standard</option>
                <option value="10th_pass">10th Pass (SSLC)</option>
                <option value="12th_pass">12th Pass (HSC)</option>
                <option value="diploma">Diploma / Polytechnic</option>
                <option value="undergraduate">Undergraduate Degree (BA, BSc, BCom, etc.)</option>
                <option value="professional">Professional Degree (BE, MBBS, Agri, Law)</option>
                <option value="postgraduate">Postgraduate / Research</option>
              </select>
            </div>

            {/* Studied in Government School */}
            <div className="form-group">
              <label>Studied in a Government School?</label>
              <select
                className="form-select"
                value={profile.government_school}
                onChange={e => handleChange('government_school', e.target.value)}
              >
                <option value="unknown">Not sure / Unspecified</option>
                <option value="yes">Yes (Classes 6-12 in Govt School)</option>
                <option value="no">No (Private / Aided)</option>
              </select>
            </div>

            {/* Current Student Status */}
            <div className="form-group">
              <label>Currently Enrolled Student?</label>
              <select
                className="form-select"
                value={profile.current_student_status}
                onChange={e => handleChange('current_student_status', e.target.value)}
              >
                <option value="unknown">Not sure / Unspecified</option>
                <option value="yes">Yes, currently pursuing education</option>
                <option value="no">No, completed or discontinued</option>
              </select>
            </div>

            {/* Marital Status */}
            <div className="form-group">
              <label>Marital Status</label>
              <select
                className="form-select"
                value={profile.marital_status}
                onChange={e => handleChange('marital_status', e.target.value)}
              >
                <option value="">Any / Unspecified</option>
                <option value="unmarried">Unmarried / Single</option>
                <option value="married">Married</option>
                <option value="widow">Widow / Deserted</option>
                <option value="divorced">Divorced / Abandoned / Destitute</option>
              </select>
            </div>

            {/* Disability Status */}
            <div className="form-group">
              <label>Differently Abled (Disability)?</label>
              <select
                className="form-select"
                value={profile.disability_status}
                onChange={e => handleChange('disability_status', e.target.value)}
              >
                <option value="unknown">Not sure / Unspecified</option>
                <option value="yes">Yes (Person with Disability)</option>
                <option value="no">No</option>
              </select>
            </div>

            {/* Farmer Status */}
            <div className="form-group">
              <label>Land Ownership / Farmer?</label>
              <select
                className="form-select"
                value={profile.farmer_status}
                onChange={e => handleChange('farmer_status', e.target.value)}
              >
                <option value="unknown">Not sure / Unspecified</option>
                <option value="yes">Yes (Land-holding farmer / Agri worker)</option>
                <option value="no">No</option>
              </select>
            </div>

            {/* District */}
            <div className="form-group">
              <label>District / Residence</label>
              <input
                type="text"
                placeholder="e.g. Madurai, Chennai"
                className="form-input"
                value={profile.district}
                onChange={e => handleChange('district', e.target.value)}
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="profile-actions">
            <button
              type="button"
              className="btn-outline"
              onClick={handleReset}
              disabled={loading}
            >
              <RotateCcw size={16} />
              Reset
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Evaluating Eligibility...' : 'Find Matching Schemes'}
              <ArrowRight size={18} />
            </button>
          </div>
        </form>
      </div>

      {/* API Error Notification */}
      {apiError && (
        <div style={{ backgroundColor: '#FFEBEE', color: '#C62828', padding: '1rem', borderRadius: '6px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertCircle size={20} />
          <div>{apiError}</div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-skeleton">
          <div className="spinner"></div>
          <h3>Analyzing your profile against 150 Tamil Nadu Government schemes...</h3>
          <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>Evaluating explicit age, income, category, and eligibility criteria.</p>
        </div>
      )}

      {/* Results Section */}
      {!loading && response && (
        <div>
          <div className="results-header">
            <div>
              <h2 style={{ fontSize: '1.6rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                Evaluation Results
              </h2>
              <div className="results-counts">
                <span className="count-pill all">
                  Total: {response.total_schemes_evaluated}
                </span>
                <span className="count-pill likely">
                  <CheckCircle2 size={15} /> Likely Matches: {response.likely_matches_count}
                </span>
                <span className="count-pill verification">
                  <AlertCircle size={15} /> Needs Verification: {response.needs_verification_count}
                </span>
                <span className="count-pill nomatch">
                  <XCircle size={15} /> Does Not Match: {response.does_not_match_count}
                </span>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="filter-tabs">
              <button
                className={`tab-btn ${activeTab === 'ALL' ? 'active' : ''}`}
                onClick={() => setActiveTab('ALL')}
              >
                All ({response.total_schemes_evaluated})
              </button>
              <button
                className={`tab-btn ${activeTab === 'LIKELY_MATCH' ? 'active' : ''}`}
                onClick={() => setActiveTab('LIKELY_MATCH')}
              >
                Likely Matches ({response.likely_matches_count})
              </button>
              <button
                className={`tab-btn ${activeTab === 'NEEDS_VERIFICATION' ? 'active' : ''}`}
                onClick={() => setActiveTab('NEEDS_VERIFICATION')}
              >
                Needs Verification ({response.needs_verification_count})
              </button>
              <button
                className={`tab-btn ${activeTab === 'DOES_NOT_MATCH' ? 'active' : ''}`}
                onClick={() => setActiveTab('DOES_NOT_MATCH')}
              >
                Does Not Match ({response.does_not_match_count})
              </button>
            </div>
          </div>

          {/* Cards List */}
          {filteredRecommendations.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
              <HelpCircle size={40} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <h3>No schemes in this category</h3>
              <p>Try switching to another tab or updating your profile information.</p>
            </div>
          ) : (
            <div className="recommendations-list">
              {filteredRecommendations.map((rec) => {
                const statusClass = rec.status === 'LIKELY_MATCH'
                  ? 'likely'
                  : rec.status === 'NEEDS_VERIFICATION'
                  ? 'verification'
                  : 'nomatch';

                const statusLabel = rec.status === 'LIKELY_MATCH'
                  ? 'Likely Match'
                  : rec.status === 'NEEDS_VERIFICATION'
                  ? 'Needs Verification'
                  : 'Does Not Match';

                return (
                  <div key={rec.scheme_id} className={`rec-card ${statusClass}`}>
                    <div className="rec-card-header">
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary-red)', background: 'var(--bg-cream)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                            {rec.scheme_id}
                          </span>
                          <h3 className="rec-scheme-title">{rec.scheme_name}</h3>
                        </div>
                        <div className="rec-scheme-dept">
                          {rec.department || 'Department not specified'} • {rec.category || 'General'}
                        </div>
                      </div>

                      <div className={`status-badge ${statusClass}`}>
                        {rec.status === 'LIKELY_MATCH' && <CheckCircle2 size={16} />}
                        {rec.status === 'NEEDS_VERIFICATION' && <AlertCircle size={16} />}
                        {rec.status === 'DOES_NOT_MATCH' && <XCircle size={16} />}
                        {statusLabel}
                      </div>
                    </div>

                    {/* Explanations Block */}
                    <div className="conditions-block">
                      {/* Matched conditions */}
                      {rec.matched_conditions && rec.matched_conditions.length > 0 && (
                        <div>
                          {rec.matched_conditions.map((m, idx) => (
                            <div key={`m-${idx}`} className="condition-item matched">
                              <CheckCircle2 size={16} className="condition-icon" />
                              <span>{m}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Unknown / Needs verification conditions */}
                      {rec.unknown_conditions && rec.unknown_conditions.length > 0 && (
                        <div>
                          {rec.unknown_conditions.map((u, idx) => (
                            <div key={`u-${idx}`} className="condition-item unknown">
                              <AlertCircle size={16} className="condition-icon" />
                              <span>{u}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Failed conditions */}
                      {rec.failed_conditions && rec.failed_conditions.length > 0 && (
                        <div>
                          {rec.failed_conditions.map((f, idx) => (
                            <div key={`f-${idx}`} className="condition-item failed">
                              <XCircle size={16} className="condition-icon" />
                              <span>{f}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Original eligibility snippet */}
                    {rec.eligibility && (
                      <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        <strong>Record Criteria:</strong> {rec.eligibility}
                      </div>
                    )}

                    {/* Footer */}
                    <div className="rec-card-footer">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className="verification-tag">
                          Dataset Status: {rec.verification_level || 'PARTIAL'}
                        </span>
                      </div>

                      <div className="rec-links">
                        <Link to={`/schemes/${rec.scheme_id}`} className="link-action" style={{ fontSize: '0.9rem' }}>
                          View Scheme Details <ArrowRight size={14} />
                        </Link>
                        {rec.official_source_url && (
                          <a
                            href={rec.official_source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="link-action"
                            style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}
                          >
                            Official Source <ExternalLink size={14} />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
