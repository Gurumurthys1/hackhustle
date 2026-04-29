import React, { useState, useEffect } from 'react';

const ReviewDashboard = ({ initialClaim, onReset }) => {
    const [step, setStep] = useState(0); 
    const [isWizardActive, setIsWizardActive] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    
    const [formData, setFormData] = useState({
        claimId: "",
        userId: "",
        defectedImage: "",
        registeredImage: "/assets/registered_user.png",
        googleLensResultImage: "/assets/catalog_jacket.png",
        socialMediaPostImage: "/assets/social_post.png",
        dressVerificationResult: null,
        faceVerificationResult: null,
        videoCallRevealed: false
    });

    useEffect(() => {
        if (initialClaim) {
            setFormData({
                ...formData,
                claimId: initialClaim.id,
                userId: initialClaim.userId,
                defectedImage: initialClaim.defectedImageUrl
            });
            setIsWizardActive(true);
            setStep(1);
        }
    }, [initialClaim]);

    const startLensScan = () => {
        setIsScanning(true);
        setTimeout(() => {
            setIsScanning(false);
        }, 3000);
    };

    // Step 1: Returned Product vs Google Lens Result
    const renderStep1 = () => (
        <div className="wizard-step animate-fade-in">
            <div className="step-heading">
                <h3>Step 1: Visual Intelligence Scan</h3>
                <p>Analyzing returned product against global marketplace data (Google Lens Integration).</p>
            </div>
            
            <div className="split-view">
                <div className="view-panel left">
                    <span className="panel-label">User Uploaded Return Item</span>
                    <div className="image-container">
                        <img src={formData.defectedImage} alt="Return Item" />
                        {isScanning && <div className="scan-bar"></div>}
                    </div>
                </div>

                <div className="view-panel right">
                    <span className="panel-label">Google Lens: Related Marketplace Image</span>
                    <div className={`image-container ${isScanning ? 'blur' : ''}`}>
                        {isScanning ? (
                            <div className="loading-content">
                                <div className="spinner"></div>
                                <span>Scanning Global Databases...</span>
                            </div>
                        ) : (
                            <img src={formData.googleLensResultImage} alt="Lens Result" />
                        )}
                    </div>
                </div>
            </div>

            {!isScanning && (
                <div className="action-footer">
                    {!formData.googleLensResultImage || isScanning ? null : (
                        <div className="decision-prompt">
                            <p>Does the returned product match the identified listing?</p>
                            <div className="btn-group">
                                <button className="btn-approve" onClick={() => { setFormData({...formData, dressVerificationResult: 'PASS'}); setStep(2); }}>
                                    ✅ Product Matches
                                </button>
                                <button className="btn-reject" onClick={() => { setFormData({...formData, dressVerificationResult: 'FRAUD'}); setStep(2); }}>
                                    🚩 Flag as Fraud (Suspected Mismatch)
                                </button>
                            </div>
                        </div>
                    )}
                    <button className="btn-secondary" onClick={startLensScan} style={{marginTop: '1rem'}}>
                        {isScanning ? 'Scanning...' : 'Re-run Visual Scan'}
                    </button>
                </div>
            )}
        </div>
    );

    // Step 2: Registered Profile vs Social Media Post Image
    const renderStep2 = () => (
        <div className="wizard-step animate-fade-in">
             <div className="step-heading">
                <h3>Step 2: Social Media Cross-Verification</h3>
                <p>Comparing internal profile photo with recent social media activity (Post Discovery).</p>
            </div>

            <div className="split-view">
                <div className="view-panel left">
                    <span className="panel-label">Platform Registered Identity</span>
                    <div className="image-container">
                        <img src={formData.registeredImage} alt="Platform ID" />
                    </div>
                </div>

                <div className="view-panel right">
                    <span className="panel-label">Instagram Post: Found via Visual Match</span>
                    <div className="image-container">
                        <img src={formData.socialMediaPostImage} alt="Social Media" />
                    </div>
                </div>
            </div>

            <div className="action-footer">
                <div className="decision-prompt">
                    <p>Is the person in the social media post the same as the registered user?</p>
                    <div className="btn-group">
                        <button className="btn-approve" onClick={() => { setFormData({...formData, faceVerificationResult: 'PASS'}); setStep(5); }}>
                            ✅ Identity Matches
                        </button>
                        <button className="btn-reject" onClick={() => { setFormData({...formData, faceVerificationResult: 'FRAUD'}); setStep(3); }}>
                            🚩 Flag as Identity Fraud
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    // Step 3: Video Call Initiation
    const renderStep3 = () => (
        <div className="wizard-step animate-fade-in">
            <div className="step-heading">
                <h3>Step 3: Escalated Video Verification</h3>
                <p>Final human-in-the-loop verification to reveal potential fraud.</p>
            </div>

            <div className="glass-card video-card">
                <div className="video-placeholder">
                    <div className="user-initials">UC</div>
                    <div className="call-overlay">
                        <span>CONNECTING TO USER FOR LIVE IDENTITY REVEAL...</span>
                    </div>
                </div>
                <div className="call-controls">
                    <button className="btn-reject-heavy" onClick={() => { setFormData({...formData, videoCallRevealed: true}); setStep(4); }}>
                        🔴 Reveal Fraud & Block Account
                    </button>
                    <button className="btn-approve" onClick={() => { setFormData({...formData, videoCallRevealed: false}); setStep(5); }}>
                        ✅ Clear Suspicions
                    </button>
                </div>
            </div>
        </div>
    );

    const renderFraudRevealed = () => (
        <div className="wizard-step animate-fade-in">
            <div className="result-banner fraud">
                <h2>⚠️ FRAUD REVEALED</h2>
                <p>Visual and Identity verification layers confirmed a malicious refund attempt.</p>
            </div>

            <div className="glass-card result-summary">
                <div className="summary-section">
                    <h4>Evidence Log</h4>
                    <div className="log-item fail">
                        <span>Dress Verification</span>
                        <span>FRAUD DETECTED (Mismatched item detected via Google Lens)</span>
                    </div>
                    <div className="log-item fail">
                        <span>Face Verification</span>
                        <span>FRAUD DETECTED (Identity mismatch on Instagram Post)</span>
                    </div>
                    <div className="log-item fail">
                        <span>Video Call</span>
                        <span>FRAUD REVEALED (User failed live verification)</span>
                    </div>
                </div>

                <div className="action-footer">
                    <button className="btn-reject" onClick={() => { setIsWizardActive(false); onReset(); setStep(0); }}>
                        Close Case & Flag User
                    </button>
                </div>
            </div>
        </div>
    );

    const renderSuccess = () => (
        <div className="wizard-step animate-fade-in">
            <div className="result-banner success">
                <h2>✅ VERIFICATION SUCCESSFUL</h2>
                <p>All security layers cleared. Identity and product match confirmed.</p>
            </div>

            <div className="glass-card result-summary">
                <div className="summary-section">
                    <h4>Verification Log</h4>
                    <div className="log-item pass">
                        <span>Dress Verification</span>
                        <span>MATCHED</span>
                    </div>
                    <div className="log-item pass">
                        <span>Face Verification</span>
                        <span>MATCHED</span>
                    </div>
                </div>

                <div className="action-footer">
                    <button className="btn-approve" onClick={() => { setIsWizardActive(false); onReset(); setStep(0); }}>
                        Approve Refund
                    </button>
                </div>
            </div>
        </div>
    );

    return (
        <div className="view-container animate-fade-in">
            <header className="view-header">
                <h2>Fraud Investigation Command</h2>
                <p>Advanced multi-layered verification pipeline.</p>
            </header>

            {!isWizardActive ? (
                <div className="empty-state glass-card">
                    <div className="empty-icon">🕵️‍♂️</div>
                    <h3>Investigation Console Idle</h3>
                    <p>Start a new investigation from the 'Defected Items' dashboard to begin the verification process.</p>
                </div>
            ) : (
                <div className="wizard-container large">
                    <div className="stepper compact">
                        <div className={`step-dot ${step >= 1 ? 'active' : ''}`}>1</div>
                        <div className="step-line"></div>
                        <div className={`step-dot ${step >= 2 ? 'active' : ''}`}>2</div>
                        <div className="step-line"></div>
                        <div className={`step-dot ${step >= 3 ? 'active' : ''}`}>3</div>
                    </div>

                    {step === 1 && renderStep1()}
                    {step === 2 && renderStep2()}
                    {step === 3 && renderStep3()}
                    {step === 4 && renderFraudRevealed()}
                    {step === 5 && renderSuccess()}
                </div>
            )}
        </div>
    );
};

export default ReviewDashboard;
