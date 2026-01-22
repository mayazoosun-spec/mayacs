import { useMemo, useState } from 'react';
import { Card, Radio, Table, Empty, Row, Col } from 'antd';
import ReactECharts from 'echarts-for-react';
import { useData } from '../store/DataContext';
import { calculateProductRanking, calculateCategoryAnalysis, formatCurrency } from '../utils/analytics';
import type { ColumnsType } from 'antd/es/table';
import type { ProductRanking } from '../types';

type ViewMode = 'chart' | 'table';
type SortBy = 'sales' | 'quantity';

export default function ProductRankingChart() {
  const { filteredRecords } = useData();
  const [viewMode, setViewMode] = useState<ViewMode>('chart');
  const [sortBy, setSortBy] = useState<SortBy>('sales');

  const productRanking = useMemo(() => {
    return calculateProductRanking(filteredRecords, sortBy, 10);
  }, [filteredRecords, sortBy]);

  const categoryAnalysis = useMemo(() => {
    return calculateCategoryAnalysis(filteredRecords);
  }, [filteredRecords]);

  const barChartOption = useMemo(() => {
    const data = [...productRanking].reverse();
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        formatter: (params: unknown[]) => {
          const p = params as { name: string; value: number; seriesName: string }[];
          const item = productRanking.find((d) => d.productName === p[0].name);
          return `
            <div style="font-weight:600">${p[0].name}</div>
            <div>销售额: ${formatCurrency(item?.totalSales || 0)}</div>
            <div>销量: ${item?.totalQuantity.toLocaleString() || 0}</div>
            <div>订单数: ${item?.orderCount.toLocaleString() || 0}</div>
          `;
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        axisLabel: {
          formatter: (value: number) => {
            if (sortBy === 'sales') {
              return value >= 10000 ? `${(value / 10000).toFixed(0)}万` : value.toString();
            }
            return value.toString();
          },
        },
      },
      yAxis: {
        type: 'category',
        data: data.map((d) => d.productName),
        axisLabel: {
          width: 100,
          overflow: 'truncate',
        },
      },
      series: [
        {
          type: 'bar',
          data: data.map((d) => sortBy === 'sales' ? d.totalSales : d.totalQuantity),
          itemStyle: {
            borderRadius: [0, 4, 4, 0],
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: '#1890ff' },
                { offset: 1, color: '#69c0ff' },
              ],
            },
          },
          label: {
            show: true,
            position: 'right',
            formatter: (params: { value: number }) => {
              if (sortBy === 'sales') {
                return formatCurrency(params.value);
              }
              return params.value.toLocaleString();
            },
          },
        },
      ],
    };
  }, [productRanking, sortBy]);

  const pieChartOption = useMemo(() => {
    return {
      tooltip: {
        trigger: 'item',
        formatter: (params: { name: string; value: number; percent: number }) => {
          return `${params.name}<br/>销售额: ${formatCurrency(params.value)}<br/>占比: ${params.percent.toFixed(1)}%`;
        },
      },
      legend: {
        orient: 'vertical',
        right: '5%',
        top: 'center',
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['35%', '50%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2,
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold',
            },
          },
          data: categoryAnalysis.map((d) => ({
            name: d.category,
            value: d.totalSales,
          })),
        },
      ],
    };
  }, [categoryAnalysis]);

  const tableColumns: ColumnsType<ProductRanking> = [
    {
      title: '排名',
      key: 'rank',
      width: 60,
      render: (_, __, index) => (
        <span
          style={{
            display: 'inline-block',
            width: 24,
            height: 24,
            lineHeight: '24px',
            textAlign: 'center',
            borderRadius: '50%',
            background: index < 3 ? ['#ffd700', '#c0c0c0', '#cd7f32'][index] : '#f0f0f0',
            color: index < 3 ? '#fff' : '#666',
            fontWeight: 600,
          }}
        >
          {index + 1}
        </span>
      ),
    },
    {
      title: '商品名称',
      dataIndex: 'productName',
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      width: 100,
    },
    {
      title: '销售额',
      dataIndex: 'totalSales',
      width: 120,
      render: (value) => formatCurrency(value),
      sorter: (a, b) => a.totalSales - b.totalSales,
    },
    {
      title: '销量',
      dataIndex: 'totalQuantity',
      width: 80,
      render: (value) => value.toLocaleString(),
      sorter: (a, b) => a.totalQuantity - b.totalQuantity,
    },
    {
      title: '订单数',
      dataIndex: 'orderCount',
      width: 80,
      render: (value) => value.toLocaleString(),
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={14}>
        <Card
          title="商品销售排行 TOP10"
          extra={
            <div style={{ display: 'flex', gap: 8 }}>
              <Radio.Group
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                size="small"
              >
                <Radio.Button value="sales">按金额</Radio.Button>
                <Radio.Button value="quantity">按销量</Radio.Button>
              </Radio.Group>
              <Radio.Group
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value)}
                size="small"
              >
                <Radio.Button value="chart">图表</Radio.Button>
                <Radio.Button value="table">表格</Radio.Button>
              </Radio.Group>
            </div>
          }
          style={{ borderRadius: 8 }}
        >
          {productRanking.length > 0 ? (
            viewMode === 'chart' ? (
              <ReactECharts option={barChartOption} style={{ height: 400 }} />
            ) : (
              <Table
                dataSource={productRanking}
                columns={tableColumns}
                rowKey="productId"
                pagination={false}
                size="small"
                scroll={{ y: 360 }}
              />
            )
          ) : (
            <Empty description="暂无数据" style={{ height: 400, display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
          )}
        </Card>
      </Col>
      <Col xs={24} lg={10}>
        <Card title="品类销售占比" style={{ borderRadius: 8 }}>
          {categoryAnalysis.length > 0 ? (
            <ReactECharts option={pieChartOption} style={{ height: 400 }} />
          ) : (
            <Empty description="暂无数据" style={{ height: 400, display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
          )}
        </Card>
      </Col>
    </Row>
  );
}
