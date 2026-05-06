import React from 'react';
import { useNavigate } from 'react-router-dom';

export const PageHeader = ({ title, icon = '', onBack = true }) => {
  const navigate = useNavigate();

  return (
    <header style={{backgroundColor: '#fff', borderBottom: '1px solid #eee', padding: '16px 0'}}>
      <div style={{maxWidth: '1200px', margin: '0 auto', padding: '0 20px', display: 'flex', alignItems: 'center', gap: '16px'}}>
        {onBack && (
          <button
            onClick={() => navigate(-1)}
            style={{
              background: 'none',
              border: 'none',
              color: '#00a8e8',
              fontSize: '1.2rem',
              cursor: 'pointer',
              padding: '4px 8px',
              fontWeight: 600
            }}
          >
            ← Back
          </button>
        )}
        <h1 style={{fontSize: '1.5rem', fontWeight: 700, color: '#0f3460', margin: 0}}>
          {icon && <span style={{marginRight: '8px'}}>{icon}</span>}
          {title}
        </h1>
      </div>
    </header>
  );
};
