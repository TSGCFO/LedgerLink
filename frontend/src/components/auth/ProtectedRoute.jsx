import PropTypes from 'prop-types';

// Development version - bypasses authentication
const ProtectedRoute = ({ children }) => {
  // Set a development token if not present
  if (!localStorage.getItem('auth_token')) {
    localStorage.setItem('auth_token', 'development_token');
  }
  
  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ProtectedRoute;