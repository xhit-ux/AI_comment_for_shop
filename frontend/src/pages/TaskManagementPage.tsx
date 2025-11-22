import React from 'react'
import { Card, Table, Tag, Button, Space, Typography } from 'antd'
import { EyeOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons'

const { Title, Paragraph } = Typography

const TaskManagementPage: React.FC = () => {
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '电商平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform: string) => {
        const platformMap: Record<string, { color: string; text: string }> = {
          jd: { color: 'red', text: '京东' },
          taobao: { color: 'orange', text: '淘宝' },
          tmall: { color: 'blue', text: '天猫' },
          pdd: { color: 'green', text: '拼多多' },
        }
        const config = platformMap[platform] || { color: 'default', text: platform }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          pending: { color: 'orange', text: '待采集' },
          collecting: { color: 'blue', text: '采集中' },
          cleaning: { color: 'cyan', text: '清洗中' },
          analyzing: { color: 'purple', text: '分析中' },
          completed: { color: 'green', text: '已完成' },
          failed: { color: 'red', text: '失败' },
        }
        const config = statusMap[status] || { color: 'default', text: status }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '评论数量',
      dataIndex: 'commentCount',
      key: 'commentCount',
      render: (count: number) => `${count} 条`,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />}
            disabled={record.status !== 'completed'}
          >
            查看
          </Button>
          <Button 
            type="link" 
            icon={<DownloadOutlined />}
            disabled={record.status !== 'completed'}
          >
            导出
          </Button>
          <Button 
            type="link" 
            icon={<ReloadOutlined />}
            disabled={record.status === 'collecting' || record.status === 'analyzing'}
          >
            重试
          </Button>
        </Space>
      ),
    },
  ]

  const data = [
    {
      key: '1',
      id: 'task_001',
      name: 'iPhone 15 评论分析',
      platform: 'jd',
      status: 'completed',
      commentCount: 2456,
      createdAt: '2024-01-15 10:30:00',
    },
    {
      key: '2',
      id: 'task_002',
      name: '小米14 用户反馈',
      platform: 'tmall',
      status: 'analyzing',
      commentCount: 1872,
      createdAt: '2024-01-15 14:20:00',
    },
    {
      key: '3',
      id: 'task_003',
      name: '华为Mate 60 评价',
      platform: 'jd',
      status: 'collecting',
      commentCount: 3124,
      createdAt: '2024-01-15 16:45:00',
    },
    {
      key: '4',
      id: 'task_004',
      name: 'AirPods Pro 评论',
      platform: 'pdd',
      status: 'failed',
      commentCount: 0,
      createdAt: '2024-01-14 09:15:00',
    },
  ]

  return (
    <div>
      <Title level={2}>任务管理</Title>
      <Paragraph style={{ color: '#666', marginBottom: '32px' }}>
        查看和管理所有分析任务，监控任务状态和进度
      </Paragraph>

      <Card>
        <Table 
          columns={columns} 
          dataSource={data}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条任务`,
          }}
        />
      </Card>
    </div>
  )
}

export default TaskManagementPage
