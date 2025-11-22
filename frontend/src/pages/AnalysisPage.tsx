import React from 'react'
import { useParams } from 'react-router-dom'
import { Card, Row, Col, Typography } from 'antd'

const { Title, Paragraph } = Typography

const AnalysisPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>()

  return (
    <div>
      <Title level={2}>分析结果 - 任务 {taskId}</Title>
      <Paragraph style={{ color: '#666', marginBottom: '32px' }}>
        正在分析中，请稍候...
      </Paragraph>

      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card title="分析状态" style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }}>
              🔄
            </div>
            <Title level={3}>分析进行中</Title>
            <Paragraph style={{ color: '#666' }}>
              系统正在采集评论数据并进行情感分析，请耐心等待...
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default AnalysisPage
