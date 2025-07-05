"use client";
import { FC } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface PredictionChartProps {
  prediction: number[];
}

const statLabels = [
  "PTS", "REB", "AST", "STL", "BLK", "TO", "FG%", "3PM", "FT%", "MIN"
];

const PredictionChart: FC<PredictionChartProps> = ({ prediction }) => {
  const data = prediction.map((value, idx) => ({
    stat: statLabels[idx] || `Stat ${idx + 1}`,
    value,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="stat" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="value" fill="#2563eb" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default PredictionChart; 