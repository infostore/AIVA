'use client';

import StockChart from '@/components/charts/StockChart';
import { analysisService, stockService } from '@/services/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Stock {
  id: string;
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  marketCap: number;
  volume: number;
  high52Week: number;
  low52Week: number;
  description: string;
}

interface StockHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface Analysis {
  stockId: string;
  recommendation: string;
  targetPrice: number;
  riskLevel: string;
  technicalIndicators: {
    rsi: number;
    macd: number;
    movingAverage50: number;
    movingAverage200: number;
  };
  fundamentalMetrics: {
    pe: number;
    eps: number;
    dividendYield: number;
    bookValue: number;
  };
}

export default function StockDetail() {
  const { id } = useParams();
  const [stock, setStock] = useState<Stock | null>(null);
  const [history, setHistory] = useState<StockHistory[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartPeriod, setChartPeriod] = useState<'1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all'>('1m');

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const [stockData, historyData, analysisData] = await Promise.all([
          stockService.getStockById(id as string),
          stockService.getStockHistory(id as string, { period: chartPeriod }),
          analysisService.getAnalysis(id as string)
        ]);
        
        setStock(stockData);
        setHistory(historyData);
        setAnalysis(analysisData);
        setError(null);
      } catch (err: any) {
        setError(err.message || '데이터를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, chartPeriod]);

  const handlePeriodChange = (period: '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all') => {
    setChartPeriod(period);
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline">
          ← 대시보드로 돌아가기
        </Link>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      ) : stock ? (
        <div className="space-y-8">
          {/* 주식 기본 정보 */}
          <div className="card">
            <div className="flex flex-col md:flex-row md:justify-between md:items-center">
              <div>
                <h1 className="text-3xl font-bold mb-1">{stock.name} ({stock.symbol})</h1>
                <div className="flex items-center">
                  <span className="text-2xl font-semibold">{stock.currentPrice.toLocaleString()} 원</span>
                  <span className={`ml-3 ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change.toLocaleString()} 
                    ({stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>
              
              {analysis && (
                <div className="mt-4 md:mt-0 p-3 rounded-lg bg-gray-50 border">
                  <div className="text-sm text-gray-600">투자 의견</div>
                  <div className="font-semibold text-lg">{analysis.recommendation}</div>
                  <div className="text-sm">
                    목표가: <span className="font-medium">{analysis.targetPrice.toLocaleString()} 원</span>
                  </div>
                </div>
              )}
            </div>
            
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">시가총액</div>
                <div className="font-medium">{stock.marketCap.toLocaleString()} 원</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">거래량</div>
                <div className="font-medium">{stock.volume.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">52주 최고</div>
                <div className="font-medium">{stock.high52Week.toLocaleString()} 원</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">52주 최저</div>
                <div className="font-medium">{stock.low52Week.toLocaleString()} 원</div>
              </div>
            </div>
            
            {stock.description && (
              <div className="mt-6">
                <h3 className="text-lg font-medium mb-2">기업 정보</h3>
                <p className="text-gray-700">{stock.description}</p>
              </div>
            )}
          </div>
          
          {/* 주가 차트 */}
          {history.length > 0 && (
            <div className="card">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
                <h2 className="text-xl font-semibold">주가 차트</h2>
                <div className="flex space-x-2 mt-2 sm:mt-0">
                  <button
                    onClick={() => handlePeriodChange('1d')}
                    className={`px-3 py-1 text-sm rounded-md ${
                      chartPeriod === '1d'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    1일
                  </button>
                  <button
                    onClick={() => handlePeriodChange('1w')}
                    className={`px-3 py-1 text-sm rounded-md ${
                      chartPeriod === '1w'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    1주
                  </button>
                  <button
                    onClick={() => handlePeriodChange('1m')}
                    className={`px-3 py-1 text-sm rounded-md ${
                      chartPeriod === '1m'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    1개월
                  </button>
                  <button
                    onClick={() => handlePeriodChange('3m')}
                    className={`px-3 py-1 text-sm rounded-md ${
                      chartPeriod === '3m'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    3개월
                  </button>
                  <button
                    onClick={() => handlePeriodChange('6m')}
                    className={`px-3 py-1 text-sm rounded-md ${
                      chartPeriod === '6m'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    6개월
                  </button>
                  <button
                    onClick={() => handlePeriodChange('1y')}
                    className={`px-3 py-1 text-sm rounded-md ${
                      chartPeriod === '1y'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    1년
                  </button>
                </div>
              </div>
              <StockChart data={history} period={chartPeriod} height={400} />
            </div>
          )}
          
          {/* 기술적 지표 */}
          {analysis && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">투자 분석</h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div>
                  <h3 className="text-sm text-gray-600 mb-1">기술적 지표</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>RSI</span>
                      <span className="font-medium">{analysis.technicalIndicators.rsi.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>MACD</span>
                      <span className="font-medium">{analysis.technicalIndicators.macd.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>MA(50)</span>
                      <span className="font-medium">{analysis.technicalIndicators.movingAverage50.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>MA(200)</span>
                      <span className="font-medium">{analysis.technicalIndicators.movingAverage200.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm text-gray-600 mb-1">기본 지표</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>P/E</span>
                      <span className="font-medium">{analysis.fundamentalMetrics.pe.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>EPS</span>
                      <span className="font-medium">{analysis.fundamentalMetrics.eps.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>배당수익률</span>
                      <span className="font-medium">{analysis.fundamentalMetrics.dividendYield.toFixed(2)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>장부가</span>
                      <span className="font-medium">{analysis.fundamentalMetrics.bookValue.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                
                <div className="col-span-2">
                  <h3 className="text-sm text-gray-600 mb-1">위험 수준</h3>
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${
                          analysis.riskLevel === 'Low' ? 'bg-green-500 w-1/3' : 
                          analysis.riskLevel === 'Medium' ? 'bg-yellow-500 w-2/3' : 
                          'bg-red-500 w-full'
                        }`}
                      ></div>
                    </div>
                    <div className="flex justify-between mt-1 text-xs text-gray-600">
                      <span>낮음</span>
                      <span>중간</span>
                      <span>높음</span>
                    </div>
                    <p className="mt-2 text-sm">
                      이 주식은 <span className="font-medium">
                        {analysis.riskLevel === 'Low' ? '낮은' : 
                         analysis.riskLevel === 'Medium' ? '중간' : '높은'} 위험
                      </span> 수준으로 평가됩니다.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* 거래 내역 */}
          {history.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">최근 거래 내역</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">날짜</th>
                      <th className="text-right py-2">시가</th>
                      <th className="text-right py-2">고가</th>
                      <th className="text-right py-2">저가</th>
                      <th className="text-right py-2">종가</th>
                      <th className="text-right py-2">거래량</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.slice(0, 10).map((item, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="py-2">{item.date}</td>
                        <td className="text-right py-2">{item.open.toLocaleString()}</td>
                        <td className="text-right py-2">{item.high.toLocaleString()}</td>
                        <td className="text-right py-2">{item.low.toLocaleString()}</td>
                        <td className="text-right py-2">{item.close.toLocaleString()}</td>
                        <td className="text-right py-2">{item.volume.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="card">
          <p>주식 정보를 찾을 수 없습니다.</p>
        </div>
      )}
    </main>
  );
} 