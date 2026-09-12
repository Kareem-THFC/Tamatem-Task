import { useState } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'

import { TomatoMark } from '@/components/brand/TomatoMark'
import { Button } from '@/components/ui/Button'
import { CoinAmount } from '@/components/ui/CoinAmount'
import { useAuth } from '@/context/auth-context'
import { cn } from '@/lib/cn'

export function Header() {
  const { user, isAuthenticated, signOut } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [openedAt, setOpenedAt] = useState<string | null>(null)
  const menuOpen = openedAt === location.pathname

  function setMenuOpen(open: boolean) {
    setOpenedAt(open ? location.pathname : null)
  }

  function handleSignOut() {
    setMenuOpen(false)
    signOut()
    navigate('/products')
  }

  function goFromMenu(to: string) {
    setMenuOpen(false)
    navigate(to)
  }

  return (
    <header className="border-b-[3px] border-ink bg-surface">
      <div className="mx-auto flex h-16 max-w-360 items-center gap-4 px-5 sm:px-9 md:h-18 lg:gap-8">
        <Link to="/products" className="flex min-w-0 items-center gap-2.5 md:gap-3">
          <span className="md:hidden">
            <TomatoMark size={34} />
          </span>
          <span className="hidden md:block">
            <TomatoMark size={40} />
          </span>

          <span className="truncate font-display text-lg font-semibold text-ink hidden md:text-[22px] lg:block">
            Loot Market
          </span>
        </Link>

        <nav className="hidden items-center gap-1.5 md:flex">
          <HeaderLink to="/products">Store</HeaderLink>
          {isAuthenticated && <HeaderLink to="/orders">Orders</HeaderLink>}
        </nav>

        <div className="ml-auto hidden items-center gap-3.5 md:flex">
          {user ? (
            <>
              <div className="flex items-center gap-2 rounded-full border-[2.5px] border-ink bg-cream py-1.5 pr-4 pl-2 shadow-hard-xs">
                <CoinAmount amount={user.gem_balance} />
              </div>

              <Avatar username={user.username} />

              <Button variant="secondary" size="sm" onClick={handleSignOut}>
                Sign out
              </Button>
            </>
          ) : (
            <>
              <Button variant="secondary" size="sm" onClick={() => navigate('/login')}>
                Sign in
              </Button>
              <Button size="sm" onClick={() => navigate('/register')}>
                Create account
              </Button>
            </>
          )}
        </div>

        <div className="ml-auto flex items-center gap-2.5 md:hidden">
          {user && (
            <div className="flex items-center rounded-full border-[2.5px] border-ink bg-cream py-1 pr-3 pl-1.5 shadow-hard-xs">
              <CoinAmount amount={user.gem_balance} size="sm" />
            </div>
          )}

          <MenuToggle open={menuOpen} onToggle={() => setMenuOpen(!menuOpen)} />
        </div>
      </div>

      {menuOpen && (
        <div
          id="header-menu"
          className="animate-rise border-t-[3px] border-ink bg-cream px-5 pt-4 pb-5 md:hidden"
        >
          {user && (
            <div className="mb-4 flex items-center gap-3">
              <Avatar username={user.username} />
              <span className="min-w-0">
                <span className="block truncate font-display text-[17px] font-semibold text-ink">
                  {user.username}
                </span>
                <span className="block text-[13px] font-bold text-ink-muted">
                  Signed in
                </span>
              </span>
            </div>
          )}

          <nav className="flex flex-col gap-1.5">
            <HeaderLink to="/products" stacked onNavigate={() => setMenuOpen(false)}>
              Store
            </HeaderLink>
            {isAuthenticated && (
              <HeaderLink to="/orders" stacked onNavigate={() => setMenuOpen(false)}>
                Orders
              </HeaderLink>
            )}
          </nav>

          <div className="mt-4 flex flex-col gap-2.5">
            {user ? (
              <Button variant="secondary" fullWidth onClick={handleSignOut}>
                Sign out
              </Button>
            ) : (
              <>
                <Button variant="secondary" fullWidth onClick={() => goFromMenu('/login')}>
                  Sign in
                </Button>
                <Button fullWidth onClick={() => goFromMenu('/register')}>
                  Create account
                </Button>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  )
}

function Avatar({ username }: { username: string }) {
  return (
    <span
      title={username}
      className="grid size-11 shrink-0 place-items-center rounded-[14px] border-[3px] border-ink bg-violet font-display text-lg font-semibold text-white shadow-[0_4px_0_rgba(42,26,20,0.25)]"
    >
      {username.charAt(0).toUpperCase()}
    </span>
  )
}

function MenuToggle({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-expanded={open}
      aria-controls="header-menu"
      aria-label={open ? 'Close menu' : 'Open menu'}
      className={cn(
        'grid size-11 shrink-0 cursor-pointer place-items-center rounded-xl',
        'border-[2.5px] border-ink shadow-hard-xs',
        'transition-[transform,box-shadow] duration-120 active:translate-y-1 active:shadow-none',
        open ? 'bg-sand' : 'bg-surface',
      )}
    >
      <span aria-hidden="true" className="relative block h-3.5 w-5">
        <span
          className={cn(
            'absolute left-0 block h-[2.5px] w-full rounded-full bg-ink transition-all duration-150',
            open ? 'top-[5.75px] rotate-45' : 'top-0',
          )}
        />
        <span
          className={cn(
            'absolute top-[5.75px] left-0 block h-[2.5px] w-full rounded-full bg-ink',
            'transition-opacity duration-150',
            open && 'opacity-0',
          )}
        />
        <span
          className={cn(
            'absolute left-0 block h-[2.5px] w-full rounded-full bg-ink transition-all duration-150',
            open ? 'top-[5.75px] -rotate-45' : 'top-[11.5px]',
          )}
        />
      </span>
    </button>
  )
}

function HeaderLink({
  to,
  children,
  stacked = false,
  onNavigate,
}: {
  to: string
  children: string
  stacked?: boolean
  onNavigate?: () => void
}) {
  return (
    <NavLink
      to={to}
      onClick={onNavigate}
      className={({ isActive }) =>
        cn(
          'rounded-xl transition-colors',
          stacked ? 'block px-4 py-3 text-[15px]' : 'px-4 py-2 text-sm',
          isActive
            ? 'border-2 border-ink bg-sand font-extrabold text-ink'
            : 'border-2 border-transparent font-bold text-ink-muted hover:bg-ink/6 hover:text-ink',
        )
      }
    >
      {children}
    </NavLink>
  )
}
