import React from 'react'
import { PageContainer } from '../components/common/SharedComponents'

export default function Dashboard() {
  return (
    <PageContainer title="Dashboard">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 12 }}>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>Today Appointments</div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>Pending Tasks</div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>Alerts</div>
      </div>
    </PageContainer>
  )
}
