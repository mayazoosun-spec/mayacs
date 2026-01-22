import { Card, Row, Col } from 'antd';
import {
  ShoppingCartOutlined,
  DollarOutlined,
  UserOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { useMemo } from 'react';
import { useData } from '../store/DataContext';
import { calculateDashboardSummary, formatCurrency } from '../utils/analytics';
import dayjs from 'dayjs';

export default function SummaryCards() {
  const { filteredRecords, records, dateRange } = useData();

  const summary = useMemo(() => {
    // 计算上一周期的数据用于对比
    const days = dayjs(dateRange.end).diff(dayjs(dateRange.start), 'day');
    const prevStart = dayjs(dateRange.start).subtract(days, 'day');
    const prevEnd = dayjs(dateRange.start).subtract(1, 'day');

    const previousRecords = records.filter((r) => {
      const date = dayjs(r.orderDate);
      return date.isAfter(prevStart.subtract(1, 'day')) && date.isBefore(prevEnd.add(1, 'day'));
    });

    return calculateDashboardSummary(filteredRecords, previousRecords);
  }, [filteredRecords, records, dateRange]);

  const cards = [
    {
      title: '总销售额',
      value: formatCurrency(summary.totalSales),
      growth: summary.salesGrowth,
      icon: <DollarOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
      color: '#e6f7ff',
    },
    {
      title: '订单数',
      value: summary.totalOrders,
      growth: summary.orderGrowth,
      icon: <ShoppingCartOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
      color: '#f6ffed',
    },
    {
      title: '客户数',
      value: summary.totalCustomers,
      growth: summary.customerGrowth,
      icon: <UserOutlined style={{ fontSize: 24, color: '#722ed1' }} />,
      color: '#f9f0ff',
    },
    {
      title: '客单价',
      value: formatCurrency(summary.avgOrderValue),
      growth: null,
      icon: <RiseOutlined style={{ fontSize: 24, color: '#fa8c16' }} />,
      color: '#fff7e6',
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      {cards.map((card, index) => (
        <Col xs={24} sm={12} lg={6} key={index}>
          <Card
            style={{ background: card.color, borderRadius: 8 }}
            bodyStyle={{ padding: 16 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ color: '#666', fontSize: 14, marginBottom: 8 }}>
                  {card.title}
                </div>
                <div style={{ fontSize: 24, fontWeight: 600 }}>
                  {card.value}
                </div>
                {card.growth !== null && (
                  <div
                    style={{
                      marginTop: 8,
                      fontSize: 12,
                      color: card.growth >= 0 ? '#52c41a' : '#ff4d4f',
                    }}
                  >
                    {card.growth >= 0 ? '+' : ''}{card.growth.toFixed(2)}% 较上周期
                  </div>
                )}
              </div>
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  background: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {card.icon}
              </div>
            </div>
          </Card>
        </Col>
      ))}
    </Row>
  );
}
