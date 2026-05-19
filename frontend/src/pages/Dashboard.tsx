import React from 'react'
import { PageContainer } from '../components/common/SharedComponents'
import { Link } from 'react-router-dom'
import { CanAccess } from '../lib/rbac/guards'

export default function Dashboard() {
  return (
    <PageContainer title="Panel de Control">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 12 }}>
        <Link to="/citas" style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16, textDecoration: 'none', color: 'inherit', display: 'block' }}>
          Citas de Hoy
        </Link>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>Tareas Pendientes</div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>Alertas</div>
      </div>

      <CanAccess module="users" action="view">
        <div style={{ marginTop: 24 }}>
          <h3>Acciones de Admin</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: 12, marginTop: 12 }}>
            <Link to="/admin/users" style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16, textDecoration: 'none', color: 'inherit' }}>
              <h4 style={{ margin: '0 0 8px 0' }}>Gestionar Usuarios</h4>
              <p style={{ margin: 0, color: '#6b7280', fontSize: 14 }}>Ver y editar usuarios</p>
            </Link>
            <Link to="/admin/users/register" style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 16, textDecoration: 'none', color: 'inherit' }}>
              <h4 style={{ margin: '0 0 8px 0' }}>Registrar Usuario</h4>
              <p style={{ margin: 0, color: '#6b7280', fontSize: 14 }}>Crear una nueva cuenta de usuario</p>
            </Link>
          </div>
        </div>
      </CanAccess>
    </PageContainer>
  )
}
