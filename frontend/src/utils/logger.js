/**
 * Enhanced logger utility for frontend application
 * - Logs to console
 * - Captures console logs to localStorage
 * - Supports exporting logs to file
 */

const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR'
};

// Enable all logging in development, only warnings and errors in production
const LOG_LEVEL = process.env.NODE_ENV === 'production' ? LOG_LEVELS.WARN : LOG_LEVELS.DEBUG;

// Storage key for logs in localStorage
const STORAGE_KEY = 'ledgerlink_console_logs';
const MAX_LOGS = 10000; // Maximum number of logs to keep in storage

const getTimestamp = () => new Date().toISOString();

const formatMessage = (level, message, data = null) => {
  const timestamp = getTimestamp();
  const dataString = data ? `\nData: ${JSON.stringify(data, null, 2)}` : '';
  return `[${timestamp}] [${level}] ${message}${dataString}`;
};

const shouldLog = (messageLevel) => {
  const levels = Object.values(LOG_LEVELS);
  const currentLevelIndex = levels.indexOf(LOG_LEVEL);
  const messageLevelIndex = levels.indexOf(messageLevel);
  return messageLevelIndex >= currentLevelIndex;
};

// Function to store logs to localStorage
const storeLog = (level, message, data = null) => {
  try {
    // Get existing logs
    const existingLogs = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    
    // Add new log with timestamp
    const newLog = {
      timestamp: getTimestamp(),
      level,
      message,
      data: data ? JSON.stringify(data) : null,
    };
    
    // Keep only the most recent logs
    const updatedLogs = [newLog, ...existingLogs].slice(0, MAX_LOGS);
    
    // Store back to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedLogs));
  } catch (err) {
    console.error('Error storing log:', err);
  }
};

// Helper to format console arguments
const formatArgument = (arg) => {
  if (arg === undefined) return 'undefined';
  if (arg === null) return 'null';
  
  try {
    if (typeof arg === 'object') {
      return JSON.stringify(arg);
    }
    return String(arg);
  } catch (e) {
    return '[Object could not be stringified]';
  }
};

// Console Capture System
// We'll capture all browser console logs and store them
let consoleOverrideInitialized = false;

const setupConsoleCapture = () => {
  if (typeof window !== 'undefined' && !consoleOverrideInitialized) {
    consoleOverrideInitialized = true;
    
    const originalConsole = {
      log: console.log,
      debug: console.debug,
      info: console.info,
      warn: console.warn,
      error: console.error
    };
    
    console.log = (...args) => {
      originalConsole.log(...args);
      storeLog('LOG', args.map(arg => formatArgument(arg)).join(' '));
    };
    
    console.debug = (...args) => {
      originalConsole.debug(...args);
      storeLog('DEBUG', args.map(arg => formatArgument(arg)).join(' '));
    };
    
    console.info = (...args) => {
      originalConsole.info(...args);
      storeLog('INFO', args.map(arg => formatArgument(arg)).join(' '));
    };
    
    console.warn = (...args) => {
      originalConsole.warn(...args);
      storeLog('WARN', args.map(arg => formatArgument(arg)).join(' '));
    };
    
    console.error = (...args) => {
      originalConsole.error(...args);
      storeLog('ERROR', args.map(arg => formatArgument(arg)).join(' '));
    };
    
    window.addEventListener('error', (event) => {
      storeLog('ERROR', 'Uncaught error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack || 'No stack trace'
      });
    });
    
    window.addEventListener('unhandledrejection', (event) => {
      storeLog('ERROR', 'Unhandled promise rejection', {
        reason: formatArgument(event.reason),
      });
    });
  }
};

// Initialize console capture
if (typeof window !== 'undefined') {
  // Setup when the module is loaded
  setupConsoleCapture();
  
  // Also try to setup on DOMContentLoaded
  window.addEventListener('DOMContentLoaded', setupConsoleCapture);
}

const logger = {
  debug: (message, data = null) => {
    if (shouldLog(LOG_LEVELS.DEBUG)) {
      console.debug(formatMessage(LOG_LEVELS.DEBUG, message, data));
      storeLog(LOG_LEVELS.DEBUG, message, data);
    }
  },

  info: (message, data = null) => {
    if (shouldLog(LOG_LEVELS.INFO)) {
      console.info(formatMessage(LOG_LEVELS.INFO, message, data));
      storeLog(LOG_LEVELS.INFO, message, data);
    }
  },

  warn: (message, data = null) => {
    if (shouldLog(LOG_LEVELS.WARN)) {
      console.warn(formatMessage(LOG_LEVELS.WARN, message, data));
      storeLog(LOG_LEVELS.WARN, message, data);
    }
  },

  error: (message, error = null) => {
    if (shouldLog(LOG_LEVELS.ERROR)) {
      const errorData = error ? {
        message: error.message,
        stack: error.stack,
        ...error
      } : null;
      console.error(formatMessage(LOG_LEVELS.ERROR, message, errorData));
      storeLog(LOG_LEVELS.ERROR, message, errorData);
    }
  },

  // Specific API logging methods
  logApiRequest: (method, url, options) => {
    if (shouldLog(LOG_LEVELS.DEBUG)) {
      const requestData = {
        method,
        url,
        headers: options.headers,
        body: options.body ? JSON.parse(options.body) : undefined
      };
      logger.debug(`API Request: ${method} ${url}`, requestData);
    }
  },

  logApiResponse: (method, url, response, data) => {
    const level = response.ok ? LOG_LEVELS.DEBUG : LOG_LEVELS.ERROR;
    if (shouldLog(level)) {
      const responseData = {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        data
      };
      logger[level === LOG_LEVELS.DEBUG ? 'debug' : 'error'](
        `API Response: ${method} ${url}`,
        responseData
      );
    }
  },

  logApiError: (method, url, error) => {
    logger.error(`API Error: ${method} ${url}`, error);
  },
  
  // Utilities for accessing and exporting logs
  
  // Get all stored logs
  getLogs: () => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch (err) {
      console.error('Error retrieving logs:', err);
      return [];
    }
  },
  
  // Clear all stored logs
  clearLogs: () => {
    localStorage.removeItem(STORAGE_KEY);
  },
  
  // Export logs to file
  exportLogs: () => {
    try {
      const logs = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `ledgerlink-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
      a.click();
      
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting logs:', err);
    }
  },
  
  // Save logs to server-side file system
  saveLogsToServer: async () => {
    try {
      const logs = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      
      if (logs.length === 0) {
        console.warn('No logs to save to server');
        return { success: false, error: 'No logs to save' };
      }
      
      const response = await fetch('/api/v1/logs/client/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include authorization if user is logged in
          ...(localStorage.getItem('auth_token') && {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          })
        },
        body: JSON.stringify({ logs })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        console.info(`Successfully saved ${logs.length} logs to server`);
        return { success: true, ...data };
      } else {
        console.error('Error saving logs to server:', data);
        return { success: false, error: data.error || 'Failed to save logs to server' };
      }
    } catch (err) {
      console.error('Error saving logs to server:', err);
      return { success: false, error: err.message };
    }
  }
};

export default logger;