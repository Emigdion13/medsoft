import React from 'react'

export function PageContainer({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ padding: 20 }}>
      <h1 style={{ marginTop: 0 }}>{title}</h1>
      {children}
    </section>
  )
}
