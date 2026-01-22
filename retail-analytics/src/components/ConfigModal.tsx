import { useState } from 'react';
import { Modal, Form, Input, Button, Space, Alert, Typography, Divider } from 'antd';
import { SettingOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useData } from '../store/DataContext';
import type { FeishuConfig } from '../types';

const { Text, Link } = Typography;

interface ConfigModalProps {
  visible: boolean;
  onClose: () => void;
}

export default function ConfigModal({ visible, onClose }: ConfigModalProps) {
  const { initFeishu, fetchData, loadDemoData, isConfigured, loading } = useData();
  const [form] = Form.useForm();
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (values: FeishuConfig) => {
    setConnecting(true);
    setError(null);

    try {
      initFeishu(values);
      await fetchData();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '连接失败，请检查配置');
    } finally {
      setConnecting(false);
    }
  };

  const handleLoadDemo = () => {
    loadDemoData();
    onClose();
  };

  return (
    <Modal
      title={
        <Space>
          <SettingOutlined />
          飞书数据源配置
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={560}
    >
      <Alert
        message="配置说明"
        description={
          <div>
            <Text>请填写飞书开放平台应用凭证和多维表格信息。</Text>
            <br />
            <Link
              href="https://open.feishu.cn/document/home/introduction-to-scope-and-authorization/introduction"
              target="_blank"
            >
              <QuestionCircleOutlined /> 查看飞书开放平台文档
            </Link>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      {error && (
        <Alert
          message="连接失败"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          closable
          onClose={() => setError(null)}
        />
      )}

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          appId: localStorage.getItem('feishu_app_id') || '',
          appSecret: localStorage.getItem('feishu_app_secret') || '',
          appToken: localStorage.getItem('feishu_app_token') || '',
          tableId: localStorage.getItem('feishu_table_id') || '',
        }}
      >
        <Form.Item
          label="App ID"
          name="appId"
          rules={[{ required: true, message: '请输入 App ID' }]}
          tooltip="飞书开放平台创建的应用 App ID"
        >
          <Input placeholder="cli_xxxxxxxx" />
        </Form.Item>

        <Form.Item
          label="App Secret"
          name="appSecret"
          rules={[{ required: true, message: '请输入 App Secret' }]}
          tooltip="飞书应用的 App Secret"
        >
          <Input.Password placeholder="请输入 App Secret" />
        </Form.Item>

        <Form.Item
          label="多维表格 App Token"
          name="appToken"
          rules={[{ required: true, message: '请输入多维表格 App Token' }]}
          tooltip="从多维表格 URL 中获取，格式如 bascnxxxxxxxx"
        >
          <Input placeholder="bascnxxxxxxxx" />
        </Form.Item>

        <Form.Item
          label="数据表 Table ID"
          name="tableId"
          rules={[{ required: true, message: '请输入数据表 Table ID' }]}
          tooltip="从多维表格 URL 中获取，格式如 tblxxxxxxxx"
        >
          <Input placeholder="tblxxxxxxxx" />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0 }}>
          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            <Button onClick={onClose}>取消</Button>
            <Button
              type="primary"
              htmlType="submit"
              loading={connecting || loading}
            >
              连接并获取数据
            </Button>
          </Space>
        </Form.Item>
      </Form>

      <Divider>或者</Divider>

      <div style={{ textAlign: 'center' }}>
        <Button onClick={handleLoadDemo} disabled={isConfigured}>
          加载演示数据
        </Button>
        <div style={{ marginTop: 8 }}>
          <Text type="secondary">使用模拟数据体验系统功能</Text>
        </div>
      </div>
    </Modal>
  );
}
