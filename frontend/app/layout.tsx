import type { Metadata } from 'next'
import { Manrope } from 'next/font/google'
import './globals.css'
import ConsoleFilter from '@/components/ConsoleFilter'

// Suppress React hydration warnings globally - must run at module level
if (typeof window !== 'undefined') {
  const originalError = console.error.bind(console);
  console.error = function(...args: any[]) {
    const msg = args.map(a => String(a || '')).join(' ').toLowerCase();
    if (
      msg.includes('extra attributes from the server') ||
      msg.includes('data-has-listeners') ||
      msg.includes('extra attributes from the server') ||
      msg.toLowerCase().includes('hydration') ||
      msg.includes('hydration') && msg.includes('warning') ||
      msg.includes('at input') && msg.includes('at div') ||
      msg.includes('download the react devtools')
    ) {
      return; // Suppress hydration warnings silently
    }
    originalError.apply(console, args);
  };
}

const manrope = Manrope({
  subsets: ['latin'],
  variable: '--font-manrope',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'CreatorFlow AI - AI-Powered Content Creation',
  description: 'Generate viral hooks, scripts, shot lists, and music prompts for your content',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning className={manrope.variable}>
      <body suppressHydrationWarning>
        <ConsoleFilter />
        {children}
      </body>
    </html>
  )
}
