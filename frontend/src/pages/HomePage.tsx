import React from 'react'
import { Card, Row, Col, Statistic, Button, Typography } from 'antd'
import { Link } from 'react-router-dom'
import { 
  BarChartOutlined, 
  PlusOutlined, 
  CheckCircleOutlined,
  ClockCircleOutlined 
} from '@ant-design/icons'

const { Title, Paragraph } = Typography

const HomePage: React.FC = () => {
  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <Title level={1} style={{ color: '#1890ff', marginBottom: '16px' }}>
          电商评论情感分析系统
        </Title>
        <Paragraph style={{ fontSize: '16px', color: '#666', maxWidth: '600px', margin: '0 auto' }}>
          基于大模型AI的智能电商评论分析平台，支持京东、淘宝等主流电商平台的评论采集、情感分析和可视化展示
        </Paragraph>
      </div>

      <Row gutter={[24, 24]} style={{ marginBottom: '48px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总分析任务"
              value={156}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已完成任务"
              value={128}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="进行中任务"
              value={12}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="分析评论数"
              value={45876}
              suffix="条"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={8}>
          <Card 
            title="快速开始" 
            bordered={false}
            style={{ height: '100%' }}
          >
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <PlusOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
              <Title level={4}>新建分析任务</Title>
              <Paragraph style={{ color: '#666', marginBottom: '24px' }}>
                输入商品链接或ID，配置分析参数，开始您的第一个评论分析任务
              </Paragraph>
              <Link to="/task">
                <Button type="primary" size="large" icon={<PlusOutlined />}>
                  创建新任务
                </Button>
              </Link>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card 
            title="任务管理" 
            bordered={false}
            style={{ height: '100%' }}
          >
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <BarChartOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
              <Title level={4}>查看分析结果</Title>
              <Paragraph style={{ color: '#666', marginBottom: '24px' }}>
                管理所有分析任务，查看任务状态，浏览详细的分析结果和可视化图表
              </Paragraph>
              <Link to="/management">
                <Button size="large" icon={<BarChartOutlined />}>
                  任务管理
                </Button>
              </Link>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card 
            title="系统特性" 
            bordered={false}
            style={{ height: '100%' }}
          >
            <div style={{ padding: '20px 0' }}>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                <li style={{ marginBottom: '12px', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <strong>多平台支持</strong> - 京东、淘宝等主流电商平台
                </li>
                <li style={{ marginBottom: '12px', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <strong>AI情感分析</strong> - 基于大模型的精准情感识别
                </li>
                <li style={{ marginBottom: '12px', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <strong>数据可视化</strong> - 丰富的图表和统计报告
                </li>
                <li style={{ padding: '8px 0' }}>
                  <strong>数据导出</strong> - 支持CSV格式数据导出
                </li>
              </ul>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default HomePage
