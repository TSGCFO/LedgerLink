import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  CssBaseline,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import {
  People as PeopleIcon,
  Dashboard as DashboardIcon,
  BusinessCenter as BusinessCenterIcon,
  Build as BuildIcon,
  ShoppingCart as ShoppingCartIcon,
  Inventory as InventoryIcon,
  Description as DescriptionIcon,
  LocalShipping as LocalShippingIcon,
  Rule as RuleIcon,
  Category as CategoryIcon,
  Inventory2 as Inventory2Icon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';

// Import our components
import Login from './components/auth/Login';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { isAuthenticated } from './utils/auth';
import CustomerList from './components/customers/CustomerList';
import CustomerForm from './components/customers/CustomerForm';
import CustomerServiceList from './components/customer-services/CustomerServiceList';
import CustomerServiceForm from './components/customer-services/CustomerServiceForm';
import ServiceList from './components/services/ServiceList';
import ServiceForm from './components/services/ServiceForm';
import OrderList from './components/orders/OrderList';
import OrderForm from './components/orders/OrderForm';
import ProductList from './components/products/ProductList';
import ProductForm from './components/products/ProductForm';
import InsertList from './components/inserts/InsertList';
import InsertForm from './components/inserts/InsertForm';
import CADShippingList from './components/shipping/CADShippingList';
import CADShippingForm from './components/shipping/CADShippingForm';
import USShippingList from './components/shipping/USShippingList';
import USShippingForm from './components/shipping/USShippingForm';
import RulesManagement from './components/rules/RulesManagement';
import MaterialList from './components/materials/MaterialList';
import MaterialForm from './components/materials/MaterialForm';
import BoxPriceList from './components/materials/BoxPriceList';
import BoxPriceForm from './components/materials/BoxPriceForm';
import BulkOperations from './components/bulk-operations/BulkOperations';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Drawer width
const drawerWidth = 240;

function App() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated());

  useEffect(() => {
    const handleAuthChange = (event) => {
      setAuthenticated(event.detail.isAuthenticated);
    };

    window.addEventListener('auth_state_changed', handleAuthChange);

    return () => {
      window.removeEventListener('auth_state_changed', handleAuthChange);
    };
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          
          {/* App Bar */}
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <Typography variant="h6" noWrap component="div">
                LedgerLink
              </Typography>
            </Toolbar>
          </AppBar>

          {/* Sidebar - Only show when authenticated */}
          {authenticated && (
            <Drawer
              variant="permanent"
              sx={{
                width: drawerWidth,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                  width: drawerWidth,
                  boxSizing: 'border-box',
                },
              }}
            >
              <Toolbar /> {/* This creates space for the AppBar */}
              <Box sx={{ overflow: 'auto' }}>
                <List>
                  <ListItem button component={Link} to="/">
                    <ListItemIcon>
                      <DashboardIcon />
                    </ListItemIcon>
                    <ListItemText primary="Dashboard" />
                  </ListItem>
                  <ListItem button component={Link} to="/customers">
                    <ListItemIcon>
                      <PeopleIcon />
                    </ListItemIcon>
                    <ListItemText primary="Customers" />
                  </ListItem>
                  <ListItem button component={Link} to="/customer-services">
                    <ListItemIcon>
                      <BusinessCenterIcon />
                    </ListItemIcon>
                    <ListItemText primary="Customer Services" />
                  </ListItem>
                  <ListItem button component={Link} to="/services">
                    <ListItemIcon>
                      <BuildIcon />
                    </ListItemIcon>
                    <ListItemText primary="Services" />
                  </ListItem>
                  <ListItem button component={Link} to="/orders">
                    <ListItemIcon>
                      <ShoppingCartIcon />
                    </ListItemIcon>
                    <ListItemText primary="Orders" />
                  </ListItem>
                  <ListItem button component={Link} to="/products">
                    <ListItemIcon>
                      <InventoryIcon />
                    </ListItemIcon>
                    <ListItemText primary="Products" />
                  </ListItem>
                  <ListItem button component={Link} to="/materials">
                    <ListItemIcon>
                      <CategoryIcon />
                    </ListItemIcon>
                    <ListItemText primary="Materials" />
                  </ListItem>
                  <ListItem button component={Link} to="/box-prices">
                    <ListItemIcon>
                      <Inventory2Icon />
                    </ListItemIcon>
                    <ListItemText primary="Box Prices" />
                  </ListItem>
                  <ListItem button component={Link} to="/inserts">
                    <ListItemIcon>
                      <DescriptionIcon />
                    </ListItemIcon>
                    <ListItemText primary="Inserts" />
                  </ListItem>
                  <ListItem button component={Link} to="/rules">
                    <ListItemIcon>
                      <RuleIcon />
                    </ListItemIcon>
                    <ListItemText primary="Rules" />
                  </ListItem>
                  <ListItem button component={Link} to="/shipping/cad">
                    <ListItemIcon>
                      <LocalShippingIcon />
                    </ListItemIcon>
                    <ListItemText primary="CAD Shipping" />
                  </ListItem>
                  <ListItem button component={Link} to="/shipping/us">
                    <ListItemIcon>
                      <LocalShippingIcon />
                    </ListItemIcon>
                    <ListItemText primary="US Shipping" />
                  </ListItem>
                  <ListItem button component={Link} to="/bulk-operations">
                    <ListItemIcon>
                      <CloudUploadIcon />
                    </ListItemIcon>
                    <ListItemText primary="Bulk Operations" />
                  </ListItem>
                </List>
              </Box>
            </Drawer>
          )}

          {/* Main Content */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: authenticated ? { sm: `calc(100% - ${drawerWidth}px)` } : '100%',
            }}
          >
            <Toolbar /> {/* This creates space for the AppBar */}
            <Container maxWidth="lg">
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />

                {/* Protected Routes */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Typography variant="h4" component="h1">
                        Welcome to LedgerLink
                      </Typography>
                    </ProtectedRoute>
                  }
                />
                <Route path="/customers" element={<ProtectedRoute><CustomerList /></ProtectedRoute>} />
                <Route path="/customers/new" element={<ProtectedRoute><CustomerForm /></ProtectedRoute>} />
                <Route path="/customers/:id/edit" element={<ProtectedRoute><CustomerForm /></ProtectedRoute>} />
                <Route path="/customer-services" element={<ProtectedRoute><CustomerServiceList /></ProtectedRoute>} />
                <Route path="/customer-services/new" element={<ProtectedRoute><CustomerServiceForm /></ProtectedRoute>} />
                <Route path="/customer-services/:id/edit" element={<ProtectedRoute><CustomerServiceForm /></ProtectedRoute>} />
                <Route path="/services" element={<ProtectedRoute><ServiceList /></ProtectedRoute>} />
                <Route path="/services/new" element={<ProtectedRoute><ServiceForm /></ProtectedRoute>} />
                <Route path="/services/:id/edit" element={<ProtectedRoute><ServiceForm /></ProtectedRoute>} />
                <Route path="/products" element={<ProtectedRoute><ProductList /></ProtectedRoute>} />
                <Route path="/products/new" element={<ProtectedRoute><ProductForm /></ProtectedRoute>} />
                <Route path="/products/:id/edit" element={<ProtectedRoute><ProductForm /></ProtectedRoute>} />
                <Route path="/materials" element={<ProtectedRoute><MaterialList /></ProtectedRoute>} />
                <Route path="/materials/new" element={<ProtectedRoute><MaterialForm /></ProtectedRoute>} />
                <Route path="/materials/:id/edit" element={<ProtectedRoute><MaterialForm /></ProtectedRoute>} />
                <Route path="/box-prices" element={<ProtectedRoute><BoxPriceList /></ProtectedRoute>} />
                <Route path="/box-prices/new" element={<ProtectedRoute><BoxPriceForm /></ProtectedRoute>} />
                <Route path="/box-prices/:id/edit" element={<ProtectedRoute><BoxPriceForm /></ProtectedRoute>} />
                <Route path="/inserts" element={<ProtectedRoute><InsertList /></ProtectedRoute>} />
                <Route path="/inserts/new" element={<ProtectedRoute><InsertForm /></ProtectedRoute>} />
                <Route path="/inserts/:id/edit" element={<ProtectedRoute><InsertForm /></ProtectedRoute>} />
                <Route path="/orders" element={<ProtectedRoute><OrderList /></ProtectedRoute>} />
                <Route path="/orders/new" element={<ProtectedRoute><OrderForm /></ProtectedRoute>} />
                <Route path="/orders/:id/edit" element={<ProtectedRoute><OrderForm /></ProtectedRoute>} />
                <Route path="/rules" element={<ProtectedRoute><RulesManagement /></ProtectedRoute>} />
                <Route path="/shipping/cad" element={<ProtectedRoute><CADShippingList /></ProtectedRoute>} />
                <Route path="/shipping/cad/new" element={<ProtectedRoute><CADShippingForm /></ProtectedRoute>} />
                <Route path="/shipping/cad/:id/edit" element={<ProtectedRoute><CADShippingForm /></ProtectedRoute>} />
                <Route path="/shipping/us" element={<ProtectedRoute><USShippingList /></ProtectedRoute>} />
                <Route path="/shipping/us/new" element={<ProtectedRoute><USShippingForm /></ProtectedRoute>} />
                <Route path="/shipping/us/:id/edit" element={<ProtectedRoute><USShippingForm /></ProtectedRoute>} />
                <Route path="/bulk-operations" element={<ProtectedRoute><BulkOperations /></ProtectedRoute>} />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
