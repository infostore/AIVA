'use client';

import { stockService } from '@/services/api';
import Link from 'next/link';
import { useEffect, useState } from 'react';

interface Stock {
  id: string;
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
}

export default function Home() {
  const [topStocks, setTopStocks] = useState<Stock[]>([]);
  const [recentStocks, setRecentStocks] = useState<Stock[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // 인기 주식 가져오기
        const topResponse = await stockService.getTopStocks();
        setTopStocks(topResponse.data);

        // 최근 조회한 주식 가져오기
        const recentResponse = await stockService.getRecentStocks();
        setRecentStocks(recentResponse.data);
        
        setError(null);
      } catch (err) {
        console.error('데이터 가져오기 실패:', err);
        setError('데이터를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(price);
  };

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold text-gray-900 mb-6">대시보드</h1>
        
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
            <p>{error}</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">인기 주식</h2>
                {topStocks.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            종목
                          </th>
                          <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            현재가
                          </th>
                          <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            변동
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {topStocks.map((stock) => (
                          <tr key={stock.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Link href={`/stocks/${stock.id}`} className="text-blue-600 hover:text-blue-900">
                                <div className="font-medium">{stock.name}</div>
                                <div className="text-sm text-gray-500">{stock.symbol}</div>
                              </Link>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                              {formatPrice(stock.currentPrice)}
                            </td>
                            <td className={`px-6 py-4 whitespace-nowrap text-right text-sm font-medium ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {stock.change >= 0 ? '+' : ''}{formatPrice(stock.change)} ({stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%)
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">인기 주식 데이터가 없습니다.</p>
                )}
                <div className="mt-4 text-right">
                  <Link href="/stocks" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    모든 주식 보기 →
                  </Link>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">최근 조회한 주식</h2>
                {recentStocks.length > 0 ? (
                  <div className="space-y-4">
                    {recentStocks.map((stock) => (
                      <Link 
                        key={stock.id} 
                        href={`/stocks/${stock.id}`}
                        className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <div className="font-medium text-gray-900">{stock.name}</div>
                            <div className="text-sm text-gray-500">{stock.symbol}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{formatPrice(stock.currentPrice)}</div>
                            <div className={`text-sm ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                            </div>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">최근 조회한 주식이 없습니다.</p>
                )}
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6 mt-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">시장 개요</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">코스피</h3>
                  <p className="text-2xl font-bold text-gray-900 mt-1">2,456.78</p>
                  <p className="text-sm text-green-600">+12.34 (+0.5%)</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">코스닥</h3>
                  <p className="text-2xl font-bold text-gray-900 mt-1">876.54</p>
                  <p className="text-sm text-red-600">-5.67 (-0.65%)</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500">원/달러</h3>
                  <p className="text-2xl font-bold text-gray-900 mt-1">1,345.67</p>
                  <p className="text-sm text-green-600">+2.34 (+0.17%)</p>
                </div>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
