import { useState, useEffect } from 'react';
import {
  Layout,
  DatePicker,
  Button,
  Space,
  Typography,
  Spin,
  Empty,
  ConfigProvider,
} from 'antd';
import {
  SettingOutlined,
  ReloadOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import zhCN from 'antd/locale/zh_CN';
import 'dayjs/locale/zh-cn';

import { DataProvider, useData } from './store/DataContext';
import {
  SummaryCards,
  SalesTrendChart,
  ProductRankingChart,
  CustomerAnalysisChart,
  ConfigModal,
} from './components';
import './App.css';

dayjs.locale('zh-cn');

const { Header, Content } = Layout;
const { RangePicker } = DatePicker;
const { Title } = Typography;

function Dashboard() {
  const {
    filteredRecords,
    loading,
    error,
    isConfigured,
    dateRange,
    setDateRange,
    fetchData,
  } = useData();

  const [configModalVisible, setConfigModalVisible] = useState(false);

  // 首次加载时如果未配置，显示配置弹窗
  useEffect(() => {
    if (!isConfigured) {
      setConfigModalVisible(true);
    }
  }, [isConfigured]);

  const handleDateRangeChange = (
    dates: [dayjs.Dayjs | null, dayjs.Dayjs | null] | null
  ) => {
    if (dates && dates[0] && dates[1]) {
      setDateRange({
        start: dates[0].format('YYYY-MM-DD'),
        end: dates[1].format('YYYY-MM-DD'),
      });
    }
  };

  const handleRefresh = async () => {
    if (isConfigured) {
      await fetchData();
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header
        style={{
          background: 'linear-gradient(90deg, #1890ff 0%, #722ed1 100%)',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <BarChartOutlined style={{ fontSize: 28, color: '#fff' }} />
          <Title level={4} style={{ margin: 0, color: '#fff' }}>
            零售数据分析平台
          </Title>
        </div>

        <Space>
          <RangePicker
            value={[dayjs(dateRange.start), dayjs(dateRange.end)]}
            onChange={handleDateRangeChange}
            allowClear={false}
            style={{ width: 260 }}
            presets={[
              { label: '最近7天', value: [dayjs().subtract(7, 'd'), dayjs()] },
              { label: '最近30天', value: [dayjs().subtract(30, 'd'), dayjs()] },
              { label: '最近90天', value: [dayjs().subtract(90, 'd'), dayjs()] },
              { label: '本月', value: [dayjs().startOf('month'), dayjs()] },
              { label: '上月', value: [dayjs().subtract(1, 'month').startOf('month'), dayjs().subtract(1, 'month').endOf('month')] },
            ]}
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            loading={loading}
          >
            刷新
          </Button>
          <Button
            icon={<SettingOutlined />}
            onClick={() => setConfigModalVisible(true)}
          >
            配置
          </Button>
        </Space>
      </Header>

      <Content style={{ padding: 24 }}>
        {loading && !filteredRecords.length ? (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: 400,
            }}
          >
            <Spin size="large" tip="加载数据中..." />
          </div>
        ) : error ? (
          <Empty
            description={error}
            style={{ marginTop: 100 }}
          >
            <Button type="primary" onClick={() => setConfigModalVisible(true)}>
              重新配置
            </Button>
          </Empty>
        ) : !isConfigured ? (
          <Empty
            description="请先配置飞书数据源或加载演示数据"
            style={{ marginTop: 100 }}
          >
            <Button type="primary" onClick={() => setConfigModalVisible(true)}>
              开始配置
            </Button>
          </Empty>
        ) : (
          <div className="dashboard-content">
            {/* 概览卡片 */}
            <section style={{ marginBottom: 24 }}>
              <SummaryCards />
            </section>

            {/* 销售趋势 */}
            <section style={{ marginBottom: 24 }}>
              <SalesTrendChart />
            </section>

            {/* 商品分析 */}
            <section style={{ marginBottom: 24 }}>
              <ProductRankingChart />
            </section>

            {/* 客户分析 */}
            <section style={{ marginBottom: 24 }}>
              <CustomerAnalysisChart />
            </section>

            {/* 页脚 */}
            <footer
              style={{
                textAlign: 'center',
                color: '#999',
                padding: '24px 0',
              }}
            >
              零售数据分析平台 | 基于飞书多维表格
            </footer>
          </div>
        )}
      </Content>

      <ConfigModal
        visible={configModalVisible}
        onClose={() => setConfigModalVisible(false)}
      />
    </Layout>
  );
}

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <DataProvider>
        <Dashboard />
      </DataProvider>
    </ConfigProvider>
  );
}

export default App;
