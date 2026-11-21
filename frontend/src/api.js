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
export const runFunction = (project, file, fn, args = [], kwargs = {}) =>
  API.post(`/projects/${project}/files/${file}/functions/${fn}/run`, { args, kwargs }, { timeout: 30000 })

// Stage 1 — AI test generation
export const stage1Overview = ()                 => API.get('/stage1/overview', { timeout: 60000 })
export const stage1Item     = (id)               => API.get(`/stage1/items/${id}`)
export const stage1Save     = (id, tool, code)   => API.put(`/stage1/items/${id}/${tool}`, { code }, { timeout: 200000 })
export const stage1Run      = (id, tool)         => API.post(`/stage1/items/${id}/${tool}/run`, {}, { timeout: 200000 })
export const stage1Generate = (id, tool)         => API.post(`/stage1/items/${id}/${tool}/generate`, {}, { timeout: 400000 })
export const stage1Delete   = (id, tool)         => API.delete(`/stage1/items/${id}/${tool}`)
export const stage1ExportUrl = () => `${API.defaults.baseURL}/stage1/export.csv`

// Stats
export const getStats = () => API.get('/stats')
