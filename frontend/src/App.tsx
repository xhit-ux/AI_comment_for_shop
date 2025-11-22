import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import TaskPage from './pages/TaskPage'
import AnalysisPage from './pages/AnalysisPage'
import TaskManagementPage from './pages/TaskManagementPage'

const { Content } = Layout

const App: React.FC = () => {
  return (
    <Layout>
      <Header />
      <Content style={{ padding: '24px', minHeight: 'calc(100vh - 64px)' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/task" element={<TaskPage />} />
          <Route path="/analysis/:taskId" element={<AnalysisPage />} />
          <Route path="/management" element={<TaskManagementPage />} />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App
