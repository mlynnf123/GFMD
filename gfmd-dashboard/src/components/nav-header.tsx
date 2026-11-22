'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function NavHeader() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Narc Gone' },
    { href: '/centrifuge', label: 'Silencer Centrifuge' },
    { href: '/spectrum', label: 'Spectrum dx' },
  ];

  return (
    <nav
      className="w-full border-b"
      style={{ borderColor: '#efebe2', backgroundColor: '#ffffff' }}
    >
      <div className="max-w-7xl mx-auto px-4 md:px-8 flex items-center gap-8 h-12">
        <span className="text-sm font-normal" style={{ color: '#272030' }}>
          GFMD
        </span>
        <div className="flex items-center gap-6">
          {links.map((link) => {
            const isActive =
              link.href === '/'
                ? pathname === '/'
                : pathname.startsWith(link.href);

            return (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm font-normal py-3 border-b-2 transition-colors"
                style={{
                  color: isActive ? '#4e2780' : '#272030',
                  borderColor: isActive ? '#4e2780' : 'transparent',
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
