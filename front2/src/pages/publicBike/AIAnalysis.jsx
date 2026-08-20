import { useEffect, useState } from "react";
import AreaChartCard from "../../components/charts/AreaChartCard";
import BarChartCard from "../../components/charts/BarChartCard";
import InsightCard from "../../components/cards/InsightCard";
import Loading from "../../components/common/Loading";
import EmptyState from "../../components/common/EmptyState";
import publicBikeService from "../../services/publicBikeService";

export default function AIAnalysis() {
  const [data, setData] = useState(null);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    publicBikeService
      .getAnalysis()
      .then(setData)
      .catch((err) => {
        console.error("AI 분석 데이터 로드 실패:", err.response?.status, err.response?.data);
        setLoadError("분석 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.");
      });
  }, []);

  if (loadError) {
    return (
      <div className="py-24">
        <EmptyState title="문제가 발생했습니다" description={loadError} />
      </div>
    );
  }

  if (!data) return <Loading />;

  return (
    <div>
      <p className="mb-1 text-sm font-semibold text-bike">연간 트렌드</p>
      <h2 className="mb-6 text-2xl font-extrabold text-white">월별 이용 추이</h2>
      <AreaChartCard
        data={data.monthlyUsage}
        xKey="month"
        yKey="count"
        color="#38BDF8"
        yTickFormatter={(v) => `${Math.round(v / 10000)}만`}
        height={300}
      />

      <div className="mt-10 grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div>
          <p className="mb-1 text-sm font-semibold text-bike">대여소 순위</p>
          <h2 className="mb-4 text-2xl font-extrabold text-white">인기 대여소 TOP 6</h2>
          <BarChartCard data={data.topStations} xKey="name" yKey="count" layout="horizontal" color="#1E3A4F" highlightColor="#38BDF8" />
        </div>
        <div>
          <p className="mb-1 text-sm font-semibold text-bike">이용자 분석</p>
          <h2 className="mb-4 text-2xl font-extrabold text-white">연령대별 이용 비율</h2>
          <BarChartCard data={data.ageDistribution} xKey="age" yKey="percent" color="#1E3A4F" highlightColor="#38BDF8" />
        </div>
      </div>

      <div className="mt-10">
        <p className="mb-1 text-sm font-semibold text-bike">AI 인사이트</p>
        <h2 className="mb-6 text-2xl font-extrabold text-white">핵심 분석 결과</h2>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {data.insights.map((insight) => (
            <InsightCard key={insight.title} {...insight} />
          ))}
        </div>
      </div>

      <p className="mt-8 text-center text-xs text-gray-600">
        본 분석은 서울 열린데이터 광장 공공자전거 이용 정보를 기반으로 재구성한 데이터입니다.
      </p>
    </div>
  );
}
