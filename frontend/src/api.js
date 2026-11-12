import axios from 'axios'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 15000,
})

// Projects
export const getProjects    = ()               => API.get('/projects')
export const getFiles       = (project)        => API.get(`/projects/${project}/files`)
export const getFunctions   = (project, file)  => API.get(`/projects/${project}/files/${file}/functions`)
export const getSource      = (project, file)  => API.get(`/projects/${project}/files/${file}/source`)
export const getFnSource    = (project, file, fn) => API.get(`/projects/${project}/files/${file}/functions/${fn}/source`)
export const getFnAST       = (project, file, fn) => API.get(`/projects/${project}/files/${file}/functions/${fn}/ast`)

// Run
export const runFunction = (project, file, fn, args = []) =>
  API.post(`/projects/${project}/files/${file}/functions/${fn}/run`, { args })

// Analysis
export const analyzeAST      = (tests)  => API.post('/analyze/ast', { tests })
export const analyzeMutation = (data)   => API.post('/analyze/mutation', data)

// Stats
export const getStats = () => API.get('/stats')
