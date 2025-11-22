'use client';

import { useEffect } from 'react';

export default function ConsoleFilter() {
  useEffect(() => {
    // Filter out noisy browser extension messages - run IMMEDIATELY on mount
    const originalLog = console.log;
    const originalInfo = console.info;
    const originalWarn = console.warn;
    const originalError = console.error;

    const shouldFilter = (args: any[]): boolean => {
      // Convert all arguments to a searchable string - check both string and object properties
      let message = '';
      
      for (const arg of args) {
        if (typeof arg === 'string') {
          message += ' ' + arg.toLowerCase();
        } else if (typeof arg === 'object' && arg !== null) {
          // Check object properties, especially for React errors
          try {
            const str = JSON.stringify(arg).toLowerCase();
            message += ' ' + str;
          } catch {
            // If stringify fails, check toString
            message += ' ' + String(arg).toLowerCase();
          }
          
          // Check specific properties that React errors have
          if (arg && typeof arg === 'object') {
            // Check for React error properties
            if ('message' in arg) message += ' ' + String(arg.message).toLowerCase();
            if ('stack' in arg) {
              const stack = String(arg.stack).toLowerCase();
              message += ' ' + stack;
            }
          }
        } else {
          message += ' ' + String(arg).toLowerCase();
        }
      }
      
      // Filter out known noisy messages - be specific to avoid blocking real errors
      const noisyPatterns = [
        'contentscript.js',
        'citation_search',
        'check_if_pdf',
        'scrape',
        'w.fn.init',
        'download the react devtools',
        // Hydration warnings - check for multiple patterns
        message.includes('extra attributes from the server') && message.includes('data-has-listeners') ? 'hydration-warning' : null,
        message.includes('extra attributes') && message.includes('referenceinput') ? 'hydration-warning' : null,
        message.includes('warnforextraattributes') || message.includes('warn for extra attributes') ? 'hydration-warning' : null,
        (message.includes('at input') && message.includes('at div') && message.includes('referenceinput')) ? 'hydration-warning' : null,
        'data-lt-installed',
        'running ginger widget',
        'fast refresh',
        // Don't filter these - they might contain real errors
        // 'react-dom.development.js',
        // 'app-index.js',
        // 'main-app.js',
        // 'hydration-error-info.js',
      ].filter(Boolean); // Remove nulls
      
      // Check if any pattern matches
      const shouldFilterResult = noisyPatterns.some(pattern => 
        message.includes(pattern.toLowerCase())
      );
      
      return shouldFilterResult;
    };

    // Override console methods
    console.log = function(...args: any[]) {
      if (!shouldFilter(args)) {
        originalLog.apply(console, args);
      }
    };

    console.info = function(...args: any[]) {
      if (!shouldFilter(args)) {
        originalInfo.apply(console, args);
      }
    };

    console.warn = function(...args: any[]) {
      if (!shouldFilter(args)) {
        originalWarn.apply(console, args);
      }
    };

    console.error = function(...args: any[]) {
      if (!shouldFilter(args)) {
        originalError.apply(console, args);
      }
    };

    // Also intercept React's error handler if possible
    if (typeof window !== 'undefined') {
      const originalOnError = window.onerror;
      window.onerror = function(message, source, lineno, colno, error) {
        const messageStr = String(message || '').toLowerCase();
        if (
          messageStr.includes('extra attributes from the server') ||
          messageStr.includes('data-has-listeners') ||
          messageStr.includes('hydration')
        ) {
          return true; // Suppress the error
        }
        if (originalOnError) {
          return originalOnError.call(window, message, source, lineno, colno, error);
        }
        return false;
      };

      const originalOnUnhandledRejection = window.onunhandledrejection;
      window.onunhandledrejection = function(event: PromiseRejectionEvent) {
        const reason = String(event.reason || '').toLowerCase();
        if (
          reason.includes('extra attributes from the server') ||
          reason.includes('data-has-listeners') ||
          reason.includes('hydration')
        ) {
          event.preventDefault();
          return;
        }
        if (originalOnUnhandledRejection) {
          return originalOnUnhandledRejection.call(window, event);
        }
      };

      // Cleanup on unmount
      return () => {
        console.log = originalLog;
        console.info = originalInfo;
        console.warn = originalWarn;
        console.error = originalError;
        window.onerror = originalOnError;
        window.onunhandledrejection = originalOnUnhandledRejection;
      };
    } else {
      // Cleanup on unmount (no window)
      return () => {
        console.log = originalLog;
        console.info = originalInfo;
        console.warn = originalWarn;
        console.error = originalError;
      };
    }
  }, []);

  return null; // This component doesn't render anything
}

