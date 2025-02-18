/**
 * Logger utility for frontend application
 */

const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR'
};

// Enable all logging in development, only warnings and errors in production
const LOG_LEVEL = process.env.NODE_ENV === 'production' ? LOG_LEVELS.WARN : LOG_LEVELS.DEBUG;

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

const logger = {
  debug: (message, data = null) => {
    if (shouldLog(LOG_LEVELS.DEBUG)) {
      console.debug(formatMessage(LOG_LEVELS.DEBUG, message, data));
    }
  },

  info: (message, data = null) => {
    if (shouldLog(LOG_LEVELS.INFO)) {
      console.info(formatMessage(LOG_LEVELS.INFO, message, data));
    }
  },

  warn: (message, data = null) => {
    if (shouldLog(LOG_LEVELS.WARN)) {
      console.warn(formatMessage(LOG_LEVELS.WARN, message, data));
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
  }
};

export default logger;