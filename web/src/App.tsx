import { useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid2 as Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Box,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fab,
  Alert
} from '@mui/material'
import {
  Home,
  Settings,
  Info,
  Add,
  MusicNote
} from '@mui/icons-material'
import reactLogo from './assets/react.svg'
import appLogo from '/favicon.svg'
import PWABadge from './PWABadge.tsx'

function App() {
  const [count, setCount] = useState(0)
  const [textValue, setTextValue] = useState('')

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <MusicNote sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Flute - MUI Demo
          </Typography>
          <Button color="inherit">Login</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={4}>
          {/* Welcome Section */}
          <Grid xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Avatar src={appLogo} alt="Flute logo" />
                  <Avatar src={reactLogo} alt="React logo" />
                  <Typography variant="h4" component="h1">
                    Welcome to Flute
                  </Typography>
                </Box>
                <Alert severity="success" sx={{ mb: 2 }}>
                  MUI has been successfully integrated!
                </Alert>
                <Typography variant="body1" paragraph>
                  This page demonstrates various Material-UI components working with React 19 and Vite.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Interactive Components */}
          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h2" gutterBottom>
                  Interactive Counter
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <Button 
                    variant="contained" 
                    onClick={() => setCount((count) => count + 1)}
                    size="large"
                  >
                    Count is {count}
                  </Button>
                  <Button 
                    variant="outlined" 
                    onClick={() => setCount(0)}
                  >
                    Reset
                  </Button>
                  <Box display="flex" gap={1}>
                    <Chip label={`Current: ${count}`} color="primary" />
                    <Chip 
                      label={count > 5 ? "High" : "Low"} 
                      color={count > 5 ? "warning" : "default"}
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Form Components */}
          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h2" gutterBottom>
                  Form Elements
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <TextField
                    label="Enter some text"
                    variant="outlined"
                    value={textValue}
                    onChange={(e) => setTextValue(e.target.value)}
                    fullWidth
                  />
                  <Button variant="contained" color="secondary">
                    Submit Form
                  </Button>
                  {textValue && (
                    <Alert severity="info">
                      You typed: {textValue}
                    </Alert>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Navigation List */}
          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h2" gutterBottom>
                  Navigation Menu
                </Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Home />
                    </ListItemIcon>
                    <ListItemText primary="Home" secondary="Main dashboard" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Settings />
                    </ListItemIcon>
                    <ListItemText primary="Settings" secondary="App configuration" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Info />
                    </ListItemIcon>
                    <ListItemText primary="About" secondary="App information" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Development Info */}
          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h2" gutterBottom>
                  Development Info
                </Typography>
                <Typography variant="body2" paragraph>
                  Edit <code>src/App.tsx</code> and save to test HMR
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap">
                  <Chip label="React 19" variant="outlined" />
                  <Chip label="Material-UI" variant="outlined" />
                  <Chip label="Vite" variant="outlined" />
                  <Chip label="TypeScript" variant="outlined" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <PWABadge />
      </Container>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
      >
        <Add />
      </Fab>
    </Box>
  )
}

export default App
