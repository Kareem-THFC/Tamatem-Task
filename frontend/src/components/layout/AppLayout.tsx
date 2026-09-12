import { Outlet, useLocation } from 'react-router-dom'

import { Header } from '@/components/layout/Header'

export function AppLayout() {
  const location = useLocation()

  return (
    <div className="flex min-h-screen flex-col bg-canvas">
      <Header />

      <main
        key={location.pathname}
        className="mx-auto w-full max-w-360 flex-1 animate-rise px-5 py-9 sm:px-9"
      >
        <Outlet />
      </main>
    </div>
  )
}
