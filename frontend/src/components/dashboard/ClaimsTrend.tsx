import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card } from "../ui/Card";
import { formatCurrency, formatMonth } from "../../lib/formatters";

export interface MonthlyTrendPoint {
  month_date: string;
  total_claims: number;
  total_billed: number;
  total_paid: number;
}

export function ClaimsTrend({ data }: { data: MonthlyTrendPoint[] }) {
  return (
    <Card title="Billed vs. Paid — Monthly Trend">
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 0 }}>
            <defs>
              <linearGradient id="billed" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3a4757" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#3a4757" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="paid" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1b2330" />
            <XAxis dataKey="month_date" tickFormatter={formatMonth} stroke="#64748b" fontSize={11} />
            <YAxis tickFormatter={(v) => formatCurrency(v)} stroke="#64748b" fontSize={11} width={70} />
            <Tooltip
              contentStyle={{ background: "#0f141d", border: "1px solid #28323f", borderRadius: 8, fontSize: 12 }}
              labelFormatter={(v) => formatMonth(v as string)}
              formatter={(value: number, name: string) => [formatCurrency(value), name === "total_billed" ? "Billed" : "Paid"]}
            />
            <Area type="monotone" dataKey="total_billed" stroke="#3a4757" fill="url(#billed)" strokeWidth={2} />
            <Area type="monotone" dataKey="total_paid" stroke="#2dd4bf" fill="url(#paid)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
