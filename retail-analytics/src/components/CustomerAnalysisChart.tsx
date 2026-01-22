import { useMemo } from 'react';
import { Card, Table, Row, Col, Empty, Tag } from 'antd';
import ReactECharts from 'echarts-for-react';
import { useData } from '../store/DataContext';
import { calculateCustomerAnalysis, calculateRegionAnalysis, formatCurrency } from '../utils/analytics';
import type { ColumnsType } from 'antd/es/table';
import type { CustomerAnalysis } from '../types';

export default function CustomerAnalysisChart() {
  const { filteredRecords } = useData();

  const customerAnalysis = useMemo(() => {
    return calculateCustomerAnalysis(filteredRecords).slice(0, 10);
  }, [filteredRecords]);

  const regionAnalysis = useMemo(() => {
    return calculateRegionAnalysis(filteredRecords);
  }, [filteredRecords]);

  // 客户类型分布
  const customerTypeData = useMemo(() => {
    const typeMap = new Map<string, number>();
    filteredRecords.forEach((r) => {
      const type = r.customerType || '未知';
      typeMap.set(type, (typeMap.get(type) || 0) + 1);
    });

    return Array.from(typeMap.entries()).map(([name, value]) => ({
      name,
      value,
    }));
  }, [filteredRecords]);

  const customerTypeOption = useMemo(() => {
    return {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)',
      },
      legend: {
        orient: 'horizontal',
        bottom: 0,
      },
      series: [
        {
          type: 'pie',
          radius: ['0%', '65%'],
          center: ['50%', '45%'],
          data: customerTypeData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
          label: {
            formatter: '{b}\n{d}%',
          },
          itemStyle: {
            borderRadius: 6,
            borderColor: '#fff',
            borderWidth: 2,
          },
        },
      ],
      color: ['#1890ff', '#52c41a', '#faad14', '#722ed1', '#eb2f96'],
    };
  }, [customerTypeData]);

  const regionMapOption = useMemo(() => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        formatter: (params: unknown[]) => {
          const p = params as { name: string; value: number }[];
          const region = regionAnalysis.find((r) => r.region === p[0].name);
          return `
            <div style="font-weight:600">${p[0].name}</div>
            <div>销售额: ${formatCurrency(region?.totalSales || 0)}</div>
            <div>订单数: ${region?.orderCount.toLocaleString() || 0}</div>
            <div>客户数: ${region?.customerCount.toLocaleString() || 0}</div>
          `;
        },
      },
      grid: {
        left: '3%',
        right: '10%',
        bottom: '3%',
        top: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        axisLabel: {
          formatter: (value: number) =>
            value >= 10000 ? `${(value / 10000).toFixed(0)}万` : value.toString(),
        },
      },
      yAxis: {
        type: 'category',
        data: [...regionAnalysis].reverse().map((d) => d.region),
      },
      series: [
        {
          type: 'bar',
          data: [...regionAnalysis].reverse().map((d) => d.totalSales),
          itemStyle: {
            borderRadius: [0, 4, 4, 0],
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: '#722ed1' },
                { offset: 1, color: '#b37feb' },
              ],
            },
          },
          label: {
            show: true,
            position: 'right',
            formatter: (params: { value: number }) => formatCurrency(params.value),
          },
        },
      ],
    };
  }, [regionAnalysis]);

  const tableColumns: ColumnsType<CustomerAnalysis> = [
    {
      title: '排名',
      key: 'rank',
      width: 50,
      render: (_, __, index) => (
        <span style={{ fontWeight: index < 3 ? 600 : 400 }}>
          {index + 1}
        </span>
      ),
    },
    {
      title: '客户名称',
      dataIndex: 'customerName',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'customerType',
      width: 80,
      render: (type) => {
        const colors: Record<string, string> = {
          VIP: 'gold',
          '普通': 'blue',
          '新客': 'green',
        };
        return <Tag color={colors[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '消费总额',
      dataIndex: 'totalSpent',
      width: 120,
      render: (value) => formatCurrency(value),
      sorter: (a, b) => a.totalSpent - b.totalSpent,
    },
    {
      title: '订单数',
      dataIndex: 'totalOrders',
      width: 70,
      render: (value) => value.toLocaleString(),
    },
    {
      title: '客单价',
      dataIndex: 'avgOrderValue',
      width: 100,
      render: (value) => formatCurrency(value),
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={8}>
        <Card title="客户类型分布" style={{ borderRadius: 8 }}>
          {customerTypeData.length > 0 ? (
            <ReactECharts option={customerTypeOption} style={{ height: 300 }} />
          ) : (
            <Empty description="暂无数据" style={{ height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
          )}
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        <Card title="地区销售分布" style={{ borderRadius: 8 }}>
          {regionAnalysis.length > 0 ? (
            <ReactECharts option={regionMapOption} style={{ height: 300 }} />
          ) : (
            <Empty description="暂无数据" style={{ height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
          )}
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        <Card title="高价值客户 TOP10" style={{ borderRadius: 8 }}>
          {customerAnalysis.length > 0 ? (
            <Table
              dataSource={customerAnalysis}
              columns={tableColumns}
              rowKey="customerId"
              pagination={false}
              size="small"
              scroll={{ y: 260 }}
            />
          ) : (
            <Empty description="暂无数据" style={{ height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
          )}
        </Card>
      </Col>
    </Row>
  );
}
