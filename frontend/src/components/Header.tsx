import React from 'react'
import { Layout, Menu, Button } from 'antd'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeOutlined, 
  PlusOutlined, 
  BarChartOutlined, 
  SettingOutlined 
} from '@ant-design/icons'

const { Header: AntHeader } = Layout

const Header: React.FC = () => {
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/task',
      icon: <PlusOutlined />,
      label: <Link to="/task">新建任务</Link>,
    },
    {
      key: '/management',
      icon: <SettingOutlined />,
      label: <Link to="/management">任务管理</Link>,
    },
  ]

  return (
    <AntHeader style={{ 
      display: 'flex', 
      alignItems: 'center',
      background: '#fff',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
      padding: '0 24px'
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginRight: 'auto' 
      }}>
        <BarChartOutlined style={{ 
          fontSize: '24px', 
          color: '#1890ff', 
          marginRight: '12px' 
        }} />
        <h1 style={{ 
          margin: 0, 
          fontSize: '20px', 
          fontWeight: 'bold',
          color: '#1890ff'
        }}>
          电商评论情感分析系统
        </h1>
      </div>
      
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        style={{ 
          border: 'none',
          background: 'transparent'
        }}
      />
    </AntHeader>
  )
}

export default Header
