import React, { useState } from 'react';

const DefectedItemsView = ({ onInitiateVerification }) => {
    const [claims, setClaims] = useState([
        {
            id: "RET-7721",
            userId: "USR-992",
            productName: "Premium Leather Jacket",
            defectedImageUrl: "/assets/defected_jacket.png",
            description: "Zipper is broken and there is a tear on the left sleeve.",
            status: "PENDING",
            createdAt: new Date().toISOString()
        }
    ]);

    const handleStatusUpdate = (id, newStatus) => {
        setClaims(claims.map(c => c.id === id ? { ...c, status: newStatus } : c));
    };

    return (
        <div className="view-container animate-fade-in">
            <header className="view-header">
                <h2>Defected Items Management</h2>
                <p>Review and process return requests with visual evidence.</p>
            </header>

            <div className="claims-grid">
                {claims.map(claim => (
                    <div key={claim.id} className="glass-card claim-item">
                        <div className="claim-image-wrapper">
                            <img src={claim.defectedImageUrl} alt="Defect Evidence" className="claim-image" />
                            <div className={`status-tag ${claim.status.toLowerCase()}`}>
                                {claim.status}
                            </div>
                        </div>
                        
                        <div className="claim-details">
                            <div className="detail-row">
                                <span className="label">Claim ID:</span>
                                <span className="value">{claim.id}</span>
                            </div>
                            <div className="detail-row">
                                <span className="label">Product:</span>
                                <span className="value">{claim.productName}</span>
                            </div>
                            
                            <div className="description-box">
                                <h5>Admin Note:</h5>
                                <p>{claim.description}</p>
                            </div>

                            <div className="claim-actions" style={{flexDirection: 'column'}}>
                                <button className="btn-approve" onClick={() => onInitiateVerification(claim)}>
                                    🛡️ Process Identity Check
                                </button>
                                <div style={{display: 'flex', gap: '0.5rem', width: '100%'}}>
                                    <button className="btn-secondary" onClick={() => handleStatusUpdate(claim.id, 'APPROVED')} style={{fontSize: '0.8rem'}}>
                                        Quick Approve
                                    </button>
                                    <button className="btn-reject" onClick={() => handleStatusUpdate(claim.id, 'REJECTED')} style={{fontSize: '0.8rem'}}>
                                        Reject
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DefectedItemsView;
