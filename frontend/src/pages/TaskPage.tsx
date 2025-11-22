import React, { useState } from 'react'
import { 
  Card, 
  Form, 
  Input, 
  Select, 
  Button, 
  DatePicker, 
  InputNumber, 
  Switch, 
  message,
  Row,
  Col,
  Typography,
  Steps
} from 'antd'
import { useNavigate } from 'react-router-dom'
import { 
  ShoppingOutlined, 
  LinkOutlined, 
  SettingOutlined,
  CheckCircleOutlined 
} from '@ant-design/icons'

const { Title, Paragraph } = Typography
const { Step } = Steps
const { Option } = Select
const { TextArea } = Input

const TaskPage: React.FC = () => {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const taskId = Math.random().toString(36).substr(2, 9)
      message.success('任务创建成功！正在开始分析...')
      
      // 跳转到分析页面
      navigate(`/analysis/${taskId}`)
    } catch (error) {
      message.error('任务创建失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const steps = [
    {
      title: '商品信息',
      icon: <ShoppingOutlined />,
    },
    {
      title: '采集配置',
      icon: <SettingOutlined />,
    },
    {
      title: '确认创建',
      icon: <CheckCircleOutlined />,
    },
  ]

  return (
    <div>
      <Title level={2}>新建分析任务</Title>
      <Paragraph style={{ color: '#666', marginBottom: '32px' }}>
        输入商品信息并配置采集参数，系统将自动采集评论并进行情感分析
      </Paragraph>

      <Card>
        <Steps current={currentStep} style={{ marginBottom: '32px' }}>
          {steps.map(item => (
            <Step key={item.title} title={item.title} icon={item.icon} />
          ))}
        </Steps>

        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            platform: 'jd',
            maxComments: 100,
            includeFollowUp: true,
            timeRange: null,
          }}
        >
          {currentStep === 0 && (
            <Row gutter={24}>
              <Col span={24}>
                <Form.Item
                  label="电商平台"
                  name="platform"
                  rules={[{ required: true, message: '请选择电商平台' }]}
                >
                  <Select placeholder="选择电商平台">
                    <Option value="jd">京东</Option>
                    <Option value="taobao">淘宝</Option>
                    <Option value="tmall">天猫</Option>
                    <Option value="pdd">拼多多</Option>
                  </Select>
                </Form.Item>
              </Col>
              
              <Col span={24}>
                <Form.Item
                  label="商品链接"
                  name="productUrl"
                  rules={[{ required: true, message: '请输入商品链接' }]}
                >
                  <Input 
                    placeholder="请输入商品链接，例如：https://item.jd.com/123456.html" 
                    prefix={<LinkOutlined />}
                  />
                </Form.Item>
              </Col>

              <Col span={12}>
                <Form.Item
                  label="商品ID"
                  name="productId"
                >
                  <Input placeholder="可选：直接输入商品ID" />
                </Form.Item>
              </Col>

              <Col span={12}>
                <Form.Item
                  label="任务名称"
                  name="taskName"
                  rules={[{ required: true, message: '请输入任务名称' }]}
                >
                  <Input placeholder="输入任务名称，便于识别" />
                </Form.Item>
              </Col>

              <Col span={24}>
                <Form.Item
                  label="任务描述"
                  name="description"
                >
                  <TextArea 
                    rows={3} 
                    placeholder="可选：输入任务描述信息" 
                  />
                </Form.Item>
              </Col>
            </Row>
          )}

          {currentStep === 1 && (
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item
                  label="最大评论数"
                  name="maxComments"
                  rules={[{ required: true, message: '请输入最大评论数' }]}
                >
                  <InputNumber 
                    min={1} 
                    max={10000} 
                    style={{ width: '100%' }}
                    placeholder="最多采集多少条评论"
                  />
                </Form.Item>
              </Col>

              <Col span={12}>
                <Form.Item
                  label="时间范围"
                  name="timeRange"
                >
                  <DatePicker.RangePicker 
                    style={{ width: '100%' }}
                    placeholder={['开始时间', '结束时间']}
                  />
                </Form.Item>
              </Col>

              <Col span={24}>
                <Form.Item
                  label="包含追评"
                  name="includeFollowUp"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>

              <Col span={24}>
                <Form.Item
                  label="包含图片评论"
                  name="includeImageComments"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>

              <Col span={24}>
                <Form.Item
                  label="包含视频评论"
                  name="includeVideoComments"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
            </Row>
          )}

          {currentStep === 2 && (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <CheckCircleOutlined style={{ fontSize: '64px', color: '#52c41a', marginBottom: '24px' }} />
              <Title level={3} style={{ color: '#52c41a' }}>确认创建任务</Title>
              <Paragraph style={{ color: '#666', marginBottom: '32px' }}>
                请确认任务信息无误，点击"开始分析"按钮启动评论采集和情感分析流程
              </Paragraph>
            </div>
          )}

          <div style={{ textAlign: 'center', marginTop: '32px' }}>
            {currentStep > 0 && (
              <Button 
                style={{ marginRight: '16px' }}
                onClick={() => setCurrentStep(currentStep - 1)}
              >
                上一步
              </Button>
            )}
            
            {currentStep < steps.length - 1 ? (
              <Button 
                type="primary"
                onClick={() => setCurrentStep(currentStep + 1)}
              >
                下一步
              </Button>
            ) : (
              <Button 
                type="primary" 
                htmlType="submit"
                loading={loading}
                icon={<CheckCircleOutlined />}
              >
                开始分析
              </Button>
            )}
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default TaskPage
