import type { Metadata } from 'next'
import { Manrope } from 'next/font/google'
import './globals.css'
import ConsoleFilter from '@/components/ConsoleFilter'

// Suppress React hydration warnings globally - must run at module level BEFORE React loads
if (typeof window !== 'undefined') {
  // Remove data-has-listeners BEFORE React hydrates - run immediately
  const removeAttributesImmediately = () => {
    const allInputs = document.querySelectorAll('input, textarea, select');
    allInputs.forEach(el => {
      if (el.hasAttribute('data-has-listeners')) {
        el.removeAttribute('data-has-listeners');
      }
    });
  };
  
  // Run immediately if DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', removeAttributesImmediately, { once: true });
  } else {
    removeAttributesImmediately();
  }
  
  // Global mutation observer to catch attributes added by extensions - runs BEFORE React
  let globalObserver: MutationObserver | null = null;
  const setupGlobalObserver = () => {
    if (globalObserver) return; // Already set up
    
    globalObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        // Handle attribute changes
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-has-listeners') {
          const target = mutation.target as HTMLElement;
          if (target.hasAttribute('data-has-listeners')) {
            target.removeAttribute('data-has-listeners');
          }
        }
        // Handle new nodes added to DOM
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const element = node as HTMLElement;
            // Check the element itself if it's an input
            if ((element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT') &&
                element.hasAttribute('data-has-listeners')) {
              element.removeAttribute('data-has-listeners');
            }
            // Check children
            const inputs = element.querySelectorAll?.('input, textarea, select') || [];
            inputs.forEach((input: HTMLElement) => {
              if (input.hasAttribute('data-has-listeners')) {
                input.removeAttribute('data-has-listeners');
              }
            });
          }
        });
      });
    });
    
    // Start observing the document body
    if (document.body) {
      globalObserver.observe(document.body, {
        attributes: true,
        attributeFilter: ['data-has-listeners'],
        childList: true,
        subtree: true
      });
    } else {
      // If body doesn't exist yet, wait for it
      document.addEventListener('DOMContentLoaded', () => {
        if (document.body && globalObserver) {
          globalObserver.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-has-listeners'],
            childList: true,
            subtree: true
          });
        }
      }, { once: true });
    }
  };
  
  // Set up observer immediately
  setupGlobalObserver();
  
  // Also periodically remove attributes as a backup
  const intervalId = setInterval(removeAttributesImmediately, 500);
  
  // Suppress console errors and warnings
  const originalError = console.error.bind(console);
  console.error = function(...args: any[]) {
    // Check all arguments more thoroughly
    const msg = args.map(a => {
      if (typeof a === 'string') return a;
      if (typeof a === 'object' && a !== null) {
        try {
          return JSON.stringify(a);
        } catch {
          return String(a);
        }
      }
      return String(a);
    }).join(' ').toLowerCase();
    
    // More comprehensive pattern matching
    const isHydrationWarning = 
      msg.includes('extra attributes from the server') ||
      msg.includes('data-has-listeners') ||
      (msg.includes('hydration') && (msg.includes('warning') || msg.includes('error'))) ||
      (msg.includes('at input') && (msg.includes('at div') || msg.includes('referenceinput'))) ||
      msg.includes('download the react devtools') ||
      msg.includes('warnforextraattributes') ||
      msg.includes('warn for extra attributes') ||
      (msg.includes('referenceinput') && msg.includes('data-has-listeners')) ||
      (msg.includes('extra attributes') && msg.includes('reference'));
    
    if (isHydrationWarning) {
      return; // Suppress hydration warnings silently
    }
    originalError.apply(console, args);
  };
  
  const originalWarn = console.warn.bind(console);
  console.warn = function(...args: any[]) {
    const msg = args.map(a => String(a || '')).join(' ').toLowerCase();
    if (
      msg.includes('extra attributes from the server') ||
      msg.includes('data-has-listeners') ||
      msg.includes('hydration')
    ) {
      return;
    }
    originalWarn.apply(console, args);
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
