import React from 'react'
import { PageContainer } from '../components/common/SharedComponents'

export default function MedicalRecords() {
  return (
    <PageContainer title="Historias Médicas">
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>
        <p style={{ margin: 0, color: '#6b7280' }}>Página de gestión de historias médicas</p>
      </div>
    </PageContainer>
  )
}
