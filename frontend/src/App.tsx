import { Button, Container, Typography } from '@mui/material'
import axios from 'axios'
import { useState } from 'react'

export function App() {
  const [status, setStatus] = useState<string>('unknown')

  const checkHealth = async () => {
    const res = await axios.get('/api/health')
    setStatus(res.data.status)
  }

  return (
    <Container style={{ paddingTop: 40 }}>
      <Typography variant="h4">TourHub</Typography>

      <Typography style={{ marginTop: 20 }}>
        Backend status: {status}
      </Typography>

      <Button
        variant="contained"
        onClick={checkHealth}
        style={{ marginTop: 20 }}
      >
        Check backend
      </Button>
    </Container>
  )
}